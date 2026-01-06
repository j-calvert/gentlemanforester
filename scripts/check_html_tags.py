#!/usr/bin/env python3
import sys
from html.parser import HTMLParser
from pathlib import Path

VOID_ELEMENTS = {
    'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'
}

class TagChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() in VOID_ELEMENTS:
            return
        self.stack.append((tag, self.getpos()))

    def handle_startendtag(self, tag, attrs):
        # Self-closing tag (e.g. <img />) - treat as void
        return

    def handle_endtag(self, tag):
        if not self.stack:
            self.errors.append(f"Unexpected closing </{tag}> at {self.getpos()}")
            return
        last_tag, pos = self.stack.pop()
        if last_tag.lower() != tag.lower():
            self.errors.append(f"Mismatched closing </{tag}> at {self.getpos()}, expected </{last_tag}> from {pos}")

    def close(self):
        super().close()
        if self.stack:
            for tag, pos in self.stack:
                self.errors.append(f"Unclosed <{tag}> opened at {pos}")


def check_file(p: Path):
    data = p.read_text(encoding='utf-8')
    parser = TagChecker()
    try:
        parser.feed(data)
        parser.close()
    except Exception as e:
        return [f"Parse error: {e}"]
    return parser.errors


def main():
    root = Path(__file__).resolve().parents[1]
    html_files = list(root.glob('**/*.html'))
    any_errors = False
    for f in sorted(html_files):
        errs = check_file(f)
        if errs:
            any_errors = True
            print(f"--- {f.relative_to(root)} ---")
            for e in errs:
                print(e)
            print()
    if not any_errors:
        print('No unclosed/mismatched tags found.')

if __name__ == '__main__':
    main()
