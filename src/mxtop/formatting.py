from __future__ import annotations


def format_bytes(value: int | None) -> str:
    if value is None:
        return "N/A"
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    amount = float(value)
    for unit in units:
        if abs(amount) < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(amount)}B"
            if unit == "MiB":
                return f"{amount:.0f}MiB"
            return f"{amount:.1f}{unit}"
        amount /= 1024
    return f"{amount:.1f}TiB"


def format_mib(value: int | None) -> str:
    if value is None:
        return "N/A"
    return f"{value / 1024**2:.0f}MiB"


def format_percent(value: float | None) -> str:
    return "N/A" if value is None else f"{value:.0f}%"


def format_float(value: float | None, unit: str) -> str:
    return "N/A" if value is None else f"{value:.0f}{unit}"


def format_duration(value: float | None) -> str:
    if value is None:
        return "N/A"
    seconds = max(0, int(value))
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def format_bar(value: float | None, width: int = 12) -> str:
    if width <= 0:
        return ""
    if value is None:
        return "?" * width
    percent = max(0.0, min(100.0, value))
    filled = round(width * percent / 100)
    return "█" * filled + "░" * (width - filled)


def ellipsize(value: str | None, width: int) -> str:
    text = value or ""
    if len(text) <= width:
        return text
    if width <= 1:
        return text[:width]
    return text[: width - 1] + "~"
