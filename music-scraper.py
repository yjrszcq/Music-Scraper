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

VERSION = "2.7.0"

SUPPORTED_EXTS = [".mp3", ".flac", ".m4a"]

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


def mime_to_ext(mime: str):
    mapping = {
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }
    return mapping.get((mime or "").lower(), ".bin")


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
    album_artist = artist

    return artists, album_artist, album, cover


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


def normalize_track(track):
    if track is None:
        return None
    s = str(track).strip()
    if not s:
        return None
    if not s.isdigit():
        raise ValueError(f"track 必须是纯数字，当前为: {track}")
    return str(int(s))


def normalize_year(year):
    if year is None:
        return None
    s = str(year).strip()
    if not s:
        return None
    if not re.fullmatch(r"\d{4}", s):
        raise ValueError(f"年份必须是 4 位数字，当前为: {year}")
    return s


def is_supported_audio(path: Path):
    return path.suffix.lower() in SUPPORTED_EXTS


def iter_audio_files(folder: Path):
    for f in sorted(folder.rglob("*")):
        if f.is_file() and is_supported_audio(f):
            yield f


# ========================
# 封面提取
# ========================

def get_mp3_cover(path: Path):
    try:
        tags = ID3(path)
        apics = tags.getall("APIC")
        if not apics:
            return None
        pic = apics[0]
        return {
            "data": pic.data,
            "mime": pic.mime or "image/jpeg",
        }
    except Exception as e:
        return {"error": str(e)}


def get_flac_cover(path: Path):
    try:
        audio = FLAC(path)
        if not audio.pictures:
            return None
        pic = audio.pictures[0]
        return {
            "data": pic.data,
            "mime": pic.mime or "image/jpeg",
        }
    except Exception as e:
        return {"error": str(e)}


def get_m4a_cover(path: Path):
    try:
        audio = MP4(path)
        covr = audio.get("covr")
        if not covr:
            return None

        item = covr[0]
        data = bytes(item)

        fmt = getattr(item, "imageformat", None)
        if fmt == MP4Cover.FORMAT_PNG:
            mime = "image/png"
        else:
            mime = "image/jpeg"

        return {
            "data": data,
            "mime": mime,
        }
    except Exception as e:
        return {"error": str(e)}


def get_cover_data(path: Path):
    ext = path.suffix.lower()

    if ext == ".mp3":
        return get_mp3_cover(path)
    elif ext == ".flac":
        return get_flac_cover(path)
    elif ext == ".m4a":
        return get_m4a_cover(path)
    else:
        return {"error": f"不支持格式: {path.suffix}"}


def build_default_cover_output_path(audio_path: Path, mime: str):
    ext = mime_to_ext(mime)
    return audio_path.with_name(f"{audio_path.stem}.cover{ext}")


def resolve_cover_output_path(audio_path: Path, cover_info: dict, output_arg: str | None, single_file: bool):
    ext = mime_to_ext(cover_info["mime"])

    if not output_arg:
        return build_default_cover_output_path(audio_path, cover_info["mime"])

    out = Path(output_arg).resolve()

    if single_file:
        if out.exists() and out.is_dir():
            return out / f"{audio_path.stem}.cover{ext}"
        return out

    # 目录模式：指定路径按目录处理
    if out.exists() and out.is_file():
        raise ValueError(f"目录批量提取时，--extract-cover 不能是文件路径: {out}")

    return out / f"{audio_path.stem}.cover{ext}"


