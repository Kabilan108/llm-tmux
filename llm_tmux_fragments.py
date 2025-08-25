import os
import subprocess

import llm


@llm.hookimpl
def register_fragment_loaders(register):
    """Fragment loader: tmux:..."""
    register('tmux', tmux_loader)


def _run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()


def active_pane() -> str:
    return _run(['tmux', 'display-message', '-p', '#{pane_id}'])


def history_limit() -> int:
    try:
        v = _run(['tmux', 'display-message', '-p', '#{history-limit}'])
        return int(v) if v.isdigit() else 3000
    except Exception:
        return 3000


def in_tmux() -> bool:
    if os.environ.get('TMUX'):
        return True
    try:
        active_pane()
        return True
    except Exception:
        return False


def list_panes() -> list[str]:
    out = _run(['tmux', 'list-panes', '-F', '#{pane_id}'])
    return [p for p in out.splitlines() if p]


def capture_pane(n: int, pid: str | None = None) -> str:
    cmd = ['tmux', 'capture-pane', '-p', '-S', f'-{n}']
    if pid:
        cmd += ['-t', pid]
    return _run(cmd)


def _wrap_pane_text(pid: str, text: str, active: bool) -> str:
    return f'<pane id="{pid}" active="{str(active).lower()}">\n{text}\n</pane>'


def _parse_argument(argument: str) -> tuple[str, int | None]:
    """
    Supported tmux fragment arguments:
      - "current[:N]" — active pane, last N lines
      - "%<pane_id>[:N]" — specific pane id, e.g., "%1:1000"
      - "all[:N]" — all panes, one fragment per pane
      - "sys" — uname -a, $SHELL, aliases

    Returns (mode, N or None). For "%<id>", mode is the literal "%<id>".
    """
    arg = (argument or '').strip().lower()
    if not arg:
        arg = 'current'
    if arg == 'sys':
        return ('sys', None)

    parts = arg.split(':', 1)
    head = parts[0]
    n: int | None = None
    if len(parts) == 2 and parts[1]:
        try:
            n = int(parts[1])
        except ValueError as ex:
            raise ValueError(f'Invalid line count in tmux fragment: {parts[1]!r}') from ex
    if head in {'current', 'all'} or head.startswith('%'):
        return (head, n)
    raise ValueError(
        f'Unsupported tmux fragment arg {argument!r}. '
        'Use one of: current[:N], %<pane_id>[:N], all[:N], sys'
    )


def _sys_fragment() -> llm.Fragment:
    try:
        sysinfo = _run(['uname', '-a'])
    except Exception:
        sysinfo = ''
    shell = os.environ.get('SHELL') or ''
    aliases = ''
    try:
        if shell:
            aliases = subprocess.check_output([shell, '-ic', 'alias'], text=True).strip()
    except Exception:
        pass
    body = (
        '<system_info>\n'
        f'<system>{sysinfo}</system>\n'
        f'<shell>{shell}</shell>\n'
        '<aliases>\n' + aliases + '\n</aliases>\n'
        '</system_info>'
    )
    return llm.Fragment(body, 'tmux:sys')


def _fragments_for_all(n: int) -> list[llm.Fragment]:
    ap = active_pane()
    frags: list[llm.Fragment] = []
    for pid in list_panes():
        txt = capture_pane(n, pid)
        src = f'tmux:{pid}:{n}'
        frags.append(llm.Fragment(_wrap_pane_text(pid, txt, active=(pid == ap)), src))
    return frags


def _fragment_for_one(target: str, n: int) -> llm.Fragment:
    ap = active_pane()
    pid = ap if target == 'current' else target
    txt = capture_pane(n, pid if target != 'current' else None)
    src = f'tmux:{"current" if target == "current" else pid}:{n}'
    return llm.Fragment(_wrap_pane_text(pid, txt, active=(pid == ap)), src)


def tmux_loader(argument: str) -> llm.Fragment | list[llm.Fragment]:
    """
    Load terminal context from tmux as one or more fragments.

    Usage:
      -f tmux:current[:N]    # active pane
      -f tmux:%1[:N]         # specific pane id
      -f tmux:all[:N]        # all panes (multiple fragments)
      -f tmux:sys            # system info fragment (uname, shell, aliases)

    N defaults to tmux #{history-limit}.
    """
    if not in_tmux():
        raise ValueError(
            'Not in a tmux session (no $TMUX and tmux not reachable). '
            'Open in tmux, or install tmux. Tip: increase history with '
            '`set -g history-limit 50000` in ~/.tmux.conf.'
        )
    mode, n = _parse_argument(argument)
    n = n or history_limit()
    if mode == 'sys':
        return _sys_fragment()
    if mode == 'all':
        return _fragments_for_all(n)
    return _fragment_for_one(mode, n)


@llm.hookimpl
def register_template_loaders(register):
    """Template loader: shassist:..."""
    register('shassist', assisstant_loader)


def assisstant_loader(name: str) -> llm.Template:
    """Shell assistant prompts"""
    name = (name or 'default').strip().lower()
    if name not in {'default', 'command'}:
        raise ValueError('Template not found: use shassist:default|command')

    default_sp = """<assistant>
You are a shell mentor. Be concise, practical, and safe.
</assistant>
<rules>
- Prefer minimal, correct commands.
- Explain briefly. Warn on destructive ops.
- When input includes terminal context (tmux fragments), analyze it first.
</rules>
<response_format>
1) For direct command questions:
   - Start with the exact command in ```bash``` (no $/# prefix)
   - One-paragraph rationale and 1–2 variations
2) When context is provided:
   - Summarize what happened
   - Propose the safest fix
</response_format>
"""

    command_sp = """<assistant>
You output only bash commands in fenced blocks. No prose.
</assistant>
<rules>
- Use ```bash``` blocks only.
- Add brief `#` comments when multiple lines are required.
- Prepend `# WARNING` for destructive ops; `# Requires sudo` when needed.
</rules>
"""

    systems = {
        'default': default_sp,
        'command': command_sp,
    }

    return llm.Template(name=f'shassist:{name}', system=systems[name])
