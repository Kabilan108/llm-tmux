<web url='https://llm.datasette.io/en/stable/fragments.html#fragments'>
Title: Fragments - LLM
Author: 
Published Date: 2025-04-06T00:00:00.000Z
URL: https://llm.datasette.io/en/stable/fragments.html…
Text: ContentsMenuExpandLight modeDark modeAuto light/dark mode

[Back to top](https://llm.datasette.io/en/stable/fragments.html)

Toggle Light / Dark / Auto color theme

Toggle table of contents sidebar

# Fragments [\#](https://llm.datasette.io/en/stable/fragments.html\#fragments)

LLM prompts can optionally be composed out of **fragments** \- reusable pieces of text that are logged just once to the database and can then be attached to multiple prompts.

These are particularly useful when you are working with long context models, which support feeding large amounts of text in as part of your prompt.

Fragments primarily exist to save space in the database, but may be used to support other features such as vendor prompt caching as well.

Fragments can be specified using several different mechanisms:

- URLs to text files online

- Paths to text files on disk

- Aliases that have been attached to a specific fragment

- Hash IDs of stored fragments, where the ID is the SHA256 hash of the fragment content

- Fragments that are provided by custom plugins - these look like `plugin-name:argument`


## Using fragments in a prompt [\#](https://llm.datasette.io/en/stable/fragments.html\#using-fragments-in-a-prompt)

Use the `-f/--fragment` option to specify one or more fragments to be used as part of your prompt:

```
llm-fhttps://llm.datasette.io/robots.txt"Explain this robots.txt file in detail"

```

Here we are specifying a fragment using a URL. The contents of that URL will be included in the prompt that is sent to the model, prepended prior to the prompt text.

The `-f` option can be used multiple times to combine together multiple fragments.

Fragments can also be files on disk, for example:

```
llm-fsetup.py'extract the metadata'

```

Use `-` to specify a fragment that is read from standard input:

```
llm-f-'extract the metadata' 
 
 docs/aliases.md 
 
(aliases)=
#...
-hash:16b686067375182573e2aa16b5bfc1e64d48350232535d06444537e51f1fd60c
aliases:[]
datetime_utc:'2025-04-0623:03:47'
source:simonw/files-to-prompt/pyproject.toml
content:|-
[project]
name = "files-to-prompt"
version = "0.6"
description = "Concatenate a directory full of...

```

Those long `hash` values are IDs that can be used to reference a fragment in the future:

```
llm-f16b686067375182573e2aa16b5bfc1e64d48350232535d06444537e51f1fd60c'Extract metadata'

```

Use `-q searchterm` one or more times to search for fragments that match a specific set of search terms.

To view the full content of a fragment use `llm fragments show`:

```
llmfragmentsshow0d6e368f9bc21f8db78c01e192ecf925841a957d8b991f5bf9f6239aa4d81815

```

## Setting aliases for fragments [\#](https://llm.datasette.io/en/stable/fragments.html\#setting-aliases-for-fragments)

You can assign aliases to fragments that you use often using the `llm fragments set` command:

```
llmfragmentssetmydocs./docs.md

```

To remove an alias, use `llm fragments remove`:

```
llmfragmentsremovemydocs

```

You can then use that alias in place of the fragment hash ID:

```
llm-fmydocs'How do I access metadata?'

```

Use `llm fragments --aliases` to see a full list of fragments that have been assigned aliases:

```
llmfragments--aliases

```

## Viewing fragments in your logs [\#](https://llm.datasette.io/en/stable/fragments.html\#viewing-fragments-in-your-logs)

The `llm logs` command lists the fragments that were used for a prompt. By default these are listed as fragment hash IDs, but you can use the `--expand` option to show the full content of each fragment.

This command will show the expanded fragments for your most recent conversation:

```
llmlogs-c--expand

```

You can filter for logs that used a specific fragment using the `-f/--fragment` option:

```
llmlogs-c-f0d6e368f9bc21f8db78c01e192ecf925841a957d8b991f5bf9f6239aa4d81815

```

This accepts URLs, file paths, aliases, and hash IDs.

Multiple `-f` options will return responses that used **all** of the specified fragments.

Fragments are returned by `llm logs --json` as well. By default these are truncated but you can add the `-e/--expand` option to show the full content of each fragment.

```
llmlogs-c--json--expand

```

## Using fragments from plugins [\#](https://llm.datasette.io/en/stable/fragments.html\#using-fragments-from-plugins)

LLM plugins can provide custom fragment loaders which do useful things.

One example is the [llm-fragments-github plugin](https://github.com/simonw/llm-fragments-github). This can convert the file from a public GitHub repository into a list of fragments, allowing you to ask questions about the full repository.

Here’s how to try that out:

```
llminstallllm-fragments-github
llm-fgithub:simonw/s3-credentials'Suggest new features for this tool'

```

This plugin turns a single call to `-f github:simonw/s3-credentials` into multiple fragments, one for every text file in the [simonw/s3-credentials](https://github.com/simonw/s3-credentials) GitHub repository.

Running `llm logs -c` will show that this prompt incorporated 26 fragments, one for each file.

Running `llm logs -c --usage --expand` includes token usage information and turns each fragment ID into a full copy of that file. [Here’s the output of that command](https://gist.github.com/simonw/c9bbbc5f6560b01f4b7882ac0194fb25).

See the [register\_fragment\_loaders() plugin hook](https://llm.datasette.io/en/stable/plugins/plugin-hooks.html#plugin-hooks-register-fragment-loaders) documentation for details on writing your own custom fragment plugin.

</web>