def extract_cover_from_file(audio_path: Path, output_arg: str | None = None, single_file: bool = True):
    info = get_cover_data(audio_path)

    if info is None:
        print(f"[SKIP] {audio_path} -> 没有封面")
        return

    if "error" in info:
        print(f"[ERROR] {audio_path} -> {info['error']}")
        return

    try:
        out_path = resolve_cover_output_path(audio_path, info, output_arg, single_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(info["data"])
        print(f"[OK] {audio_path} -> {out_path}")
    except Exception as e:
        print(f"[ERROR] {audio_path} -> {e}")


def extract_cover_from_folder(folder: Path, output_arg: str | None = None):
    files = list(iter_audio_files(folder))

    if not files:
        print(f"[INFO] 目录下未找到支持的音频文件: {folder}")
        return

    for f in files:
        extract_cover_from_file(f, output_arg=output_arg, single_file=False)


# ========================
# 写入不同格式
# ========================

def write_mp3(path, track, title, artists, album_artist, album, year, comment, cover):
    try:
        try:
            audio = EasyID3(path)
        except ID3NoHeaderError:
            audio = EasyID3()
            audio.save(path)
            audio = EasyID3(path)

        if track is not None:
            audio["tracknumber"] = [track]
        if title is not None:
            audio["title"] = [title]

        if artists:
            audio["artist"] = artists
        if album_artist:
            audio["albumartist"] = [album_artist]
        if album:
            audio["album"] = [album]
        if year:
            audio["date"] = [year]

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


def write_flac(path, track, title, artists, album_artist, album, year, comment, cover):
    try:
        audio = FLAC(path)

        if track is not None:
            audio["tracknumber"] = track
        if title is not None:
            audio["title"] = title

        if artists:
            audio["artist"] = artists
        if album_artist:
            audio["albumartist"] = album_artist
        if album:
            audio["album"] = album
        if year:
            audio["date"] = year
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


def write_m4a(path, track, title, artists, album_artist, album, year, comment, cover):
    try:
        audio = MP4(path)

        if track is not None:
            audio["trkn"] = [(int(track), 0)]
        if title is not None:
            audio["©nam"] = [title]

        if artists:
            audio["©ART"] = artists
        if album_artist:
            audio["aART"] = [album_artist]
        if album:
            audio["©alb"] = [album]
        if year:
            audio["©day"] = [year]
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
            "album_artist": None,
            "album": None,
            "year": None,
            "comment": None,
            "cover": "无",
        }

        try:
            audio = EasyID3(path)
            info["track"] = flatten_value(audio.get("tracknumber"))
            info["title"] = flatten_value(audio.get("title"))
            info["artist"] = flatten_value(audio.get("artist"))
            info["album_artist"] = flatten_value(audio.get("albumartist"))
            info["album"] = flatten_value(audio.get("album"))
            info["year"] = flatten_value(audio.get("date"))
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
            "album_artist": flatten_value(audio.get("albumartist")),
            "album": flatten_value(audio.get("album")),
            "year": flatten_value(audio.get("date")),
            "comment": flatten_value(audio.get("comment")),
            "cover": "无",
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
            "album_artist": flatten_value(audio.get("aART")),
            "album": flatten_value(audio.get("©alb")),
            "year": flatten_value(audio.get("©day")),
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


def read_tags(path):
    ext = path.suffix.lower()

    if ext == ".mp3":
        return show_mp3_tags(path)
    elif ext == ".flac":
        return show_flac_tags(path)
    elif ext == ".m4a":
        return show_m4a_tags(path)
    else:
        return {"file": str(path), "error": f"不支持格式: {path.suffix}"}


def print_tag_info(info):
    if "error" in info:
        print(f"[ERROR] {info['file']} -> {info['error']}")
        return

    print("=" * 60)
    print(f"文件       : {info.get('file')}")
    print(f"格式       : {info.get('format')}")
    print(f"轨道号     : {info.get('track')}")
    print(f"标题       : {info.get('title')}")
    print(f"艺术家     : {info.get('artist')}")
    print(f"专辑艺术家 : {info.get('album_artist')}")
    print(f"专辑       : {info.get('album')}")
    print(f"年份       : {info.get('year')}")
    print(f"简介/注释  : {info.get('comment')}")
    print(f"封面       : {info.get('cover')}")
    print("=" * 60)


def show_tags(path):
    info = read_tags(path)
    print_tag_info(info)


