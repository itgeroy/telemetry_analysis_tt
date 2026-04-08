"""Модуль для загрузки и экспорта данных телеметрии."""

from pathlib import Path
from typing import Union

import pandas as pd
from matplotlib.figure import Figure


def load_telemetry_data(file_path: Union[str, Path]) -> pd.DataFrame:
    """Загружает и обрабатывает CSV файл с телеметрией UAV.

    Args:
        file_path: Путь к CSV файлу.

    Returns:
        DataFrame с загруженными данными.

    Raises:
        Exception: Если не удалось загрузить файл.
    """
    try:
        df = pd.read_csv(file_path, na_values=["--.--", "nan", "NaN", ""])

        if "Timestamp" in df.columns:
            df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

        return df

    except Exception as e:
        raise Exception(f"Ошибка загрузки данных: {e}") from e


def export_statistics_to_txt(df: pd.DataFrame, filename: Union[str, Path]) -> bool:
    """Экспортирует статистику параметров в текстовый файл.

    Args:
        df: DataFrame с данными телеметрии.
        filename: Путь для сохранения файла.

    Returns:
        True если экспорт успешен, иначе False.
    """
    try:
        numeric_columns = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
        max_param_length = max(len(str(col)) for col in df.columns)
        separator_length = max_param_length + 52 + len(str(len(df)))

        with open(filename, "w", encoding="utf-8") as f:
            f.write("СТАТИСТИКА ПАРАМЕТРОВ ТЕЛЕМЕТРИИ\n")
            f.write("=" * 32 + "\n")
            f.write(f"Всего записей: {len(df):,}\n")
            f.write(f"Анализируемых параметров: {len(numeric_columns)}\n")
            f.write("=" * separator_length + "\n\n")

            # Заголовок таблицы
            header = f"{'Параметр':<{max_param_length}} {'Мин':<10} {'Макс':<10} {'Среднее':<10} {'Разброс':<10} {'Заполнено':<12}\n"
            f.write(header)
            f.write("-" * separator_length + "\n")

            # Данные по каждому параметру
            for column in df.columns:
                if pd.api.types.is_numeric_dtype(df[column]):
                    stats_line = (
                        f"{column:<{max_param_length}} "
                        f"{df[column].min():<10.3f} "
                        f"{df[column].max():<10.3f} "
                        f"{df[column].mean():<10.3f} "
                        f"{df[column].std():<10.3f} "
                        f"{df[column].count()}/{len(df):<12}\n"
                    )
                    f.write(stats_line)

            f.write("\n" + "=" * 50 + "\n")
            f.write(f"Файл сгенерирован: {pd.Timestamp.now()}\n")

        return True

    except Exception as e:  # pylint: disable=W0718
        print(f"Ошибка экспорта статистики: {e}")
        return False


def export_plot_as_png(
    df: pd.DataFrame,
    plot_params: list,
    status_var
) -> Union[Figure, None]:
    """Создает график для экспорта.

    Args:
        df: DataFrame с данными телеметрии.
        plot_params: Список с выбранными параметрами [x_var, y_var].
        status_var: Переменная для обновления статуса.

    Returns:
        Объект Figure для сохранения или None при ошибке.
    """
    try:
        x_var = plot_params[0]
        y_var = plot_params[1]

        if not x_var or not y_var:
            status_var.set("Ошибка: не выбраны оси для графика")
            return None

        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)

        ax.plot(df[x_var], df[y_var])
        ax.set_xlabel(x_var)
        ax.set_ylabel(y_var)
        ax.set_title(f"{x_var} | {y_var}")
        ax.grid(True)

        return fig

    except Exception as e:
        status_var.set(f"Ошибка сохранения: {str(e)}")
        return None
