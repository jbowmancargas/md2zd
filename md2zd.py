#!/usr/bin/env python3
"""Markdown processing and syntax highlighting."""
import argparse
import pathlib
import re
import typing

import cmarkgfm  # type: ignore
import pygments.formatters  # type: ignore
import pygments.lexers  # type: ignore
import tidy  # type: ignore

CODE_RE = re.compile(r"^```([a-z]+)?$(.+?)^```$", re.S | re.M)
CMARK_FLAGS = 132096  # UNSAFE = 1 << 17; SMART = 1 << 10; CMARK_FLAGS = UNSAFE | SMART
FORMATTER = pygments.formatters.HtmlFormatter(nowrap=True, noclasses=True, style="colorful")


def md_codeblock(match: typing.Match) -> str:
    """Substitution method to replace markdown code blocks with pygmented HTML.

    Should be called from substition (sub) regex method.

    Args:
        match: matched block

    Returns:
        A string containing the highlighted (HTML) code block.
    """
    lang, code = match.groups()
    try:
        lexer = pygments.lexers.get_lexer_by_name(lang)
    except ValueError:
        lexer = pygments.lexers.TextLexer()
    formatted = pygments.highlight(code, lexer, FORMATTER)
    return (
        f'<pre class="highlight"><code class="language-{lang}">{formatted}</code></pre>'
    )


def md_highlight(md: str) -> str:
    """Replace markdown code blocks with pygmented HTML.

    Args:
        md: Markdown string with possible code fences.

    Returns:
        A string containing Markdown with code fenced blocks
        replaced with highlighted HTML.
    """
    return CODE_RE.sub(md_codeblock, md)


def md_highlight_and_parse(md: str) -> str:
    """Code highlight then convert to HTML.

    Args:
        md: Markdown string.

    Returns:
        A string with all the Markdown converted to HTML.
    """
    return md_parse(md_highlight(md))


def md_parse(md: str) -> str:
    """Parse Markdown.

    Args:
        md: Markdown string.

    Returns:
        HTML converted from the Markdown input.
    """
    return cmarkgfm.markdown_to_html(md, CMARK_FLAGS)


def tidy_html(html: str) -> str:
    """Tidy HTML.

    Args:
        html: html string

    Returns:
        Prettified HTML as string
    """
    result = tidy.parseString(
        html,
        indent="auto",
        show_body_only=1,
        # omit_optional_tags=1,
        tidy_mark=0,
    )
    return str(result)


def md2kb(filepath: pathlib.Path):
    md = filepath.read_text()
    html = tidy_html(md_highlight_and_parse(md))
    print(html)


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="Path to file to split", type=pathlib.Path)
    args = parser.parse_args()
    md2kb(args.filepath)


if __name__ == "__main__":
    run()
