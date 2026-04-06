#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import mimetypes
import re
import sys
from pathlib import Path

from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, COMM, ID3, ID3NoHeaderError
from mutagen.flac import FLAC, Picture
from mutagen.mp4 import MP4, MP4Cover

VERSION = "2.1.0"

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


def ensure_file_exists(path: Path, parser=None, name="文件"):
    if not path.exists():
        msg = f"{name}不存在: {path}"
        if parser:
            parser.error(msg)
        raise FileNotFoundError(msg)


def flatten_value(value):
    if value is None:
        return None
    if isinstance(value, list):
        return "; ".join(str(x) for x in value)
    return str(value)


# ========================
# 写入不同格式
# ========================

def write_mp3(path, track, title, artists, album, comment, cover):
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

        tags = ID3(path)

        if comment is not None:
            tags.delall("COMM")
            tags.add(COMM(
                encoding=3,
                lang="eng",
                desc="Comment",
                text=comment
            ))

        if cover:
            with cover.open("rb") as f:
                data = f.read()

            mime = detect_mime_type(cover)

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


def write_flac(path, track, title, artists, album, comment, cover):
    try:
        audio = FLAC(path)

        audio["tracknumber"] = track
        audio["title"] = title

        if artists:
            audio["artist"] = artists
        if album:
            audio["album"] = album
        if comment is not None:
            audio["comment"] = comment

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


def write_m4a(path, track, title, artists, album, comment, cover):
    try:
        audio = MP4(path)

        audio["trkn"] = [(int(track), 0)]
        audio["©nam"] = [title]

        if artists:
            audio["©ART"] = artists
        if album:
            audio["©alb"] = [album]
        if comment is not None:
            audio["©cmt"] = [comment]

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
# 读取不同格式
# ========================

def show_mp3_tags(path):
    try:
        info = {
            "file": str(path),
            "format": "MP3",
            "track": None,
            "title": None,
            "artist": None,
            "album": None,
            "comment": None,
            "cover": "无",
        }

        try:
            audio = EasyID3(path)
            info["track"] = flatten_value(audio.get("tracknumber"))
            info["title"] = flatten_value(audio.get("title"))
            info["artist"] = flatten_value(audio.get("artist"))
            info["album"] = flatten_value(audio.get("album"))
        except Exception:
            pass

        tags = ID3(path)

        comms = tags.getall("COMM")
        if comms:
            texts = []
            for c in comms:
                if isinstance(c.text, list):
                    texts.extend(str(x) for x in c.text)
                else:
                    texts.append(str(c.text))
            info["comment"] = " | ".join(texts)

        apics = tags.getall("APIC")
        if apics:
            info["cover"] = f"有 ({len(apics)} 张)"

        return info
    except Exception as e:
        return {"file": str(path), "error": str(e)}


def show_flac_tags(path):
    try:
        audio = FLAC(path)
        info = {
            "file": str(path),
            "format": "FLAC",
            "track": flatten_value(audio.get("tracknumber")),
            "title": flatten_value(audio.get("title")),
            "artist": flatten_value(audio.get("artist")),
            "album": flatten_value(audio.get("album")),
            "comment": flatten_value(audio.get("comment")),
            "cover": "有" if getattr(audio, "pictures", None) else "无",
        }
        if getattr(audio, "pictures", None):
            info["cover"] = f"有 ({len(audio.pictures)} 张)"
        return info
    except Exception as e:
        return {"file": str(path), "error": str(e)}


def show_m4a_tags(path):
    try:
        audio = MP4(path)
        info = {
            "file": str(path),
            "format": "M4A",
            "track": None,
            "title": flatten_value(audio.get("©nam")),
            "artist": flatten_value(audio.get("©ART")),
            "album": flatten_value(audio.get("©alb")),
            "comment": flatten_value(audio.get("©cmt")),
            "cover": "无",
        }

        trkn = audio.get("trkn")
        if trkn and len(trkn) > 0:
            info["track"] = str(trkn[0][0])

        covr = audio.get("covr")
        if covr:
            info["cover"] = f"有 ({len(covr)} 张)"

        return info
    except Exception as e:
        return {"file": str(path), "error": str(e)}


