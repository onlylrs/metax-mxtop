from __future__ import annotations

import os
import time

from mxtop.models import ProcessSnapshot

_CPU_SAMPLES: dict[tuple[int, float], tuple[float, float]] = {}
_MAX_CPU_SAMPLES = 2048


def _calculate_cpu_percent(pid: int, process_identity: float, process_cpu_seconds: float, sample_time: float) -> float | None:
    key = (pid, process_identity)
    previous = _CPU_SAMPLES.get(key)
    _CPU_SAMPLES[key] = (process_cpu_seconds, sample_time)
    if len(_CPU_SAMPLES) > _MAX_CPU_SAMPLES:
        oldest_key = min(_CPU_SAMPLES, key=lambda sample_key: _CPU_SAMPLES[sample_key][1])
        del _CPU_SAMPLES[oldest_key]
    if previous is None:
        return None

    previous_cpu_seconds, previous_sample_time = previous
    elapsed = sample_time - previous_sample_time
    if elapsed <= 0:
        return None
    return max(0.0, (process_cpu_seconds - previous_cpu_seconds) / elapsed * 100)


def enrich_processes(processes: list[ProcessSnapshot]) -> None:
    try:
        import psutil
    except ModuleNotFoundError:
        _enrich_from_proc(processes)
        return

    for process in processes:
        try:
            sample_time = time.time()
            proc = psutil.Process(process.pid)
            process.name = process.name or proc.name()
            process.user = proc.username()
            command = proc.cmdline()
            process.command = " ".join(command) if command else process.name
            cpu_times = proc.cpu_times()
            create_time = proc.create_time()
            process.cpu_percent = _calculate_cpu_percent(
                process.pid,
                create_time,
                float(cpu_times.user + cpu_times.system),
                sample_time,
            )
            process.host_memory_bytes = int(proc.memory_info().rss)
            process.runtime_seconds = max(0.0, sample_time - create_time)
        except psutil.Error:
            if not process.name:
                process.name = str(process.pid)


def _enrich_from_proc(processes: list[ProcessSnapshot]) -> None:
    boot_time = _safe_boot_time()
    clock_ticks = _safe_clock_ticks()
    for process in processes:
        comm_path = f"/proc/{process.pid}/comm"
        cmdline_path = f"/proc/{process.pid}/cmdline"
        stat_path = f"/proc/{process.pid}/stat"
        status_path = f"/proc/{process.pid}/status"
        try:
            with open(comm_path, "r", encoding="utf-8") as handle:
                process.name = process.name or handle.read().strip()
        except OSError:
            process.name = process.name or str(process.pid)

        try:
            with open(cmdline_path, "rb") as handle:
                raw = handle.read().replace(b"\x00", b" ").strip()
                process.command = raw.decode("utf-8", errors="replace") or process.name
        except OSError:
            process.command = process.name

        try:
            process.user = str(os.stat(comm_path).st_uid)
        except OSError:
            process.user = None

        try:
            with open(stat_path, "r", encoding="utf-8") as handle:
                stat = handle.read().split()
            if boot_time is None:
                continue
            process_cpu_seconds = (int(stat[13]) + int(stat[14])) / clock_ticks
            start_ticks = int(stat[21])
            create_time = boot_time + start_ticks / clock_ticks
            sample_time = time.time()
            process.cpu_percent = _calculate_cpu_percent(process.pid, float(start_ticks), process_cpu_seconds, sample_time)
            process.runtime_seconds = max(0.0, sample_time - create_time)
        except (OSError, IndexError, ValueError):
            pass

        try:
            with open(status_path, "r", encoding="utf-8") as handle:
                for line in handle:
                    if line.startswith("VmRSS:"):
                        process.host_memory_bytes = int(line.split()[1]) * 1024
                        break
        except (OSError, IndexError, ValueError):
            pass


def _read_boot_time() -> float:
    with open("/proc/uptime", "r", encoding="utf-8") as handle:
        uptime_seconds = float(handle.read().split()[0])
    return time.time() - uptime_seconds


def _safe_boot_time() -> float | None:
    try:
        return _read_boot_time()
    except (OSError, IndexError, ValueError):
        return None


def _read_clock_ticks() -> int:
    return int(os.sysconf(os.sysconf_names["SC_CLK_TCK"]))


def _safe_clock_ticks() -> int:
    try:
        return _read_clock_ticks()
    except (KeyError, OSError, ValueError):
        return 100
