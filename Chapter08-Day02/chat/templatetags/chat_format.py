import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


def _inline(text):
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return text


@register.filter
def format_message(value):
    """안전하게 escape한 뒤 자주 쓰는 Markdown만 표시합니다."""
    source = escape(value or "")
    parts = re.split(r"```([^\n`]*)\n?(.*?)```", source, flags=re.DOTALL)
    output = []
    for index, part in enumerate(parts):
        if index % 3 == 1:
            continue
        if index % 3 == 2:
            language = parts[index - 1].strip()
            language_class = f' class="language-{language}"' if language else ""
            output.append(f"<pre><code{language_class}>{part.strip()}</code></pre>")
            continue

        for line in part.splitlines():
            stripped = line.strip()
            if not stripped:
                output.append("<br>")
            elif stripped.startswith("### "):
                output.append(f"<h3>{_inline(stripped[4:])}</h3>")
            elif stripped.startswith("## "):
                output.append(f"<h2>{_inline(stripped[3:])}</h2>")
            elif stripped.startswith("# "):
                output.append(f"<h1>{_inline(stripped[2:])}</h1>")
            elif re.match(r"^[-*] ", stripped):
                output.append(f'<div class="md-list">• {_inline(stripped[2:])}</div>')
            elif re.match(r"^\d+\. ", stripped):
                output.append(f'<div class="md-list">{_inline(stripped)}</div>')
            else:
                output.append(f"<div>{_inline(line)}</div>")
    return mark_safe("".join(output))
