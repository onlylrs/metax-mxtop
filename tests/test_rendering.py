from mxtop.models import DeviceSnapshot, FrameSnapshot, ProcessSnapshot
from mxtop.formatting import format_bar
from mxtop.rendering import render_once


def test_render_once_includes_gpu_and_process_rows():
    frame = FrameSnapshot(
        devices=[
            DeviceSnapshot(
                index=0,
                name="MXC500",
                bdf="0000:08:00.0",
                temperature_c=45,
                power_w=159,
                gpu_util_percent=71,
                memory_used_bytes=56 * 1024**3,
                memory_total_bytes=64 * 1024**3,
            )
        ],
        processes=[
            ProcessSnapshot(
                gpu_index=0,
                pid=967305,
                name="python",
                gpu_memory_bytes=53978 * 1024**2,
                user="alice",
                command="python train.py",
            )
        ],
    )

    output = render_once(frame, use_color=False)

    assert "MXTOP" in output
    assert "MXC500" in output
    assert "0000:08:00.0" in output
    assert "71%" in output
    assert "python train.py" in output
    assert "53978MiB" in output


def test_render_once_includes_process_runtime():
    frame = FrameSnapshot(
        devices=[],
        processes=[
            ProcessSnapshot(
                gpu_index=0,
                pid=967305,
                gpu_memory_bytes=53978 * 1024**2,
                runtime_seconds=3723,
                command="python train.py",
            )
        ],
    )

    output = render_once(frame, use_color=False)

    assert "TIME" in output
    assert "1:02:03" in output


def test_format_bar_clamps_and_fills_blocks():
    assert format_bar(50, width=10) == "█████░░░░░"
    assert format_bar(120, width=4) == "████"
    assert format_bar(None, width=3) == "???"


def test_render_once_shows_bars_on_wide_layout():
    frame = FrameSnapshot(
        devices=[DeviceSnapshot(index=0, name="MXC500", gpu_util_percent=71, memory_util_percent=83)],
        processes=[],
    )

    output = render_once(frame, width=140, use_color=False)

    assert "UTIL" in output
    assert "[████" in output
    assert "MEM" in output


def test_render_once_hides_bars_on_narrow_layout():
    frame = FrameSnapshot(
        devices=[DeviceSnapshot(index=0, name="MXC500", gpu_util_percent=71, memory_util_percent=83)],
        processes=[],
    )

    output = render_once(frame, width=90, use_color=False)

    assert "GPU%" in output
    assert "[" not in output
    assert "█" not in output


def test_render_once_orders_processes_by_gpu_id_before_memory():
    frame = FrameSnapshot(
        devices=[],
        processes=[
            ProcessSnapshot(gpu_index=2, pid=20, gpu_memory_bytes=900 * 1024**2, command="gpu2-large"),
            ProcessSnapshot(gpu_index=0, pid=10, gpu_memory_bytes=100 * 1024**2, command="gpu0-small"),
            ProcessSnapshot(gpu_index=0, pid=11, gpu_memory_bytes=200 * 1024**2, command="gpu0-large"),
            ProcessSnapshot(gpu_index=1, pid=12, gpu_memory_bytes=300 * 1024**2, command="gpu1-mid"),
        ],
    )

    output = render_once(frame, width=120, use_color=False)

    assert output.index("gpu0-large") < output.index("gpu0-small")
    assert output.index("gpu0-small") < output.index("gpu1-mid")
    assert output.index("gpu1-mid") < output.index("gpu2-large")
