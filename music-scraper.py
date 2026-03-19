#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import mimetypes
import re
import sys
from pathlib import Path

from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3, ID3NoHeaderError
from mutagen.flac import FLAC, Picture
from mutagen.mp4 import MP4, MP4Cover

VERSION = "2.0.0"

FILENAME_PATTERN = re.compile(r"^(\d+)\s+(.+)\.(mp3|flac|m4a)$", re.IGNORECASE)

AUTO_COVER_NAMES = [
    "cover.jpg", "cover.jpeg", "cover.png", "cover.webp",
    "folder.jpg", "folder.jpeg", "folder.png", "folder.webp",
    "front.jpg", "front.jpeg", "front.png", "front.webp",
]


# ========================
# 工具函数
# ========================

def parse_filename(filename: str):
    match = FILENAME_PATTERN.match(filename)
    if not match:
        return None

    track_number = match.group(1).lstrip("0") or "0"
    title = match.group(2).strip()
    return track_number, title


def detect_mime_type(path: Path):
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "image/jpeg"


def find_auto_cover(folder: Path):
    for name in AUTO_COVER_NAMES:
        p = folder / name
        if p.exists():
            return p.resolve()
    return None


def infer_auto_tags(folder: Path):
    album = folder.name
    artist = folder.parent.name if folder.parent else None
    cover = find_auto_cover(folder)

    artists = [artist] if artist else None
    return artists, album, cover


# ========================
# 写入不同格式
# ========================

def write_mp3(path, track, title, artists, album, cover):
    try:
        try:
            audio = EasyID3(path)
        except ID3NoHeaderError:
            audio = EasyID3()
            audio.save(path)
            audio = EasyID3(path)

        audio["tracknumber"] = [track]
        audio["title"] = [title]

        if artists:
            audio["artist"] = artists
        if album:
            audio["album"] = [album]

        audio.save()

        if cover:
            with cover.open("rb") as f:
                data = f.read()

            mime = detect_mime_type(cover)

            tags = ID3(path)
            tags.delall("APIC")
            tags.add(APIC(
                encoding=3,
                mime=mime,
                type=3,
                desc="Cover",
                data=data
            ))
            tags.save(path)

    except Exception as e:
        print(f"[ERROR][MP3] {path} -> {e}")


def write_flac(path, track, title, artists, album, cover):
    try:
        audio = FLAC(path)

        audio["tracknumber"] = track
        audio["title"] = title

        if artists:
            audio["artist"] = artists
        if album:
            audio["album"] = album

        if cover:
            audio.clear_pictures()
            pic = Picture()
            pic.type = 3
            pic.mime = detect_mime_type(cover)

            with cover.open("rb") as f:
                pic.data = f.read()

            audio.add_picture(pic)

        audio.save()

    except Exception as e:
        print(f"[ERROR][FLAC] {path} -> {e}")


def write_m4a(path, track, title, artists, album, cover):
    try:
        audio = MP4(path)

        audio["trkn"] = [(int(track), 0)]
        audio["©nam"] = [title]

        if artists:
            audio["©ART"] = artists
        if album:
            audio["©alb"] = [album]

        if cover:
            with cover.open("rb") as f:
                data = f.read()

            fmt = MP4Cover.FORMAT_JPEG
            if cover.suffix.lower() == ".png":
                fmt = MP4Cover.FORMAT_PNG

            audio["covr"] = [MP4Cover(data, imageformat=fmt)]

        audio.save()

    except Exception as e:
        print(f"[ERROR][M4A] {path} -> {e}")


# ========================
# 分发
# ========================

def write_tags(path, track, title, artists, album, cover, dry_run):
    if dry_run:
        print(f"[DRY RUN] {path}")
        print(f"  track = {track}, title = {title}")
        print(f"  artist = {artists}, album = {album}, cover = {cover}")
        return

    ext = path.suffix.lower()

    if ext == ".mp3":
        write_mp3(path, track, title, artists, album, cover)
    elif ext == ".flac":
        write_flac(path, track, title, artists, album, cover)
    elif ext == ".m4a":
        write_m4a(path, track, title, artists, album, cover)
    else:
        print(f"[SKIP] 不支持格式: {path}")


def process_file(path, artists, album, cover, dry_run):
    parsed = parse_filename(path.name)
    if not parsed:
        print(f"[SKIP] {path}")
        return

    track, title = parsed
    write_tags(path, track, title, artists, album, cover, dry_run)


def process_folder(folder, artists, album, cover, dry_run):
    files = list(folder.rglob("*.*"))

    for f in files:
        if f.suffix.lower() not in [".mp3", ".flac", ".m4a"]:
            continue
        process_file(f, artists, album, cover, dry_run)


# ========================
# CLI
# ========================

def main():
    parser = argparse.ArgumentParser(
        description="音乐标签刮削工具（MP3 / FLAC / M4A）",
        formatter_class=argparse.RawTextHelpFormatter
    )

    g = parser.add_mutually_exclusive_group()
    g.add_argument("-d", "--dir", help="目录")
    g.add_argument("-f", "--file", help="单文件")

    parser.add_argument("-a", "--artist", action="append", help="作者（可多个）")
    parser.add_argument("-l", "--album", help="专辑")
    parser.add_argument("-c", "--cover", help="封面路径")

    parser.add_argument("-u", "--auto", action="store_true",
                        help="自动识别 artist/album/cover（互斥）")

    parser.add_argument("-n", "--dry-run", action="store_true",
                        help="仅预览，不写入标签")
    parser.add_argument("-v", "--version", action="version",
                        version=f"%(prog)s {VERSION}")

    args = parser.parse_args()

    # 互斥校验
    if args.auto and (args.artist or args.album or args.cover):
        parser.error("-u 与 -a/-l/-c 互斥")

    cover = Path(args.cover).resolve() if args.cover else None

    # 单文件
    if args.file:
        path = Path(args.file).resolve()

        if args.auto:
            artists, album, cover = infer_auto_tags(path.parent)
        else:
            artists = args.artist
            album = args.album

        process_file(path, artists, album, cover, args.dry_run)
        return

    # 目录
    folder = Path(args.dir or ".").resolve()

    if args.auto:
        artists, album, cover = infer_auto_tags(folder)
    else:
        artists = args.artist
        album = args.album

    process_folder(folder, artists, album, cover, args.dry_run)


if __name__ == "__main__":
    main()
