from __future__ import annotations

import sys
from types import SimpleNamespace

from mxtop.host import enrich_processes
from mxtop.models import ProcessSnapshot


def test_enrich_processes_calculates_cpu_percent_from_elapsed_cpu_time(monkeypatch):
    samples = iter(
        [
            SimpleNamespace(user=10.0, system=2.0),
            SimpleNamespace(user=10.5, system=2.0),
        ]
    )

    class FakeProcess:
        def __init__(self, pid: int) -> None:
            self.pid = pid

        def name(self) -> str:
            return "python"

        def username(self) -> str:
            return "alice"

        def cmdline(self) -> list[str]:
            return ["python", "train.py"]

        def memory_info(self) -> SimpleNamespace:
            return SimpleNamespace(rss=1024)

        def create_time(self) -> float:
            return 100.0

        def cpu_times(self) -> SimpleNamespace:
            return next(samples)

    fake_psutil = SimpleNamespace(Process=FakeProcess, Error=Exception)
    monkeypatch.setitem(sys.modules, "psutil", fake_psutil)
    monkeypatch.setattr("mxtop.host.time.time", lambda: 200.0)

    process = ProcessSnapshot(gpu_index=0, pid=123)
    enrich_processes([process])

    assert process.cpu_percent is None

    monkeypatch.setattr("mxtop.host.time.time", lambda: 201.0)
    enrich_processes([process])

    assert process.cpu_percent == 50.0


def test_enrich_processes_fallback_reads_proc_metrics(monkeypatch, tmp_path):
    proc = tmp_path / "proc" / "123"
    proc.mkdir(parents=True)
    (proc / "comm").write_text("python\n", encoding="utf-8")
    (proc / "cmdline").write_bytes(b"python\x00train.py\x00")
    stat_fields = ["0"] * 52
    stat_fields[13] = "1000"
    stat_fields[14] = "200"
    stat_fields[21] = "10000"
    (proc / "stat").write_text(" ".join(stat_fields), encoding="utf-8")
    (proc / "status").write_text("Name:\tpython\nVmRSS:\t2048 kB\n", encoding="utf-8")

    real_open = open
    real_stat = __import__("os").stat

    def fake_open(path, *args, **kwargs):
        if isinstance(path, str) and path.startswith("/proc/123/"):
            return real_open(str(proc / path.rsplit("/", 1)[1]), *args, **kwargs)
        return real_open(path, *args, **kwargs)

    def fake_stat(path):
        if path == "/proc/123/comm":
            return SimpleNamespace(st_uid=31965)
        return real_stat(path)

    monkeypatch.setitem(sys.modules, "psutil", None)
    monkeypatch.setattr("builtins.open", fake_open)
    monkeypatch.setattr("mxtop.host.os.stat", fake_stat)
    monkeypatch.setattr("mxtop.host._read_boot_time", lambda: 100.0)
    monkeypatch.setattr("mxtop.host._safe_clock_ticks", lambda: 100)
    monkeypatch.setattr("mxtop.host.time.time", lambda: 250.0)

    process = ProcessSnapshot(gpu_index=0, pid=123)
    enrich_processes([process])

    assert process.name == "python"
    assert process.command == "python train.py"
    assert process.user == "31965"
    assert process.runtime_seconds == 50.0
    assert process.host_memory_bytes == 2048 * 1024

    stat_fields[13] = "1050"
    (proc / "stat").write_text(" ".join(stat_fields), encoding="utf-8")
    monkeypatch.setattr("mxtop.host.time.time", lambda: 251.0)
    enrich_processes([process])

    assert process.cpu_percent == 50.0
