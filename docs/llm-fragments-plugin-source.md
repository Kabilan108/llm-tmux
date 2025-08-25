<documents>
<document index="5">
<source>README.md</source>
<document_content>
# llm-fragments-reader

[![PyPI](https://img.shields.io/pypi/v/llm-fragments-reader.svg)](https://pypi.org/project/llm-fragments-reader/)
[![Changelog](https://img.shields.io/github/v/release/simonw/llm-fragments-reader?include_prereleases&label=changelog)](https://github.com/simonw/llm-fragments-reader/releases)
[![Tests](https://github.com/simonw/llm-fragments-reader/actions/workflows/test.yml/badge.svg)](https://github.com/simonw/llm-fragments-reader/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/llm-fragments-reader/blob/main/LICENSE)

Run URLs through the Jina Reader API

## Installation

Install this plugin in the same environment as [LLM](https://llm.datasette.io/).
```bash
llm install llm-fragments-reader
```
## Usage

Use `-f 'reader:URL` to fetch a converted Markdown document for a URL.

```bash
llm -f 'reader:https://simonwillison.net/tags/jina/' summary
```

Uses [the Jina Reader API](https://jina.ai/reader/).

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:
```bash
cd llm-fragments-reader
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
python -m pip install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```

</document_content>
</document>
<document index="6">
<source>llm_fragments_reader.py</source>
<document_content>
import httpx
import llm


@llm.hookimpl
def register_fragment_loaders(register):
    register("reader", reader_loader)


def reader_loader(argument: str) -> llm.Fragment:
    """
    Use Jina Reader to convert a URL to Markdown text.

    Example usage:
      llm -f 'reader:https://simonwillison.net/tags/jina/' ...
    """
    url = "https://r.jina.ai/" + argument
    response = httpx.get(url)
    if response.status_code != 200:
        raise ValueError(f"Failed to load fragment from {url}: {response.status_code}")
    return llm.Fragment(response.text, url)

</document_content>
</document>
<document index="7">
<source>pyproject.toml</source>
<document_content>
[project]
name = "llm-fragments-reader"
version = "0.1"
description = "Run URLs through the Jina Reader API"
readme = "README.md"
authors = [{name = "Simon Willison"}]
license = "Apache-2.0"
classifiers = []
requires-python = ">=3.9"
dependencies = [
    "llm"
]

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project.urls]
Homepage = "https://github.com/simonw/llm-fragments-reader"
Changelog = "https://github.com/simonw/llm-fragments-reader/releases"
Issues = "https://github.com/simonw/llm-fragments-reader/issues"
CI = "https://github.com/simonw/llm-fragments-reader/actions"

[project.entry-points.llm]
fragments_reader = "llm_fragments_reader"

[project.optional-dependencies]
test = ["pytest", "pytest-httpx"]

</document_content>
</document>
<document index="8">
<source>tests/test_fragments_reader.py</source>
<document_content>
from llm.plugins import pm
from llm_fragments_reader import reader_loader


def test_reader_loader(httpx_mock):
    example_text = '# Example Title\n\nExample content.'
    httpx_mock.add_response(
        url="https://r.jina.ai/https://example.com/",
        method="GET",
        text=example_text,
    )
    fragment = reader_loader("https://example.com/")
    assert str(fragment) == example_text
    assert fragment.source == "https://r.jina.ai/https://example.com/"

</document_content>
</document>
</documents>
