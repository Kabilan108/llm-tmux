import subprocess

import pytest

from llm_tmux_fragments import tmux_loader


def _patch_check_output(monkeypatch, mapping):
    def fake_check_output(cmd, text=True):
        key = tuple(cmd)
        if key in mapping:
            return mapping[key]
        raise subprocess.CalledProcessError(1, cmd, 'err')

    monkeypatch.setattr(subprocess, 'check_output', fake_check_output)


def test_not_in_tmux(monkeypatch):
    monkeypatch.delenv('TMUX', raising=False)

    def boom(cmd, text=True):
        raise subprocess.CalledProcessError(1, cmd, 'err')

    monkeypatch.setattr(subprocess, 'check_output', boom)
    with pytest.raises(ValueError):
        tmux_loader('current')


def test_current_with_default_limit(monkeypatch):
    monkeypatch.setenv('TMUX', 'yes')
    mapping = {
        tuple(['tmux', 'display-message', '-p', '#{history-limit}']): '3000',
        tuple(['tmux', 'display-message', '-p', '#{pane_id}']): '%0',
        tuple(['tmux', 'capture-pane', '-p', '-S', '-3000']): 'line1\nline2',
    }
    _patch_check_output(monkeypatch, mapping)
    frag = tmux_loader('current')
    s = str(frag)
    assert 'line1' in s and 'pane id' in s


def test_specific_pane_with_n(monkeypatch):
    monkeypatch.setenv('TMUX', 'yes')
    mapping = {
        tuple(['tmux', 'display-message', '-p', '#{history-limit}']): '3000',
        tuple(['tmux', 'display-message', '-p', '#{pane_id}']): '%1',
        tuple(['tmux', 'capture-pane', '-p', '-S', '-100']): 'hello',
    }

    def fake_check_output(cmd, text=True):
        if cmd == ['tmux', 'capture-pane', '-p', '-S', '-100', '-t', '%2']:
            return 'hello'
        key = tuple(cmd)
        return mapping[key]

    monkeypatch.setattr(subprocess, 'check_output', fake_check_output)
    frag = tmux_loader('%2:100')
    assert 'hello' in str(frag)


def test_all_panes(monkeypatch):
    monkeypatch.setenv('TMUX', 'yes')
    mapping = {
        tuple(['tmux', 'display-message', '-p', '#{history-limit}']): '2000',
        tuple(['tmux', 'display-message', '-p', '#{pane_id}']): '%1',
        tuple(['tmux', 'list-panes', '-F', '#{pane_id}']): '%1\n%2',
    }

    def fake_check_output(cmd, text=True):
        key = tuple(cmd)
        if key in mapping:
            return mapping[key]
        if cmd[:4] == ['tmux', 'capture-pane', '-p', '-S']:
            return 'X\nY'
        raise subprocess.CalledProcessError(1, cmd, 'err')

    monkeypatch.setattr(subprocess, 'check_output', fake_check_output)
    frags = tmux_loader('all:50')
    assert isinstance(frags, list) and len(frags) == 2


def test_sys(monkeypatch):
    monkeypatch.setenv('TMUX', 'yes')

    def ok(cmd, text=True):
        return '%0'

    monkeypatch.setattr(subprocess, 'check_output', ok)
    frag = tmux_loader('sys')
    assert '<system_info>' in str(frag)


def test_bad_argument(monkeypatch):
    monkeypatch.setenv('TMUX', 'yes')

    def ok(cmd, text=True):
        return '%0'

    monkeypatch.setattr(subprocess, 'check_output', ok)
    with pytest.raises(ValueError):
        tmux_loader('foo')
