# Torrent-File-Priority-Manager

## Usage

This tool allows to automate setting files priority with logic:

1. In sorted list of files:

   1. select 1-st item and set max priority

   2. select 2-nd item and set high priority

2. Go to 1 with interval

## CLI help

```pwsh
usage: torrentfileprioritymanager.exe [-h] [--url URL] [--user USER] [--password PASSWORD] [--interval INTERVAL]
                                      [--once] [-q]
                                      hash

Авто-приоритеты файлов в qBittorrent

positional arguments:
  hash                 Хеш торрента (info hash)

options:
  -h, --help           show this help message and exit
  --url URL            URL WebUI (по умолчанию http://localhost:8080)
  --user USER
  --password PASSWORD
  --interval INTERVAL  Интервал проверки, сек (по умолчанию 10)
  --once               Один раз и выход
  -q, --quiet
```

## How to build from source

Windows + Visual Studio Enterprise 2026 (Clang, MSVC)

Nuitka

```pwsh
uv run python -m nuitka --onefile --standalone --clang --lto=yes --python-flag=no_asserts --python-flag=-OO --output-dir=dist --include-package=torrentfileprioritymanager --follow-imports --remove-output .\src\torrentfileprioritymanager
```
