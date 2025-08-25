# llm-tmux-fragments

Expose tmux scrollback to [LLM](https://llm.datasette.io/) via fragments, and ship shassist-inspired templates.

## Install
```bash
llm install llm-tmux-fragments            # from PyPI
# or, local dev:
llm install -e .
```

## Use: fragments

```bash
llm -f tmux:current:2000 "Explain the last error"
llm -f tmux:%1:500 "Summarize what happened in pane %1"
llm -f tmux:all:800 "Give me a cross-pane diagnosis"
llm -f tmux:sys -f tmux:current "Given sys+history, propose a safe fix"
```

Notes: content is limited by tmux `history-limit`; consider raising it (e.g., `set -g history-limit 50000`). ([GitHub][4], [Stack Overflow][5])

## Use: templates

```bash
llm -t shassist:default -f tmux:current "Why did this pip install fail?"
llm -t shassist:command -f tmux:%1:200 "Give only the exact fix command"
llm -t shassist:default -f tmux:all:600 "Plan the next steps across panes"
llm -t shassist:default -f tmux:current "Critique my awk, then improve it"
```

Don’t want bundled templates? DIY:

```bash
llm --system 'You are a shell mentor…' --save shassist-default
llm -t shassist-default -f tmux:current 'Explain last error'
```

(See LLM templates docs for `--save` and template usage.) ([llm.datasette.io][3])

## How it works

The plugin registers a fragment loader (`tmux:`) and a template loader (`shassist:`). The fragment loader calls `tmux capture-pane` with a default line count based on `#{history-limit}`, returning one or more fragments (one per pane for `all`). Template loader returns prompts for a shell assistant.

**Credit:** Inspired by Answer.AI’s [`shell_sage`](https://ssage.answer.ai/). ([shell_sage][6])

[1]: https://llm.datasette.io/en/stable/
[2]: https://man7.org/linux/man-pages/man1/tmux.1.html
[3]: https://llm.datasette.io/en/stable/templates.html
[4]: https://stackoverflow.com/questions/18760288/how-to-increase-scrollback-buffer-size-in-tmux
[5]: https://ssage.answer.ai/
