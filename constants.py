"""Константы для анализатора телеметрии.

Содержит категории параметров и единицы измерения.
"""

CATEGORY_RULES = [
    ("Положение и ориентация", ["attitude", "position", "heading", "roll", "pitch", "yaw", "quaternion", "orientation", "local_position", "home_position"]),
    ("Скорости",  ["velocity", "speed", "climb", "vx", "vy", "vz", "air_speed"]),
    ("Высота",    ["altitude", "baro_alt", "hagl", "dist_bottom", "height", "z_valid"]),
    ("GPS", ["gps", "gnss", "lat", "lon", "hdop", "vdop"]),
    ("Датчики (IMU)", ["accel", "gyro", "mag", "imu", "sensor_combined", "sensor_baro", "sensor_mag", "sensor_optical_flow"]),
    ("Оценка состояния(EKF)", ["estimator", "ekf"]),
    ("Батарея", ["battery", "voltage", "current_a", "discharged", "remaining"]),
    ("Двигатели / ESC", ["esc", "motor", "thrust", "torque", "actuator"]),
    ("Навигация", ["mission", "waypoint", "position_setpoint", "trajectory", "navigator", "wp"]),
    ("Управление", ["control_mode", "rates_setpoint", "attitude_setpoint", "rate_ctrl", "vehicle_status"]),
    ("Вибрация", ["vibration", "clipping", "clip_counter"]),
    ("Температура", ["temperature", "temp"]),
    ("Система", ["system_power", "cpuload", "failure_detector", "land_detected", "vehicle_constraints"]),
    ("Связь / Телеметрия", ["telemetry", "radio", "mavlink"]),
]

UNIT_RULES = [
    (".lat", "°"),
    (".lon", "°"),
    ("altitude", "м"),
    ("baro_alt", "м"),
    ("hagl", "м"),
    ("dist_bottom", "м"),
    (".x", "м"),
    (".y", "м"),
    (".z", "м"),
    ("velocity", "м/с"),
    ("speed", "м/с"),
    ("climb", "м/с"),
    ("vx", "м/с"),
    ("vy", "м/с"),
    ("vz", "м/с"),
    ("voltage", "В"),
    ("current", "А"),
    ("temperature", "°C"),
    ("rpm", "об/мин"),
    ("remaining", "%"),
    ("discharged", "мА·ч"),
    ("hdop", ""),
    ("vdop", ""),
    ("heading", "°"),
    ("roll", "°"),
    ("pitch", "°"),
    ("yaw", "°"),
    ("thrust", "Н"),
    ("pressure", "Па"),
]


def get_unit(column_name: str) -> str:
    """Динамическое определение единицы измерения по имени колонки."""
    col_lower = column_name.lower()
    for pattern, unit in UNIT_RULES:
        if pattern in col_lower:
            return unit
    return ""
