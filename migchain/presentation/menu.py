"""Key-driven terminal menu."""

import sys
from dataclasses import dataclass
from select import select as _fd_select
from typing import Optional, Sequence

try:
    import termios
    import tty

    _HAS_TTY = True
except ImportError:  # pragma: no cover
    _HAS_TTY = False

# ::::: ANSI :::::
_RESET = "\033[0m"
_CYAN = "\033[36m"
_DIM = "\033[2m"
_BOLD = "\033[1m"


# ::::: Models :::::
@dataclass(frozen=True)
class MenuItem:
    """Single menu choice with keyboard shortcut.

    Use {x} in label to mark the hotkey character.
    """

    key: str
    label: str
    value: str


@dataclass(frozen=True)
class MenuGroup:
    """Named group of related menu items."""

    title: str
    items: tuple[MenuItem, ...]


# ::::: Menu registries :::::
OPERATION_MENU: tuple[MenuGroup, ...] = (
    MenuGroup(
        "Migrations",
        (
            MenuItem("a", "{a}pply pending", "apply"),
            MenuItem("n", "{n}ew migration", "new"),
        ),
    ),
    MenuGroup(
        "Rollback",
        (
            MenuItem("r", "{r}ollback all", "rollback"),
            MenuItem("o", "rollback {o}ne (safest leaf)", "rollback-one"),
            MenuItem("l", "rollback {l}atest batch", "rollback-latest"),
        ),
    ),
    MenuGroup(
        "Tools",
        (
            MenuItem("R", "full {R}eload (rollback → apply)", "reload"),
            MenuItem("O", "{O}ptimize dependencies", "optimize"),
        ),
    ),
)

ENVIRONMENT_MENU: tuple[MenuGroup, ...] = (
    MenuGroup(
        "",
        (
            MenuItem("p", "{p}roduction", "production"),
            MenuItem("t", "{t}esting (single DB)", "testing"),
            MenuItem("g", "testing with {g}ateway DBs", "testing-gw"),
        ),
    ),
)


# ::::: Rendering :::::
def _render_label(item: MenuItem) -> str:
    """Replace {key} marker with ANSI-highlighted character."""
    return item.label.replace(
        f"{{{item.key}}}",
        f"{_CYAN}{item.key}{_RESET}",
    )


def _read_key() -> str:
    """Read a single keypress, consuming escape sequences."""
    if not _HAS_TTY:  # pragma: no cover
        return ""
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            while _fd_select([sys.stdin], [], [], 0.05)[0]:
                sys.stdin.read(1)
            return ""
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def key_menu(
    groups: Sequence[MenuGroup],
    title: str = "",
) -> Optional[str]:
    """Show key-driven menu. Returns selected value or None if no TTY."""
    if not _HAS_TTY:  # pragma: no cover
        return None
    try:
        termios.tcgetattr(sys.stdin.fileno())
    except (OSError, termios.error):  # pragma: no cover
        return None

    lines = 0

    if title:
        sys.stdout.write(f"\n{_BOLD}{title}{_RESET}\n")
        lines += 2

    key_map: dict[str, str] = {}
    for group in groups:
        if group.title:
            sys.stdout.write(f"\n{_DIM}{group.title}{_RESET}\n")
            lines += 2
        for item in group.items:
            key_map[item.key] = item.value
            sys.stdout.write(f" {_render_label(item)}\n")
            lines += 1

    sys.stdout.write(f"\n{_DIM}q quit{_RESET}\n")
    lines += 2
    sys.stdout.flush()

    while True:
        pressed = _read_key()
        if pressed in key_map:
            sys.stdout.write(f"\033[{lines}A\033[J")
            sys.stdout.flush()
            return key_map[pressed]
        if pressed == "\x03":
            sys.stdout.write(f"\033[{lines}A\033[J")
            sys.stdout.flush()
            raise KeyboardInterrupt
        if pressed == "q":
            sys.stdout.write(f"\033[{lines}A\033[J")
            sys.stdout.flush()
            raise SystemExit(0)