def show_folder_tags(folder: Path):
    files = list(iter_audio_files(folder))

    if not files:
        print(f"[INFO] 目录下未找到支持的音频文件: {folder}")
        return

    for f in files:
        show_tags(f)


# ========================
# 分发
# ========================

def write_tags(path, track, title, artists, album_artist, album, year, comment, cover, dry_run):
    year = normalize_year(year)

    if dry_run:
        print(f"[DRY RUN] {path}")
        print(f"  track        = {track}")
        print(f"  title        = {title}")
        print(f"  artist       = {artists}")
        print(f"  album_artist = {album_artist}")
        print(f"  album        = {album}")
        print(f"  year         = {year}")
        print(f"  comment      = {comment}")
        print(f"  cover        = {cover}")
        return

    ext = path.suffix.lower()

    if ext == ".mp3":
        write_mp3(path, track, title, artists, album_artist, album, year, comment, cover)
    elif ext == ".flac":
        write_flac(path, track, title, artists, album_artist, album, year, comment, cover)
    elif ext == ".m4a":
        write_m4a(path, track, title, artists, album_artist, album, year, comment, cover)
    else:
        print(f"[SKIP] 不支持格式: {path}")


def process_file(
    path,
    artists,
    album_artist,
    album,
    year,
    comment,
    cover,
    dry_run,
    filename_mode=None,
    manual_track=None,
    manual_title=None,
):
    parsed = parse_filename(path.name) if filename_mode == "parse" else None

    if manual_track is not None:
        track = normalize_track(manual_track)
    elif parsed:
        track = parsed[0]
    else:
        track = None

    if manual_title is not None:
        title = manual_title.strip()
    elif filename_mode == "title":
        title = path.stem
    elif parsed:
        title = parsed[1]
    else:
        title = None

    if not any([
        track is not None,
        title is not None,
        artists,
        album_artist,
        album,
        year,
        comment is not None,
        cover
    ]):
        print(f"[SKIP] {path} -> 没有可写入的标签")
        return

    write_tags(path, track, title, artists, album_artist, album, year, comment, cover, dry_run)


def process_folder(folder, artists, album_artist, album, year, comment, cover, dry_run, filename_mode):
    files = list(folder.rglob("*.*"))

    for f in files:
        if f.suffix.lower() not in SUPPORTED_EXTS:
            continue

        process_file(
            path=f,
            artists=artists,
            album_artist=album_artist,
            album=album,
            year=year,
            comment=comment,
            cover=cover,
            dry_run=dry_run,
            filename_mode=filename_mode,
        )


