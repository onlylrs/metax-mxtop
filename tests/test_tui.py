from mxtop import tui
from mxtop.models import FrameSnapshot


class FakeScreen:
    def __init__(self):
        self.calls = []

    def addnstr(self, row, column, text, count, attr=0):
        if column >= 8 or count <= 0:
            raise RuntimeError("would be curses ERR")
        self.calls.append((row, column, text[:count], count, attr))


class FakeBackend:
    name = "fake"

    def snapshot(self):
        return FrameSnapshot(devices=[], processes=[])


def test_draw_line_does_not_write_past_current_width(monkeypatch):
    monkeypatch.setattr(tui.curses, "has_colors", lambda: False)
    screen = FakeScreen()

    tui._draw_line(screen, 5, "0    MXC500   74% [████████████] text", width=8)

    assert screen.calls


def test_run_tui_treats_keyboard_interrupt_as_clean_exit(monkeypatch):
    def raise_interrupt():
        raise KeyboardInterrupt

    monkeypatch.setattr(tui.curses, "initscr", raise_interrupt)

    assert tui.run_tui(FakeBackend(), 1.0) == 130


def test_scroll_offset_clamps_to_rendered_content():
    assert tui._clamp_scroll(5, content_lines=20, viewport_lines=10) == 5
    assert tui._clamp_scroll(50, content_lines=20, viewport_lines=10) == 10
    assert tui._clamp_scroll(-5, content_lines=20, viewport_lines=10) == 0
    assert tui._clamp_scroll(5, content_lines=8, viewport_lines=10) == 0


def test_scroll_delta_handles_mouse_wheel_constants(monkeypatch):
    monkeypatch.setattr(tui.curses, "BUTTON4_PRESSED", 0x10000, raising=False)
    monkeypatch.setattr(tui.curses, "BUTTON5_PRESSED", 0x200000, raising=False)

    assert tui._mouse_scroll_delta(0x10000) == -3
    assert tui._mouse_scroll_delta(0x200000) == 3
    assert tui._mouse_scroll_delta(0) == 0
