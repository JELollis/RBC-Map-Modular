"""Reject unexpected Unicode punctuation in Python source code.

Comments and string literals may contain intentional Unicode.  Characters
that appear as invalid/standalone tokens are rejected because they can turn a
valid-looking Python statement into invalid syntax (for example U+037E).
"""

from __future__ import annotations

import io
import pathlib
import tempfile
import tokenize


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE_FILES = tuple(sorted(ROOT.glob("*.py"))) + tuple(sorted((ROOT / "tools").glob("*.py")))
IGNORED_TOKEN_TYPES = {tokenize.STRING, tokenize.COMMENT}
if hasattr(tokenize, "FSTRING_MIDDLE"):
    IGNORED_TOKEN_TYPES.add(tokenize.FSTRING_MIDDLE)
if hasattr(tokenize, "TSTRING_MIDDLE"):
    IGNORED_TOKEN_TYPES.add(tokenize.TSTRING_MIDDLE)
BIDI_CONTROLS = set("\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069")


def check_file(path: pathlib.Path) -> list[str]:
    errors: list[str] = []
    source = path.read_bytes()
    try:
        display_path = str(path.relative_to(ROOT))
    except ValueError:
        display_path = str(path)
    decoded = source.decode("utf-8")
    for line_number, line in enumerate(decoded.splitlines(), start=1):
        controls = BIDI_CONTROLS.intersection(line)
        if controls:
            codepoint = ", ".join(f"U+{ord(char):04X}" for char in sorted(controls))
            errors.append(f"{display_path}:{line_number}: bidi control(s) {codepoint}")
    try:
        tokens = tokenize.tokenize(io.BytesIO(source).readline)
        for token in tokens:
            if token.type not in IGNORED_TOKEN_TYPES:
                unexpected = [char for char in token.string if ord(char) > 127]
                if not unexpected:
                    continue
                codepoint = ", ".join(f"U+{ord(char):04X}" for char in unexpected)
                errors.append(f"{display_path}:{token.start[0]}: {codepoint}")
    except (SyntaxError, tokenize.TokenError) as exc:
        errors.append(f"{display_path}: {exc}")
    return errors


def self_test() -> list[str]:
    """Verify that the checker catches the invalid punctuation it targets."""
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".py", delete=False) as handle:
        path = pathlib.Path(handle.name)
        handle.write("value = 1\u037e\n")
    try:
        return [] if check_file(path) else ["self-test did not detect U+037E"]
    finally:
        path.unlink(missing_ok=True)


def main() -> int:
    errors = self_test()
    errors.extend(error for path in SOURCE_FILES for error in check_file(path))
    if errors:
        print("Unexpected Unicode token(s) found:")
        print("\n".join(errors))
        return 1
    print(f"Unicode token check passed for {len(SOURCE_FILES)} Python files and its self-test.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