# ========================
# CLI
# ========================

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="音乐标签刮削工具（MP3 / FLAC / M4A）",
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False,
    )

    path_group = parser.add_mutually_exclusive_group()
    filename_group = parser.add_mutually_exclusive_group()

    parser.add_argument("-a", "--artist", action="append", help="作者 / 艺术家（可多个）")
    parser.add_argument("-A", "--album-artist", help="专辑艺术家")
    parser.add_argument("-c", "--cover", help="封面路径")
    path_group.add_argument("-d", "--dir", help="目录")
    path_group.add_argument("-f", "--file", help="单文件")
    parser.add_argument("-h", "--help", action="help", help="显示帮助信息并退出")
    parser.add_argument("-l", "--album", help="专辑")
    parser.add_argument("-m", "--comment", help="简介 / 注释")
    parser.add_argument("-n", "--dry-run", action="store_true", help="仅预览，不写入标签")
    filename_group.add_argument(
        "-N", "--name-as-title", action="store_true",
        help="将不含后缀的完整文件名作为 title"
    )
    filename_group.add_argument(
        "-p", "--parse-filename", action="store_true",
        help="按“01 标题.mp3”格式从文件名提取 track/title"
    )
    parser.add_argument("-s", "--title", help="手动指定标题（仅单文件模式）")
    parser.add_argument(
        "-S", "--show", action="store_true",
        help="查看 tag：-f 为单文件，-d 为目录；都不带则默认当前目录"
    )
    parser.add_argument("-t", "--track", help="手动指定音轨号（仅单文件模式）")
    parser.add_argument(
        "-u", "--auto", action="store_true",
        help="自动识别 artist/album_artist/album/cover（与 -a/-A/-l/-c 互斥）"
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version=f"%(prog)s {VERSION}"
    )
    parser.add_argument(
        "-x", "--extract-cover", nargs="?", const="",
        help="提取封面：-f 时可指定输出文件；-d 时可指定输出目录；不指定则按默认命名输出"
    )
    parser.add_argument("-y", "--year", help="年份，例如 2024")

    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        parser.print_help()
        return

    args = parser.parse_args(argv)

    if args.parse_filename:
        filename_mode = "parse"
    elif args.name_as_title:
        filename_mode = "title"
    else:
        filename_mode = None

    # 提取封面模式
    if args.extract_cover is not None:
        if args.file:
            path = Path(args.file).resolve()
            ensure_file_exists(path, parser, "音乐文件")
            if not path.is_file():
                parser.error(f"不是文件: {path}")
            if not is_supported_audio(path):
                parser.error(f"不支持格式: {path}")
            extract_cover_from_file(path, output_arg=args.extract_cover or None, single_file=True)
            return

        folder = Path(args.dir or ".").resolve()
        ensure_file_exists(folder, parser, "目录")
        if not folder.is_dir():
            parser.error(f"不是目录: {folder}")
        extract_cover_from_folder(folder, output_arg=args.extract_cover or None)
        return

    # show 模式
    if args.show:
        if args.file:
            path = Path(args.file).resolve()
            ensure_file_exists(path, parser, "音乐文件")
            if not path.is_file():
                parser.error(f"不是文件: {path}")
            if not is_supported_audio(path):
                parser.error(f"不支持格式: {path}")
            show_tags(path)
            return

        folder = Path(args.dir or ".").resolve()
        ensure_file_exists(folder, parser, "目录")
        if not folder.is_dir():
            parser.error(f"不是目录: {folder}")
        show_folder_tags(folder)
        return

    # track/title 只能在单文件模式使用
    if (args.track is not None or args.title is not None) and not args.file:
        parser.error("--track/--title 仅能配合 -f/--file 使用")

    # auto 互斥
    if args.auto and (args.artist or args.album_artist or args.album or args.cover):
        parser.error("-u 与 -a/-A/-l/-c 互斥")

    cover = Path(args.cover).resolve() if args.cover else None
    if cover:
        ensure_file_exists(cover, parser, "封面文件")

    try:
        year = normalize_year(args.year)
    except ValueError as e:
        parser.error(str(e))

    # 单文件
    if args.file:
        path = Path(args.file).resolve()
        ensure_file_exists(path, parser, "音乐文件")

        if args.auto:
            artists, album_artist, album, cover = infer_auto_tags(path.parent)
        else:
            artists = args.artist
            album_artist = args.album_artist
            album = args.album

        process_file(
            path=path,
            artists=artists,
            album_artist=album_artist,
            album=album,
            year=year,
            comment=args.comment,
            cover=cover,
            dry_run=args.dry_run,
            filename_mode=filename_mode,
            manual_track=args.track,
            manual_title=args.title,
        )
        return

    # 目录
    folder = Path(args.dir or ".").resolve()
    ensure_file_exists(folder, parser, "目录")

    if args.auto:
        artists, album_artist, album, cover = infer_auto_tags(folder)
    else:
        artists = args.artist
        album_artist = args.album_artist
        album = args.album

    process_folder(
        folder=folder,
        artists=artists,
        album_artist=album_artist,
        album=album,
        year=year,
        comment=args.comment,
        cover=cover,
        dry_run=args.dry_run,
        filename_mode=filename_mode,
    )


if __name__ == "__main__":
    main()
