"""Модуль для управления графиками."""

from typing import Optional

import tkinter as tk
from tkinter import ttk

import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from constants import get_unit


class PlotManager:
    """Менеджер для управления графиками."""

    def __init__(self, parent_frame: tk.Widget, status_var: Optional[tk.StringVar] = None):
        """Инициализирует менеджер графиков.

        Args:
            parent_frame: Родительский фрейм для размещения графика.
            status_var: Переменная для отображения статуса.
        """
        self.parent_frame = parent_frame
        self.status_var = status_var
        self.current_figure: Optional[Figure] = None
        self.current_canvas: Optional[FigureCanvasTkAgg] = None

    def create_plot(self, df: pd.DataFrame, x_col: str, y_col: str) -> Optional[Figure]:
        """Создает или обновляет график.

        Args:
            df: DataFrame с данными.
            x_col: Имя столбца для оси X.
            y_col: Имя столбца для оси Y.

        Returns:
            Объект Figure или None при ошибке.
        """
        self.clear_plot()

        if not x_col or not y_col:
            return None

        try:
            self.current_figure = Figure(figsize=(10, 6))
            ax = self.current_figure.add_subplot(111)

            ax.plot(df[x_col], df[y_col])
            self._set_axis_labels(ax, x_col, y_col)
            ax.set_title(f"{x_col} | {y_col}")
            ax.grid(True)

            self.current_canvas = FigureCanvasTkAgg(self.current_figure, self.parent_frame)
            self.current_canvas.draw()
            self.current_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            if self.status_var:
                self.status_var.set(f"Создан график: {x_col} | {y_col}")

            return self.current_figure

        except Exception as e:
            self._show_error(f"Ошибка построения: {str(e)}")
            return None

    def _set_axis_labels(self, ax, x_col: str, y_col: str):
        """Устанавливает подписи осей с единицами измерения.

        Args:
            ax: Объект оси matplotlib.
            x_col: Имя столбца для оси X.
            y_col: Имя столбца для оси Y.
        """
        x_unit = get_unit(x_col)
        y_unit = get_unit(y_col)

        x_label = f"{x_col}, {x_unit}" if x_unit else x_col
        y_label = f"{y_col}, {y_unit}" if y_unit else y_col

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

    def _show_error(self, message: str):
        """Отображает сообщение об ошибке.

        Args:
            message: Текст сообщения.
        """
        error_label = ttk.Label(
            self.parent_frame,
            text=message,
            foreground="red"
        )
        error_label.pack(pady=10)

        if self.status_var:
            self.status_var.set(f"Ошибка: {message}")

    def clear_plot(self):
        """Очищает текущий график."""
        if self.current_canvas:
            self.current_canvas.get_tk_widget().destroy()
            self.current_canvas = None
        self.current_figure = None

        for widget in self.parent_frame.winfo_children():
            widget.destroy()
