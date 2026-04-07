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
- 单文件手动指定 `track`
- 单文件手动指定 `title`

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

## 📦 支持格式

当前支持音频格式：

* `.mp3`
* `.flac`
* `.m4a`

---

## 📦 文件名格式

### 目录批量模式要求

目录模式下，文件名必须符合：

`音轨号 空格 标题.ext`

例如：

```text
01 Opening.mp3
82 龍族の記憶.mp3
03 Ending.flac
12 Insert Song.m4a
```

匹配成功后会自动提取：

* `tracknumber`
* `title`

### 单文件模式说明

单文件模式下，**不强制要求文件名匹配该格式**：

* 如果文件名能匹配，就自动提取 `track/title`
* 如果文件名不能匹配，也**不会跳过**
* 这时你仍然可以：

  * 手动指定 `track`
  * 手动指定 `title`
  * 或只写入其他标签（如 `artist / album / comment / cover`）

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

如果文件名可解析，则自动写入：

* `tracknumber`
* `title`

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

不同音频格式中，“简介 / 注释”对应的标签字段不同：

* MP3：`COMM`
* FLAC：`comment`
* M4A：`©cmt`

因此不同播放器里可能显示为“注释”“评论”或“简介”。

---

## 🎵 单文件手动指定 track / title

这两个参数**仅单文件模式可用**：

* `-t / --track`：手动指定音轨号
* `-s / --title`：手动指定标题

### 文件名可匹配时

```bash
python music-scraper.py -f "01 Opening.flac"
```

会自动提取：

* `track = 1`
* `title = Opening`

### 文件名不可匹配时，手动指定

```bash
python music-scraper.py -f "Opening Final Ver.flac" -t 1 -s "Opening"
```

这时不会跳过，而是使用你手动指定的值。

### 文件名不可匹配，但只写其他标签

```bash
python music-scraper.py -f "Opening Final Ver.flac" -a "作者A" -l "专辑名" -m "简介"
```

这时也不会跳过，会正常写入：

* `artist`
* `album`
* `comment`

但不会写入 `track/title`。

---

## 🔗 组合使用

```bash
python music-scraper.py -d ./music -a "A" -a "B" -l "专辑名" -c cover.jpg -m "整张专辑统一简介"
```

单文件组合示例：

```bash
python music-scraper.py -f "My Song.flac" -t 7 -s "正式标题" -a "A" -a "B" -l "专辑名" -c cover.jpg -m "歌曲说明"
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
* 单文件模式下，若文件名可解析，仍会自动提取 `track/title`
* 单文件模式下，若你同时手动传了 `-t/-s`，则以手动指定为准

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
文件     : /path/to/01 Opening.flac
格式     : FLAC
轨道号   : 1
标题     : Opening
艺术家   : 作者A; 作者B
专辑     : 专辑名
简介/注释: 这是一首开场曲
封面     : 有 (1 张)
============================================================
```

说明：

* `--show` 需要配合 `-f / --file` 使用
* 当前仅支持查看单个文件，不支持整个目录批量显示

---

## ❗ 参数互斥说明

### `--auto / -u` 与以下参数不能同时使用：

* `--artist / -a`
* `--album / -l`
* `--cover / -c`

说明：

* `--comment / -m` **可以** 与 `--auto / -u` 同时使用
* 因为 `comment` 不会自动推断，手动指定是合理的

### `--track / -t` 与 `--title / -s`

这两个参数：

* **仅能配合 `-f / --file` 使用**
* 不能用于目录批量模式

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

* 支持 `.mp3` / `.flac` / `.m4a`
* 目录模式下，文件名必须符合规则，否则跳过
* 单文件模式下，文件名不符合规则也不会自动跳过
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

## 💡 单文件示例

### 示例 1：文件名可解析

```bash
python music-scraper.py -f "07 Ending.flac"
```

会自动写入：

* `track = 7`
* `title = Ending`

### 示例 2：文件名不可解析，手动补充

```bash
python music-scraper.py -f "Ending Final Version.flac" -t 7 -s "Ending"
```

会写入：

* `track = 7`
* `title = Ending`

### 示例 3：文件名不可解析，只写其他标签

```bash
python music-scraper.py -f "Ending Final Version.flac" -a "作者A" -l "专辑名" -m "结尾曲"
```

会写入：

* `artist = 作者A`
* `album = 专辑名`
* `comment = 结尾曲`

---

## 📌 TODO（可扩展）

* 自动识别多种文件名格式（`01-xxx` / `01.xxx` / `01_xxx`）
* 自动拆分作者（`A,B,C`）
* 从网络刮削元数据（MusicBrainz）
* 批量查看目录下所有音频文件 tag

```
