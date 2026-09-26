Windows + Visual Studio Enterprise 2026 (Clang, MSVC)

Nuitka

```pwsh
uv run python -m nuitka --onefile --standalone --clang --lto=yes --python-flag=no_asserts --python-flag=-OO --output-dir=dist --include-package=torrentfileprioritymanager --follow-imports --remove-output .\src\torrentfileprioritymanager
```
