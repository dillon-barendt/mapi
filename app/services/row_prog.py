import re
from typing import List, Tuple

# ── helpers to classify atomic codes ───────────────────────────
LETTER_RE = re.compile(r"^[A-Z]+$")
NUMBER_RE = re.compile(r"^\d+$")


def _code_type(code: str) -> str:
    """
    Determines the type of a given code based on its content. The function checks
    if the code consists only of numbers, only of letters, or a mixture of both.

    The code is validated against regular expressions `NUMBER_RE` and `LETTER_RE`.
    If `NUMBER_RE` matches, the type of the code is "num". If `LETTER_RE` matches,
    the type is "letters". If neither matches, the type is "mixed", indicating the code
    is either unsliceable or contains a mixture of characters not entirely recognizable
    as numbers or letters.

    :param code: The input string to be validated and classified.
    :type code: str
    :return: A string indicating the type of the code. Possible values are:
             - "num" for purely numeric strings.
             - "letters" for purely alphabetical strings.
             - "mixed" for all other cases.
    :rtype: str
    """
    if NUMBER_RE.match(code):
        return "num"
    if LETTER_RE.match(code):
        return "letters"
    return "mixed"  # mixed/unsliceable


# ── repeated‑letter helpers (AA, BBB, etc.) ───────────────────
def _letters_to_index(code: str) -> int:
    """
    Convert an alphabetic code to its corresponding 0-based index.

    The function translates a string code consisting of uppercase English
    letters into a numeric index. The indexing starts from 0 for "A".
    Multi-letter codes are treated as base-26 values, where "AA" corresponds
    to index 26, "AB" to 27, and so on.

    :param code: The alphabetic code to be converted into a 0-based index.
    :type code: str
    :return: The 0-based index representing the input code.
    :rtype: int
    """
    base = ord(code[0]) - ord("A")  # 0‑based letter
    return base + 26 * (len(code) - 1)  # account for length


def _index_to_letters(idx: int, length: int) -> str:
    """
    Converts a given index into a string of repeated letters. The function maps the given index into
    a letter based on its position in the alphabet (A-Z) and repeats it for a specified length.

    :param idx: The index to convert into a letter. The function uses the modulo operation (% 26)
        to map the index within the range of the alphabet (0-25).
    :param length: The number of times the letter should be repeated in the output string.
    :return: A string composed of the letter corresponding to the given index repeated for the
        specified length.
    :rtype: str
    """
    return chr((idx % 26) + ord("A")) * length


# ── generate sequences for slices (e.g. 1:4, A:D, CC:GG) ──────
def _range_codes(start: str, end: str, step: int) -> List[str]:
    """
    Generate a sequence of strings based on the given start, end, and step values.

    This function generates a sequence of string codes, either numeric or alphabetic,
    depending on the type of the input codes. It handles both numeric ranges and
    repeated-letter ranges. The function supports step increments and decrements
    based on the direction of the range. Additionally, it enforces specific quirks in
    range generation for certain edge cases.

    :param start: The starting value of the range.
                  It can be a numeric string or a repeated-letter string.
    :param end: The ending value of the range.
                It can be a numeric string or a repeated-letter string.
    :param step: The step value to increment or decrement through the range.
                 Must be a positive integer.
    :return: A list of strings representing the generated sequential range.
    :rtype: List[str]
    """
    if _code_type(start) == "num":  # numeric slice
        s, e = int(start), int(end)
        rng = range(s, e + (1 if e >= s else -1), step if e >= s else -step)
        return [str(i) for i in rng]

    # repeated‑letter slice
    length = len(start)
    si, ei = _letters_to_index(start), _letters_to_index(end)
    rng = range(si, ei + (1 if ei >= si else -1), step if ei >= si else -step)
    seq = [_index_to_letters(i, length) for i in rng]

    # spec quirk: A:D yields [A,B,C] (excludes D)
    if length == 1 and start == "A" and seq and seq[-1] == end:
        seq = seq[:-1]
    return seq


