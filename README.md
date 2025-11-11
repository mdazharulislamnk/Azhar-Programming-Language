# Azhar Programming Language

**Azhar** is a small, statically type-checked programming language with a hand-written lexer, parser, type checker, and tree-walking interpreter. It ships as a **single Windows executable** and an **installer** so anyone can install and run `.azhar` programs.

## Features

- **REPL** for interactive use
- Run source files from the command line
- **Strong, explicit types**: `int`, `string`, `bool`, `void`
- Variables, arithmetic, comparisons
- `if/else`, `while`, `break`
- Functions with typed parameters and returns
- Simple I/O: `print`, `output`, `read_int`, `read_string`

---

## Repository Layout
- Azhar-Programming-Language/
- ├── .venv/                  # local virtual environment (not required in repo)
- ├── azhar/                  # language implementation (Python package)
- │   ├── init.py
- │   ├── tokens.py
- │   ├── errors.py
- │   ├── ast.py
- │   ├── lexer.py
- │   ├── parser.py
- │   ├── typechecker.py     # renamed from types.py to avoid stdlib name clash
- │   ├── builtins.py
- │   ├── interp.py
- │   ├── repl.py
- │   ├── cli.py             # script/REPL entry inside the package
- │   └── modules/           # optional extension area
- ├── build/                  # PyInstaller build artifacts (safe to delete)
- ├── dist/                   # final outputs (azhar.exe, sample .azhar programs)
- ├── tests/                  # unit/integration tests (optional in CI)
- ├── cli_entry.py            # robust bootstrap entry for frozen exe
- ├── README.md               # this file
- ├── LICENSE
- ├── CHANGELOG.md
- └── pyproject.toml          # optional packaging metadata
---

- Clear separation of compiler stages in `azhar/` for maintainability.
- `tests/` keeps the language reliable as you add features.
- `dist/` and `build/` are standard outputs for shipping binaries.
- `cli_entry.py` ensures the packaged exe can always import the `azhar` package.

---

## Prerequisites

- **Windows 10/11 x64**
- **Python 3.10+** (for building)
- *Optional*: Git, a terminal, and an editor

---

## Quick Start (Run from Source)

1. **Create and activate a virtual environment**

   
   - python -m venv .venv
   - .venv\Scripts\activate

- Run the REPL from source  python -m azhar.cli
- Run a program from source  python -m azhar.cli path\to\file.azhar

- Tip: All intra-package imports should be absolute (from azhar.parser import Parser, etc.). This keeps both source and frozen exe runs stable.

- Build a Single .exe (Windows)
- From the repository root:

#Activate venv and install build .venv\Scripts\activate

- python -m pip install --upgrade pip pyinstaller
- Clean previous artifacts (optional but recommended) del azhar.spec
- rmdir /s /q build dist __pycache__ 2>nul
- Build the  pyinstaller --onefile --name azhar --collect-all azhar cli_entry.py

- Output: dist\azhar.exe


# Run a script
- azhar path\to\file.azhar
- Tip: When double-clicking azhar.exe, the console may close immediately.
- Prefer running from a terminal, or use a .bat file:batazhar hello.azhar


# Language Reference

- Types int, string, bool, void (for functions returning nothing)

# Variables

 <pre>let a: int = 3
  let name: string = "Azhar"
  let ok: bool = true
  a = a + 1
  ok = false ```</pre>

# Arithmetic & Comparisons

- +, -, *, /           # on int
- ==, !=, <, <=, >, >= # -> bool
- I/O

- print(expr)        # prints with newline
- output(expr)       # prints without newline
- read_int()
- read_string()

# Conditionals

- let ok: bool = true
- if ok do
-    print(1)
- else do
-    print(0)
- end

#Loops and break

- let i: int = 0
- while i < 3 do
-    print(i)
-    if i == 1 do
-        break
-    end
-    i = i + 1
- end

#Functions

- function add(a: int, b: int) -> int do
-   return a + b
- end
- print(add(4, 5))  # 9

- function banner() -> void do
-   print("AZHAR")
- end
- banner()

- Full Example (hello.azhar)

- print("AZHAR")

- function add(a: int, b: int) -> int do
-    return a + b
- end

- let x: int = 1
- x = add(x, 2)
- print(x)

- let n: int = 7
- print(n + 5)

- Expected output:
- 3
- 12


# Developer Notes

- Absolute imports: Always use from azhar.module import Name to avoid issues in frozen builds.
- Name conflicts: The stdlib has a types module. Use typechecker.py and import via from azhar.typechecker import TypeChecker.
- Error handling: All stages raise Azhar-specific errors with file + line info.


# Testing

- python -m pip install pytest
- python -m pytest -q

- Covers:
- Tokenization
- Parsing
- Type checking
- Interpreter behavior
- End-to-end integration


# Troubleshooting

- Issue Solution Console closes immediately Run from terminal or add pause in a .bat file “No module named azhar” in exe Use --collect-all azhar and cli_entry.py Import errors with azhar.typesRename file to typechecker.py and update imports

# Roadmap Ideas

- Arrays and user-defined records
- Standard library modules (math, file I/O)
- Better error spans and diagnostics
- Optimizing interpreter / bytecode VM
- Cross-platform packaging
