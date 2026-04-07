# Music Scraper

一个基于文件名的音乐标签刮削工具（MP3 / FLAC / M4A）。

支持从文件名中提取：

`音轨号 音乐名.ext`

例如：

`82 龍族の記憶.mp3`

自动写入：

- `tracknumber`
- `title`

并支持：

- 多作者
- 专辑名
- 专辑封面
- 简介 / 注释
- 自动识别（目录推断）
- 单文件 / 批量处理
- dry-run 预览模式
- 查看指定音乐文件 tag

---

## 🚀 安装

### 1. 安装依赖

```bash
pip install mutagen
````

### 2. 使用脚本

```bash
python music-scraper.py
```

---

## 📦 文件名格式

必须符合：

`音轨号 空格 标题.ext`

例如：

```text
01 Opening.mp3
82 龍族の記憶.mp3
03 Ending.flac
12 Insert Song.m4a
```

当前支持扩展名：

* `.mp3`
* `.flac`
* `.m4a`

---

## 🧪 基本用法

### 🎯 当前目录批量处理

```bash
python music-scraper.py
```

---

### 📁 指定目录

```bash
python music-scraper.py -d ./music
```

---

### 🎵 单个文件

```bash
python music-scraper.py -f "82 龍族の記憶.mp3"
```

---

## ✍️ 手动指定信息

### 👤 多作者

```bash
python music-scraper.py -a "作者A" -a "作者B"
```

---

### 💿 专辑

```bash
python music-scraper.py -l "专辑名"
```

---

### 🖼 封面

```bash
python music-scraper.py -c cover.jpg
```

支持格式：

* `jpg` / `jpeg`
* `png`
* `webp`

---

### 📝 简介 / 注释

```bash
python music-scraper.py -m "这是一段歌曲简介"
```

可与其他参数组合使用：

```bash
python music-scraper.py -f "01 Opening.flac" -a "作者A" -l "专辑名" -m "这是一首开场曲"
```

说明：

不同音频格式中，“简介 / 注释”对应的标签字段不同：

* MP3：`COMM`
* FLAC：`comment`
* M4A：`©cmt`

因此不同播放器里可能显示为“注释”“评论”或“简介”。

---

### 🔗 组合使用

```bash
python music-scraper.py -d ./music -a "A" -a "B" -l "专辑名" -c cover.jpg -m "整张专辑统一简介"
```

---

## 🤖 自动模式（推荐）

```bash
python music-scraper.py -u
```

或：

```bash
python music-scraper.py -d ./music -u
python music-scraper.py -f "xxx.mp3" -u
```

### 自动识别规则

| 项目     | 来源       |
| ------ | -------- |
| album  | 当前目录名    |
| artist | 父目录名     |
| cover  | 自动查找封面文件 |

说明：

* 自动模式会自动推断 `artist / album / cover`
* `comment` 不参与自动推断，如需写入简介，请手动使用 `-m`

例如：

```bash
python music-scraper.py -d ./music -u -m "自动模式下补充简介"
```

---

## 🖼 自动封面文件名

按顺序查找：

```text
cover.jpg / cover.jpeg / cover.png / cover.webp
folder.jpg / folder.jpeg / folder.png / folder.webp
front.jpg / front.jpeg / front.png / front.webp
```

---

## 🔍 预览模式

不会写入，仅打印：

```bash
python music-scraper.py -n
```

或：

```bash
python music-scraper.py -u -n
```

输出中会显示将要写入的：

* `track`
* `title`
* `artist`
* `album`
* `comment`
* `cover`

---

## 🏷 查看指定音乐文件的 tag

可以查看某个音乐文件当前已有的标签信息：

```bash
python music-scraper.py -f "01 Opening.flac" --show
```

示例输出：

```text
============================================================
文件    : /path/to/01 Opening.flac
格式    : FLAC
轨道号  : 1
标题    : Opening
艺术家  : 作者A; 作者B
专辑    : 专辑名
简介/注释: 这是一首开场曲
封面    : 有 (1 张)
============================================================
```

说明：

* `--show` 需要配合 `-f / --file` 使用
* 目前仅支持查看单个文件，不支持整个目录批量显示

---

## ❗ 参数互斥说明

`--auto / -u` 与以下参数不能同时使用：

* `--artist / -a`
* `--album / -l`
* `--cover / -c`

说明：

* `--comment / -m` **可以** 与 `--auto / -u` 同时使用
* 因为 comment 不会自动推断，手动指定是合理的

---

## 🆘 帮助

```bash
python music-scraper.py -h
```

---

## 🔢 版本

```bash
python music-scraper.py -v
```

---

## ⚠️ 注意事项

* 仅支持 `.mp3` / `.flac` / `.m4a`
* 文件名必须符合规则，否则跳过
* 封面会覆盖原有封面
* MP3 的注释会写入 `COMM`
* 不同播放器对“注释 / 简介”字段的显示方式可能不同
* 建议先使用 `-n` 预览

---

## 💡 示例目录结构（推荐）

```text
久石让/
└── 龙族 OST/
    ├── cover.jpg
    ├── 01 Opening.mp3
    ├── 02 Theme.flac
    └── 82 龍族の記憶.m4a
```

运行：

```bash
python music-scraper.py -u
```

效果：

* `artist = 久石让`
* `album = 龙族 OST`
* 自动写入封面
* 自动写入 `track + title`

如果再加上简介：

```bash
python music-scraper.py -u -m "龙族 OST 原声集"
```

则还会写入：

* `comment = 龙族 OST 原声集`

---

## 📌 TODO（可扩展）

* 自动识别多种文件名格式（`01-xxx` / `01.xxx` / `01_xxx`）
* 自动拆分作者（`A,B,C`）
* 从网络刮削元数据（MusicBrainz）
* 批量查看目录下所有音频文件 tag
