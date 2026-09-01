"""Менеджер интерактивных графиков на базе Plotly, встроенный в окно Tkinter.

График отрисовывается браузерным движком (pywebview), что даёт полноценные
функции Plotly: зум/панорама мышью, box-zoom, ховер, клик по легенде для
скрытия/показа линии, а также динамическое добавление/удаление нескольких
линий произвольных цветов.

Plotly.js вшивается в HTML один раз (офлайн), а обновления данных отправляются
через Plotly.react, что сохраняет текущий масштаб и панораму приложения.
"""

import json
import threading

import tkinter as tk
import webview
import plotly.graph_objects as go
import plotly.offline

from constants import get_unit


PLOTLY_JS = plotly.offline.get_plotlyjs()

BASE_HTML = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script>{PLOTLY_JS}</script>
<style>
  html, body, #plot {{ height: 100%; width: 100%; margin: 0; padding: 0; }}
</style>
</head>
<body>
<div id="plot" style="height:100%; width:100%"></div>
<script>
  var _pending = null;
  function applyFig(j) {{
    if (typeof Plotly === 'undefined') {{ _pending = j; return; }}
    var f = JSON.parse(j);
    Plotly.react('plot', f.data, f.layout,
                 {{ responsive: true, displaylogo: false }});
  }}
  document.addEventListener('DOMContentLoaded', function () {{
    if (_pending) {{ applyFig(_pending); _pending = null; }}
  }});
</script>
</body>
</html>"""

DEFAULT_COLORS = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
]


class PlotManager:
    """Менеджер интерактивного Plotly-графика, встроенного в Tkinter."""

    def __init__(self, parent_frame: tk.Widget, df, status_var=None):
        self.parent = parent_frame
        self.df = df
        self.status_var = status_var
        self.x_col = "timestamp"
        self.traces = []  # список словарей {"col": str, "color": str}
        self.window = None
        self._color_index = 0
        self._start_browser()
        # Первичная отрисовка после готовности браузера.
        try:
            self.parent.after(1200, self.refresh)
        except Exception:
            pass

    def _start_browser(self):
        """Запускает браузерный движок в отдельном потоке и грузит базовую HTML."""
        self.parent.update_idletasks()
        hwnd = self.parent.winfo_id()

        def _run():
            self.window = webview.create_window(
                "plot", html=BASE_HTML, parent=hwnd
            )
            webview.start()

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

    def next_color(self) -> str:
        """Возвращает следующий цвет из палитры по кругу."""
        color = DEFAULT_COLORS[self._color_index % len(DEFAULT_COLORS)]
        self._color_index += 1
        return color

    def set_x(self, col: str):
        """Устанавливает столбец для оси X и перерисовывает график."""
        self.x_col = col
        self.refresh()

    def add_line(self, col: str, color: str = None):
        """Добавляет линию (параметр) с указанным цветом."""
        if color is None:
            color = self.next_color()
        if not any(t["col"] == col for t in self.traces):
            self.traces.append({"col": col, "color": color})
        self.refresh()

    def remove_line(self, col: str):
        """Удаляет линию по имени параметра."""
        self.traces = [t for t in self.traces if t["col"] != col]
        self.refresh()

    def clear(self):
        """Удаляет все линии."""
        self.traces = []
        self._color_index = 0
        self.refresh()

    def build_fig(self) -> go.Figure:
        """Строит объект Figure из текущих данных и линий."""
        fig = go.Figure()
        x = self.df[self.x_col]

        for t in self.traces:
            col = t["col"]
            if col in self.df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=self.df[col],
                        mode="lines",
                        name=col,
                        line=dict(color=t["color"]),
                    )
                )

        xu = get_unit(self.x_col)
        x_title = f"{self.x_col} ({xu})" if xu else self.x_col

        fig.update_layout(
            title=f"{self.x_col} | линий: {len(self.traces)}",
            xaxis_title=x_title,
            yaxis_title="значение",
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            margin=dict(l=50, r=20, t=50, b=40),
        )
        return fig

    def refresh(self):
        """Отправляет актуальный график в браузер (с сохранением зума)."""
        if self.window is None:
            return
        try:
            fig = self.build_fig()
            self.window.evaluate_js(f"applyFig({fig.to_json()})")
            if self.status_var:
                self.status_var.set(
                    f"График обновлён: {len(self.traces)} линий"
                )
        except Exception as exc:
            if self.status_var:
                self.status_var.set(f"Ошибка обновления графика: {exc}")

    def get_figure(self) -> go.Figure:
        """Возвращает текущий Figure для экспорта."""
        return self.build_fig()

    def shutdown(self):
        """Останавливает браузерный движок."""
        try:
            webview.stop()
        except Exception:
            pass
