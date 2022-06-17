from __future__ import annotations

import argparse
from typing import Sequence
import subprocess


def _retab(line: str, spaces: int) -> str:
    lstripped = line.lstrip(' ')
    return '\t' * (spaces // 2) + lstripped


def _process_lines(
        fmt_lines: list[str],
        new_lines: list[str],
) -> None:
    for line_num, fmt_line in enumerate(fmt_lines):
        new_line = fmt_line.lstrip(' ')
        spaces = len(fmt_line) - len(new_line)

        # !! SIMPLIFY / SKIP / SHORTCUT all char processing for: comments
        # !!
        if new_line[0] == '#':
            new_lines.append(_retab(new_line, spaces))
            continue

        in_string = False

        # !! markers for open interpolation, open square bracket '[', and open round bracket '(':
        # !! used as both bool and index of when we encounter an open bracket
        # !! the easiest/best way to check if spacing is needed is if a we have a previous open bracket on the same line
        open_interpolate = []
        open_square = []
        open_round = []

        i = -1
        while True:
            i += 1
            if (c := new_line[i]) == '\n':
                break

            if in_string and c != '"':

                if new_line[i:i+2] == '${' and new_line[i-1] != '$':
                    open_interpolate.append(i+1)
                    i += 1
                elif c == '}' and open_interpolate:
                    h = open_interpolate.pop()
                    new_line = new_line[:h+1] + ' ' + new_line[h+1:i] + ' ' + new_line[i:]
                    i += 2
                elif c == '\\':
                    i += 1

                continue

            if c == '"':
                in_string = not in_string

            elif c == '(':
                open_round.append(i)
            elif c == ')':
                if open_round:
                    h = open_round.pop()
                    if new_line[h+1] != '"':
                        new_line = new_line[:h+1] + ' ' + new_line[h+1:i] + ' ' + new_line[i:]
                        i += 2

            elif c == '[':
                if new_line[i+1] == ']':
                    i += 1
                else:
                    open_square.append(i)
            elif c == ']':
                if open_square:
                    h = open_square.pop()
                    if new_line[h+1] != '"':
                        new_line = new_line[:h+1] + ' ' + new_line[h+1:i] + ' ' + new_line[i:]
                        i += 2

        new_line = _retab(new_line, spaces)
        new_lines.append(new_line)


def _fix_file(
        filename: str,
) -> bool:
    p_cat = subprocess.Popen(['cat', filename], text=True, stdout=subprocess.PIPE)
    p_fmt = subprocess.Popen(['terraform', 'fmt', '-'], text=True, stdin=p_cat.stdout, stdout=subprocess.PIPE)

    p_cat.stdout.close()
    p_cat.stdout = None
    p_cat.communicate()

    fmt_lines = p_fmt.stdout.readlines()
    new_lines = []

    _process_lines(fmt_lines, new_lines)

    with open(filename, mode='r') as source:
        source_lines = source.readlines()

    with open(filename, mode='w') as new_file:
        new_file.writelines(new_lines)

    if new_lines != source_lines:
        return True

    return False


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*', help='Filenames to fix')
    args = parser.parse_args(argv)

    return_code = 0
    for filename in args.filenames:
        if _fix_file(filename):
            print(f'Fixed { filename }')
            return_code = 1
    return return_code


if __name__ == '__main__':
    raise SystemExit(main())