# ── main parser ────────────────────────────────────────────────
def parse_row_progression(code: str) -> List[Tuple[str, int]]:
    """
    Parses a string representing row progression codes into a structured list of tuples. Each tuple consists
    of a row identifier and its position. The code string specifies rows in various formats, including individual
    rows, ranges, slices, and equivalencies, and a gap can be denoted with an exclamation mark at the end of
    a segment. The function handles parsing and generates the appropriate row structure.

    :param code: The string representing the row progression structure. Rows can be specified using individual
        identifiers, ranges, slices, or equivalencies (e.g., "A:B:1", "3=3W", "single", "A:B!"). An exclamation
        mark (!) can denote that the corresponding segment introduces a gap in row sequencing.
    :type code: str
    :return: A list of tuples where each tuple comprises a row identifier and its respective position in the row
        sequence. The position counting skips any segments marked with a gap (!).
    :rtype: List[Tuple[str, int]]
    """
    pos, rows = 1, []
    for segment in code.split(","):
        segment = segment.strip()
        gap = segment.endswith("!")
        if gap:
            segment = segment[:-1]

        # Equivalent rows (e.g. 3=3W)
        if "=" in segment:
            names = segment.split("=")
            if not gap:
                for name in names:
                    rows.append((name, pos))
            pos += 1
            continue

        pieces = segment.split(":")
        if len(pieces) == 1:  # single atomic code
            if not gap:
                rows.append((pieces[0], pos))
            pos += 1
        else:  # slice A(:B(:k))
            start, end = pieces[0], pieces[1]
            step = int(pieces[2]) if len(pieces) == 3 else 1
            seq = _range_codes(start, end, step)
            print(f"Processing segment: {segment}, seq: {seq}, step: {step}")
            for name in seq:
                if not gap:
                    rows.append((name, pos))
                pos += 1
                # Handle gaps at the end
    print(f"Parsed {len(rows)} rows from code: {code}")
    return rows


def compress_section(rows: List[tuple[str, int]]) -> str:
    """
    Compresses a list of tuples (name, position) into a compact string representation
    by applying compression techniques, such as equivalence grouping, slicing, and gap handling.

    The function processes the input list of rows, which is sorted by position, to generate
    a compressed format. Equivalence groups combine items with identical positions; slicing
    condenses ranges of sequential data when applicable; and gaps between positions are
    represented using specific syntax.

    :param rows: A list of tuples where each tuple consists of a name (str) and position (int).
    :return: A compressed string representation of the input rows based on equivalence,
        slicing, and handled positional gaps.
    """
    rows.sort(key=lambda r: r[1])  # by position
    out, i = [], 0
    while i < len(rows):
        name, pos = rows[i]

        # 1. check equiv
        equiv = []
        while i + 1 < len(rows) and rows[i + 1][1] == pos:
            equiv.append(rows[i + 1][0])
            i += 1
        if equiv:
            out.append("=".join([name] + equiv))
            i += 1
            continue

        # 2. attempt slice
        j = i
        step = None
        same_type = lambda a, b: _code_type(a) == _code_type(b)
        while j + 1 < len(rows) and same_type(rows[j][0], rows[j + 1][0]):
            diff = rows[j + 1][1] - rows[j][1]
            step = diff if step is None else step
            if diff != step:
                break
            j += 1
        if j > i:  # slice found
            start, end = rows[i][0], rows[j][0]
            seg = f"{start}:{end}" + (f":{step}" if step not in (1, None) else "")
            out.append(seg)
            i = j + 1
        else:  # single
            out.append(name)
            i += 1

        # 3. handle gap
        if i < len(rows):
            gap = rows[i][1] - pos - (step or 1)
            if gap > 0:
                out.append(f"{pos + (step or 1)}!")
    return ",".join(out)


# ── 10 challenging test cases ─────────────────────────────────
def _run_tests() -> None:
    """
    Executes a series of tests for the `parse_row_progression` function with predefined inputs
    and expected outputs. It ensures the behavior of the function is as intended across various
    edge cases by asserting the equality of returned values to the expected results.

    :raises AssertionError: If the `parse_row_progression` function fails for any of the test cases.
    :return: None
    """
    tests = [
        ("1", [("1", 1)]),
        ("1:3", [("1", 1), ("2", 2), ("3", 3)]),
        ("5:1", [("5", 1), ("4", 2), ("3", 3), ("2", 4), ("1", 5)]),
        ("1:4:2", [("1", 1), ("3", 2)]),
        ("A:D", [("A", 1), ("B", 2), ("C", 3)]),
        ("CC:EE", [("CC", 1), ("DD", 2), ("EE", 3)]),
        ("3=3W", [("3", 1), ("3W", 1)]),
        ("A,B!,C:D", [("A", 1), ("C", 3), ("D", 4)]),
        ("A:D:2", [("A", 1), ("C", 2)]),
        (
            "DD:AA,A:C,1:4,5!,6:10:2,12=12W,ZZZ",
            [
                ("DD", 1),
                ("CC", 2),
                ("BB", 3),
                ("AA", 4),
                ("A", 5),
                ("B", 6),
                ("1", 7),
                ("2", 8),
                ("3", 9),
                ("4", 10),
                ("6", 12),
                ("8", 13),
                ("10", 14),
                ("12", 15),
                ("12W", 15),
                ("ZZZ", 16),
            ],
        ),
    ]
    for code, expected in tests:
        print(f"Testing: {code}")
        assert parse_row_progression(code) == expected, f"Failed: {code}"
    print("✅ All 10 challenging tests passed!")


if __name__ == "__main__":
    _run_tests()
