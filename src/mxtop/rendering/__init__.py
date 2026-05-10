from __future__ import annotations

from datetime import datetime

from mxtop.formatting import ellipsize, format_bar, format_bytes, format_duration, format_float, format_mib, format_percent
from mxtop.models import FrameSnapshot

WIDE_MIN_WIDTH = 110


def render_once(frame: FrameSnapshot, use_color: bool = True, width: int = 120) -> str:
    del use_color
    wide = width >= WIDE_MIN_WIDTH
    lines = [
        f"MXTOP {datetime.fromtimestamp(frame.timestamp).strftime('%Y-%m-%d %H:%M:%S')}  backend={frame.backend}  GPUs={len(frame.devices)}  procs={len(frame.processes)}",
        "",
    ]
    if wide:
        lines.extend(
            [
                "GPU  NAME        BDF             TEMP   POWER  UTIL                 MEM                  MEMORY",
                "---  ----------  --------------  -----  -----  -------------------  -------------------  ----------------",
            ]
        )
    else:
        lines.extend(
            [
                "GPU  NAME        BDF             TEMP   POWER  GPU%  MEM%  MEMORY",
                "---  ----------  --------------  -----  -----  ----  ----  ----------------",
            ]
        )
    for device in frame.devices:
        memory = f"{format_bytes(device.memory_used_bytes)}/{format_bytes(device.memory_total_bytes)}"
        prefix = (
            f"{device.index:<3}  {ellipsize(device.name, 10):<10}  "
            f"{ellipsize(device.bdf, 14):<14}  "
            f"{format_float(device.temperature_c, 'C'):>5}  "
            f"{format_float(device.power_w, 'W'):>5}  "
        )
        if wide:
            lines.append(
                prefix
                + f"{format_percent(device.gpu_util_percent):>4} [{format_bar(device.gpu_util_percent)}]  "
                + f"{format_percent(device.memory_util_percent):>4} [{format_bar(device.memory_util_percent)}]  "
                + memory
            )
        else:
            lines.append(
                prefix
                + f"{format_percent(device.gpu_util_percent):>4}  "
                + f"{format_percent(device.memory_util_percent):>4}  "
                + memory
            )

    lines.extend(
        [
            "",
            "GPU  PID       USER          GPU-MEM   CPU%      TIME  HOST-MEM  COMMAND",
            "---  --------  ------------  --------  ----  --------  --------  ----------------",
        ]
    )
    if frame.processes:
        sorted_processes = sorted(
            frame.processes,
            key=lambda process: (process.gpu_index, -(process.gpu_memory_bytes or 0), process.pid),
        )
        for process in sorted_processes:
            lines.append(
                f"{process.gpu_index:<3}  {process.pid:<8}  "
                f"{ellipsize(process.user, 12):<12}  "
                f"{format_mib(process.gpu_memory_bytes):>8}  "
                f"{format_percent(process.cpu_percent):>4}  "
                f"{format_duration(process.runtime_seconds):>8}  "
                f"{format_bytes(process.host_memory_bytes):>8}  "
                f"{ellipsize(process.command or process.name, max(10, width - 77))}"
            )
    else:
        lines.append("no GPU processes found")
    return "\n".join(lines)
