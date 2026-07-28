"""
preprocess.py — Pre-process Markdown before doc_writer.

Strips leading section numbers from headings (e.g. ## 1. Introduction → ## Introduction)
and normalises excessive blank lines.

Usage:
  python preprocess.py input.md [output.md]

If output path is omitted, writes to input_clean.md.
"""
import re
import sys
import pathlib


def preprocess(input_path: str, output_path: str = None) -> str:
    text = pathlib.Path(input_path).read_text(encoding='utf-8')

    # Strip leading numbers from headings: ## 0. | ## 1. | ### 2.3 | #### 1.2.3 etc.
    text = re.sub(r'^(#{1,4})\s+\d+(\.\d+)*\.?\s+', r'\1 ', text, flags=re.MULTILINE)

    # Normalise 3+ consecutive blank lines to 2
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Strip trailing whitespace from lines
    text = '\n'.join(line.rstrip() for line in text.splitlines())

    if output_path is None:
        p = pathlib.Path(input_path)
        output_path = str(p.with_name(p.stem + '_clean' + p.suffix))

    pathlib.Path(output_path).write_text(text, encoding='utf-8')
    print(f'Preprocessed → {output_path}')
    return output_path


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python preprocess.py <input.md> [output.md]')
        sys.exit(1)
    preprocess(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
