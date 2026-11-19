# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Korean publishing/editing CLI toolkit (`ko-editor`). A collection of standalone Python 3 command-line scripts for Korean-language book production workflows: speech level conversion, foreign-language transliteration, MS Word/PDF manipulation, file management, and web utilities.

## Setup

```
pip install -r requirements.txt
# Windows-only scripts additionally need: pip install pywin32
```

## Running Tests

Tests are simple scripts (not pytest), run them directly:
```
python test_pyko.py
python test_indian.py
```

## Architecture

**No framework or package structure** -- each `.py` file in the repo root is a standalone CLI tool. Scripts read from stdin or file arguments and write to stdout or files.

### Key shared modules

- `common_io.py` -- shared I/O helpers (`read_input`, `write_output`, `read_file`, `write_file`, `get_file_paths_from_args`) used by most scripts
- `convert_speech_level.py` -- core speech-level conversion engine driven by the lookup table `ko_speech_level.txt`. Used by `hae.py`, `haera.py`, `haeyo.py`, `hasipsio.py`, and `fakemt.py`
- `fileutil.py` -- file utilities (`latest_file`, `rename_numbered_files`) used by other scripts

### Speech level converters

`hae.py`, `haera.py`, `haeyo.py`, `hasipsio.py` are thin wrappers that call `convert_speech_level.convert()` with the target level. They accept stdin or file arguments via `common_io`.

### Transliteration

- `pyko.py` -- Chinese Pinyin to Korean, using `pinyin_ko.csv`
- `indian.py` / `indiantree.py` -- Indian languages (romanized) to Korean, using `indianlatin_ko.csv`

### Vendored libraries

- `google_trans_new/` -- vendored Google Translate client (used by `fakemt.py`)
- `pattern/` and `pass2act/` -- vendored NLP libraries for English passive-to-active voice conversion (used by `p2a.py`)

## Conventions

- All text files use UTF-8 encoding
- Scripts are designed to work as CLI tools (many have shebangs, intended to be on PATH)
- README and comments are in Korean
- CSV lookup tables use comma-separated format; TSV files use tab separation
