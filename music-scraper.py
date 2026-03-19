```
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import mimetypes
import re
import sys
from pathlib import Path

from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3, ID3NoHeaderError

VERSION = "1.2.0"

FILENAME_PATTERN = re.compile(r"^(\d+)\s+(.+)\.mp3$", re.IGNORECASE)

AUTO_COVER_NAMES = [
    "cover.jpg",
    "cover.jpeg",
    "cover.png",
    "cover.webp",
    "folder.jpg",
    "folder.jpeg",
    "folder.png",
    "folder.webp",
    "front.jpg",
    "front.jpeg",
    "front.png",
    "front.webp",
]


def parse_filename(filename: str):
    """
    从文件名中解析:
    '82 龍族の記憶.mp3' -> ('82', '龍族の記憶')
    """
    match = FILENAME_PATTERN.match(filename)
    if not match:
        return None

    track_number = match.group(1).lstrip("0") or "0"
    title = match.group(2).strip()
    return track_number, title


def detect_mime_type(image_path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(str(image_path))
    if mime_type in ("image/jpeg", "image/png", "image/webp"):
        return mime_type
    return "application/octet-stream"


def set_cover_art(mp3_path: Path, cover_path: Path):
    """
    写入专辑封面，覆盖已有 APIC
    """
    with cover_path.open("rb") as f:
        cover_data = f.read()

    mime_type = detect_mime_type(cover_path)

    try:
        tags = ID3(mp3_path)
    except ID3NoHeaderError:
        tags = ID3()

    tags.delall("APIC")
    tags.add(
        APIC(
            encoding=3,   # UTF-8
            mime=mime_type,
            type=3,       # front cover
            desc="Cover",
            data=cover_data,
        )
    )
    tags.save(mp3_path)


def write_tags(
    mp3_path: Path,
    track_number: str,
    title: str,
    artists=None,
    album=None,
    cover_path=None,
    dry_run=False,
):
    """
    写入 MP3 标签:
    - title
    - tracknumber
    - artist (可多个)
    - album
    - cover art
    """
    if dry_run:
        print(f"[DRY RUN] {mp3_path}")
        print(f"  tracknumber = {track_number}")
        print(f"  title       = {title}")
        if artists:
            print(f"  artist      = {artists}")
        if album:
            print(f"  album       = {album}")
        if cover_path:
            print(f"  cover       = {cover_path}")
        return

    try:
        try:
            audio = EasyID3(mp3_path)
        except ID3NoHeaderError:
            audio = EasyID3()
            audio.save(mp3_path)
            audio = EasyID3(mp3_path)

        audio["tracknumber"] = [track_number]
        audio["title"] = [title]

        if artists:
            audio["artist"] = artists

        if album:
            audio["album"] = [album]

        audio.save()

        if cover_path:
            set_cover_art(mp3_path, cover_path)

        print(f"[OK] {mp3_path}")

    except Exception as e:
        print(f"[ERROR] {mp3_path} -> {e}")


def find_auto_cover(target_dir: Path):
    """
    在目标目录中自动查找常见封面文件名
    """
    for name in AUTO_COVER_NAMES:
        candidate = target_dir / name
        if candidate.exists() and candidate.is_file():
            return candidate.resolve()
    return None


def infer_auto_tags(target_dir: Path):
    """
    自动推断:
    - album = 当前目录名
    - artist = 父目录名
    - cover = 目录中的常见封面文件
    """
    album = target_dir.name if target_dir.name else None

    artist = None
    parent = target_dir.parent
    if parent and parent != target_dir and parent.name:
        artist = parent.name

    cover_path = find_auto_cover(target_dir)

    artists = [artist] if artist else None
    return artists, album, cover_path


def process_file(mp3_file, artists, album, cover_path, dry_run):
    if not mp3_file.exists() or not mp3_file.is_file():
        print(f"错误：文件不存在 {mp3_file}")
        return

    if mp3_file.suffix.lower() != ".mp3":
        print(f"错误：仅支持 MP3 文件 {mp3_file}")
        return

    parsed = parse_filename(mp3_file.name)
    if not parsed:
        print(f"[SKIP] 文件名不符合规则: {mp3_file.name}")
        return

    track_number, title = parsed

    write_tags(
        mp3_file,
        track_number,
        title,
        artists=artists,
        album=album,
        cover_path=cover_path,
        dry_run=dry_run,
    )

    print("\n处理完成（单文件）")


def process_folder(folder, artists, album, cover_path, dry_run):
    mp3_files = list(folder.rglob("*.mp3"))

    if not mp3_files:
        print("未找到 mp3 文件。")
        return

    success = 0
    skipped = 0

    for mp3_file in mp3_files:
        parsed = parse_filename(mp3_file.name)
        if not parsed:
            print(f"[SKIP] {mp3_file}")
            skipped += 1
            continue

        track_number, title = parsed
        write_tags(
            mp3_file,
            track_number,
            title,
            artists=artists,
            album=album,
            cover_path=cover_path,
            dry_run=dry_run,
        )
        success += 1

    print("\n处理完成")
    print(f"成功: {success}，跳过: {skipped}")


def build_parser():
    parser = argparse.ArgumentParser(
        description="MP3 标签刮削工具（基于文件名：音轨号 + 标题）",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    target_group = parser.add_mutually_exclusive_group()
    target_group.add_argument(
        "-d", "--dir",
        help="音乐目录（默认：当前目录）",
    )
    target_group.add_argument(
        "-f", "--file",
        help="单个 MP3 文件路径",
    )

    parser.add_argument(
        "-a", "--artist",
        action="append",
        dest="artists",
        help="作者（可重复使用，例如 -a A -a B）",
    )

    parser.add_argument(
        "-l", "--album",
        help="专辑名称",
    )

    parser.add_argument(
        "-c", "--cover",
        help="封面图片路径（jpg/jpeg/png/webp）",
    )

    parser.add_argument(
        "-u", "--auto",
        action="store_true",
        help="自动识别 artist / album / cover；与 -a / -l / -c 互斥",
    )

    parser.add_argument(
        "-n", "--dry-run",
        action="store_true",
        help="仅预览，不写入标签",
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {VERSION}",
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # 手动校验：--auto 与相关参数互斥
    if args.auto and (args.artists or args.album or args.cover):
        parser.error("--auto / -u 与 --artist / --album / --cover 互斥")

    # 解析封面
    cover_path = None
    if args.cover:
        cover_path = Path(args.cover).expanduser().resolve()
        if not cover_path.exists() or not cover_path.is_file():
            print(f"错误：封面文件不存在 {cover_path}")
            sys.exit(1)

    # 单文件模式
    if args.file:
        mp3_file = Path(args.file).expanduser().resolve()

        if not mp3_file.exists() or not mp3_file.is_file():
            print(f"错误：无效文件 {mp3_file}")
            sys.exit(1)

        artists = args.artists
        album = args.album
        final_cover_path = cover_path

        if args.auto:
            auto_artists, auto_album, auto_cover = infer_auto_tags(mp3_file.parent)
            artists = auto_artists
            album = auto_album
            final_cover_path = auto_cover

        process_file(
            mp3_file=mp3_file,
            artists=artists,
            album=album,
            cover_path=final_cover_path,
            dry_run=args.dry_run,
        )
        return

    # 目录模式（默认当前目录）
    folder = Path(args.dir or ".").expanduser().resolve()

    if not folder.exists() or not folder.is_dir():
        print(f"错误：无效目录 {folder}")
        sys.exit(1)

    artists = args.artists
    album = args.album
    final_cover_path = cover_path

    if args.auto:
        auto_artists, auto_album, auto_cover = infer_auto_tags(folder)
        artists = auto_artists
        album = auto_album
        final_cover_path = auto_cover

    process_folder(
        folder=folder,
        artists=artists,
        album=album,
        cover_path=final_cover_path,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
```
