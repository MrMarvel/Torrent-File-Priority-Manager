"""
auto_prio.py — авто-приоритеты файлов в qBittorrent.

Логика:
  * Берём список файлов торрента.
  * Оставляем только незагруженные (progress < 1.0).
  * Сортируем их «естественно» (file2 < file10).
  * Первому  -> приоритет 7 (Maximal).
  * Второму  -> приоритет 6 (High).
  * Остальным незагруженным -> приоритет 1 (Normal).
  * Скачанные файлы НЕ трогаем.
  * Раз в N секунд повторяем.
"""

import argparse
import re
import sys
import time
import requests


def natural_key(name: str):
    return [int(p) if p.isdigit() else p.lower()
            for p in re.split(r"(\d+)", name)]


class QBittorrent:
    def __init__(self, base_url: str, username: str = "", password: str = ""):
        self.base = base_url.rstrip("/")
        self.s = requests.Session()
        self.s.headers.update({"Referer": self.base})
        self.username = username
        self.password = password

    def login(self):
        r = self.s.post(
            f"{self.base}/api/v2/auth/login",
            data={"username": self.username, "password": self.password},
            timeout=10,
        )
        r.raise_for_status()
        if r.text.strip() != "Ok.":
            raise RuntimeError(f"Не удалось залогиниться: {r.text!r}")
        return self

    def files(self, torrent_hash: str) -> list[dict]:
        r = self.s.get(
            f"{self.base}/api/v2/torrents/files",
            params={"hash": torrent_hash},
            timeout=10,
        )
        r.raise_for_status()
        return r.json()

    def set_file_priority(self, torrent_hash: str, file_id: int, priority: int):
        r = self.s.post(
            f"{self.base}/api/v2/torrents/filePrio",
            data={"hash": torrent_hash, "id": file_id, "priority": priority},
            timeout=10,
        )
        r.raise_for_status()


def rebalance_priorities(qb: QBittorrent, torrent_hash: str, verbose: bool = True):
    files = qb.files(torrent_hash)
    if not files:
        return

    # Только незагруженные, отсортированные по имени
    pending = sorted(
        (f for f in files if f["progress"] < 1.0),
        key=lambda f: natural_key(f["name"]),
    )

    if verbose:
        print(f"[{time.strftime('%H:%M:%S')}] "
              f"всего файлов: {len(files)}, не завершено: {len(pending)}")

    if not pending:
        return

    # Целевые приоритеты для первых двух незагруженных
    targets = {}
    targets[pending[0]["index"]] = 7
    if len(pending) > 1:
        targets[pending[1]["index"]] = 6

    # Всем остальным незагруженным — Normal
    for f in pending[2:]:
        targets[f["index"]] = 1

    if verbose:
        print(f"  Max (7): {pending[0]['name']}")
        if len(pending) > 1:
            print(f"  High(6): {pending[1]['name']}")

    # Применяем только если отличается (чтоб не спамить API)
    for f in pending:
        idx = f["index"]
        target = targets[idx]
        if f.get("priority") != target:
            qb.set_file_priority(torrent_hash, idx, target)
            if verbose:
                print(f"     set prio {target} → [{idx}] {f['name']}")


def main():
    p = argparse.ArgumentParser(description="Авто-приоритеты файлов в qBittorrent")
    p.add_argument("hash", help="Хеш торрента (info hash)")
    p.add_argument("--url", default="http://localhost:8080",
                   help="URL WebUI (по умолчанию http://localhost:8080)")
    p.add_argument("--user", default="admin")
    p.add_argument("--password", default="adminadmin")
    p.add_argument("--interval", type=float, default=10.0,
                   help="Интервал проверки, сек (по умолчанию 10)")
    p.add_argument("--once", action="store_true", help="Один раз и выход")
    p.add_argument("-q", "--quiet", action="store_true")
    args = p.parse_args()

    qb = QBittorrent(args.url, args.user, args.password).login()
    print(f"Залогинились в {args.url}, торрент {args.hash}")

    try:
        while True:
            try:
                rebalance_priorities(qb, args.hash, verbose=not args.quiet)
            except requests.HTTPError as e:
                if e.response is not None and e.response.status_code == 403:
                    print("Сессия истекла, перелогин...")
                    qb.login()
                else:
                    print(f"HTTP ошибка: {e}")
            except Exception as e:
                print(f"Ошибка: {e}", file=sys.stderr)

            if args.once:
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nОстановлено.")


if __name__ == "__main__":
    main()