def show_tags(path):
    ext = path.suffix.lower()

    if ext == ".mp3":
        info = show_mp3_tags(path)
    elif ext == ".flac":
        info = show_flac_tags(path)
    elif ext == ".m4a":
        info = show_m4a_tags(path)
    else:
        print(f"[SKIP] 不支持格式: {path}")
        return

    if "error" in info:
        print(f"[ERROR] {info['file']} -> {info['error']}")
        return

    print("=" * 60)
    print(f"文件    : {info.get('file')}")
    print(f"格式    : {info.get('format')}")
    print(f"轨道号  : {info.get('track')}")
    print(f"标题    : {info.get('title')}")
    print(f"艺术家  : {info.get('artist')}")
    print(f"专辑    : {info.get('album')}")
    print(f"简介/注释: {info.get('comment')}")
    print(f"封面    : {info.get('cover')}")
    print("=" * 60)


# ========================
# 分发
# ========================

def write_tags(path, track, title, artists, album, comment, cover, dry_run):
    if dry_run:
        print(f"[DRY RUN] {path}")
        print(f"  track   = {track}")
        print(f"  title   = {title}")
        print(f"  artist  = {artists}")
        print(f"  album   = {album}")
        print(f"  comment = {comment}")
        print(f"  cover   = {cover}")
        return

    ext = path.suffix.lower()

    if ext == ".mp3":
        write_mp3(path, track, title, artists, album, comment, cover)
    elif ext == ".flac":
        write_flac(path, track, title, artists, album, comment, cover)
    elif ext == ".m4a":
        write_m4a(path, track, title, artists, album, comment, cover)
    else:
        print(f"[SKIP] 不支持格式: {path}")


def process_file(path, artists, album, comment, cover, dry_run):
    parsed = parse_filename(path.name)
    if not parsed:
        print(f"[SKIP] {path}")
        return

    track, title = parsed
    write_tags(path, track, title, artists, album, comment, cover, dry_run)


def process_folder(folder, artists, album, comment, cover, dry_run):
    files = list(folder.rglob("*.*"))

    for f in files:
        if f.suffix.lower() not in [".mp3", ".flac", ".m4a"]:
            continue
        process_file(f, artists, album, comment, cover, dry_run)


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
    parser.add_argument("-m", "--comment", help="简介 / 注释")

    parser.add_argument("-u", "--auto", action="store_true",
                        help="自动识别 artist/album/cover（与 -a/-l/-c 互斥）")

    parser.add_argument("--show", action="store_true",
                        help="查看指定音乐文件的 tag（需配合 -f 使用）")

    parser.add_argument("-n", "--dry-run", action="store_true",
                        help="仅预览，不写入标签")
    parser.add_argument("-v", "--version", action="version",
                        version=f"%(prog)s {VERSION}")

    args = parser.parse_args()

    # show 模式只能用于单文件
    if args.show:
        if not args.file:
            parser.error("--show 需要配合 -f/--file 使用")
        path = Path(args.file).resolve()
        ensure_file_exists(path, parser, "音乐文件")
        show_tags(path)
        return

    # 互斥校验
    if args.auto and (args.artist or args.album or args.cover):
        parser.error("-u 与 -a/-l/-c 互斥")
    # comment 不与 auto 互斥，因为它无法自动推断，手动传入很合理

    cover = Path(args.cover).resolve() if args.cover else None
    if cover:
        ensure_file_exists(cover, parser, "封面文件")

    # 单文件
    if args.file:
        path = Path(args.file).resolve()
        ensure_file_exists(path, parser, "音乐文件")

        if args.auto:
            artists, album, cover = infer_auto_tags(path.parent)
        else:
            artists = args.artist
            album = args.album

        process_file(path, artists, album, args.comment, cover, args.dry_run)
        return

    # 目录
    folder = Path(args.dir or ".").resolve()
    ensure_file_exists(folder, parser, "目录")

    if args.auto:
        artists, album, cover = infer_auto_tags(folder)
    else:
        artists = args.artist
        album = args.album

    process_folder(folder, artists, album, args.comment, cover, args.dry_run)


if __name__ == "__main__":
    main()
