# Music Scraper

一个基于文件名的音乐标签刮削工具（MP3 / FLAC / M4A）。

可通过 `-p / --parse-filename` 从文件名中提取：

`音轨号 音乐名.ext`

例如：

`82 龍族の記憶.mp3`

并写入：

- `tracknumber`
- `title`

并支持：

- 多作者 / 艺术家
- 专辑艺术家
- 专辑名
- 年份
- 专辑封面写入
- 简介 / 注释写入
- 自动识别（目录推断）
- 单文件 / 批量处理
- dry-run 预览模式
- 查看指定音乐文件 tag
- 批量查看目录下所有音频文件 tag
- 单文件手动指定 `track`
- 单文件手动指定 `title`
- 将完整文件名作为 `title`
- 提取音乐内嵌封面

---

## 🚀 安装

### 1. 安装依赖

```bash
pip install mutagen
```

### 2. 使用脚本

```bash
python music-scraper.py -h
```

---

## 📦 支持格式

当前支持音频格式：

- `.mp3`
- `.flac`
- `.m4a`

---

## 📦 文件名策略

默认不会从文件名生成 `track/title`。需要时，从以下两个互斥策略中选择一个。

无论是否选择文件名策略，手动提供的 `artist / album_artist / album / year / comment / cover` 都会正常写入。

### 解析“音轨号 + 标题”

使用：

```bash
-p / --parse-filename
```

文件名格式：

`音轨号 空格 标题.ext`

例如：

```text
01 Opening.mp3
82 龍族の記憶.mp3
03 Ending.flac
12 Insert Song.m4a
```

匹配成功后会自动提取：

- `tracknumber`
- `title`

不匹配时不会生成 `track/title`，但不会阻止其他显式标签写入。

### 将文件名作为标题

使用：

```bash
-N / --name-as-title
```

音乐文件名去掉最后的扩展名后，会完整写入 `title`：

```text
精灵森林 III 荒林采药行.mp3
-> title = 精灵森林 III 荒林采药行
```

此策略不会生成 `tracknumber`。

例如，处理前述“凯尔特音乐”目录可使用：

```bash
python music-scraper.py -a "MIA秘境旋律" -l "凯尔特音乐" -d . -N
```

### 不选择文件名策略

可以只写入明确提供的其他标签。例如：

```bash
python music-scraper.py -d ./music -a "作者A" -l "专辑名"
```

这会递归处理目录中的音频，但保持原有 `track/title` 不变。

### 查看 / 提取封面模式说明

在以下模式下，**不要求文件名匹配**：

- `--show`
- `--extract-cover`

只要文件后缀是支持的音频格式，就可以读取标签或提取封面。

---

## 🧪 基本用法

### 🆘 不带参数

```bash
python music-scraper.py
```

等同于 `-h / --help`，打印帮助信息。

### 🎯 当前目录按编号文件名批量处理

```bash
python music-scraper.py -p
```

### 🎯 当前目录以文件名作为标题批量处理

```bash
python music-scraper.py -N
```

### 📁 指定目录

```bash
python music-scraper.py -d ./music -p
```

### 🎵 单个文件

```bash
python music-scraper.py -f "82 龍族の記憶.mp3" -p
```

如果文件名可解析，则自动写入：

- `tracknumber`
- `title`

---

## ✍️ 手动指定信息

### 👤 多作者 / 艺术家

```bash
python music-scraper.py -a "作者A" -a "作者B"
```

对应参数：

```bash
-a / --artist
```

### 👥 专辑艺术家

```bash
python music-scraper.py -A "专辑艺术家"
```

对应参数：

```bash
-A / --album-artist
```

### 💿 专辑

```bash
python music-scraper.py -l "专辑名"
```

对应参数：

```bash
-l / --album
```

### 📅 年份

```bash
python music-scraper.py -y 2024
```

对应参数：

```bash
-y / --year
```

年份要求为 4 位数字，例如：

```text
1999
2004
2024
```

### 🖼 封面写入

```bash
python music-scraper.py -c cover.jpg
```

支持格式：

- `jpg` / `jpeg`
- `png`
- `webp`

### 📝 简介 / 注释

```bash
python music-scraper.py -m "这是一段歌曲简介"
```

可与其他参数组合使用：

```bash
python music-scraper.py -f "01 Opening.flac" -a "作者A" -A "专辑艺术家" -l "专辑名" -y 2024 -m "这是一首开场曲"
```

不同音频格式中，“简介 / 注释”对应的标签字段不同：

- MP3：`COMM`
- FLAC：`comment`
- M4A：`©cmt`

因此不同播放器里可能显示为“注释”“评论”或“简介”。

---

## 🏷 标签字段对应关系

| 信息 | MP3 | FLAC | M4A |
|---|---|---|---|
| 音轨号 | `tracknumber` | `tracknumber` | `trkn` |
| 标题 | `title` | `title` | `©nam` |
| 艺术家 | `artist` | `artist` | `©ART` |
| 专辑艺术家 | `albumartist` | `albumartist` | `aART` |
| 专辑 | `album` | `album` | `©alb` |
| 年份 | `date` | `date` | `©day` |
| 简介 / 注释 | `COMM` | `comment` | `©cmt` |
| 封面 | `APIC` | `Picture` | `covr` |

---

## 🎵 单文件手动指定 track / title

这两个参数**仅单文件模式可用**：

- `-t / --track`：手动指定音轨号
- `-s / --title`：手动指定标题

### 文件名可匹配时

```bash
python music-scraper.py -f "01 Opening.flac" -p
```

会自动提取：

- `track = 1`
- `title = Opening`

### 文件名不可匹配时，手动指定

```bash
python music-scraper.py -f "Opening Final Ver.flac" -t 1 -s "Opening"
```

这时不会跳过，而是使用你手动指定的值。

### 文件名不可匹配，但只写其他标签

```bash
python music-scraper.py -f "Opening Final Ver.flac" -a "作者A" -A "专辑艺术家" -l "专辑名" -y 2024 -m "简介"
```

这时也不会跳过，会正常写入：

- `artist`
- `album_artist`
- `album`
- `year`
- `comment`

但不会写入 `track/title`。

---

## 🔗 组合使用

```bash
python music-scraper.py -d ./music -N -a "A" -a "B" -A "专辑艺术家" -l "专辑名" -y 2024 -c cover.jpg -m "整张专辑统一简介"
```

单文件组合示例：

```bash
python music-scraper.py -f "My Song.flac" -t 7 -s "正式标题" -a "A" -a "B" -A "专辑艺术家" -l "专辑名" -y 2024 -c cover.jpg -m "歌曲说明"
```

---

## 🤖 自动模式（推荐）

```bash
python music-scraper.py -u
```

该命令只自动推断 `artist / album_artist / album / cover`。如需同时从文件名生成标签，请组合 `-p` 或 `-N`：

```bash
python music-scraper.py -d ./music -u -p
python music-scraper.py -f "xxx.mp3" -u -N
```

### 自动识别规则

| 项目 | 来源 |
|---|---|
| `album` | 当前目录名 |
| `artist` | 父目录名 |
| `album_artist` | 父目录名 |
| `cover` | 自动查找封面文件 |

说明：

- 自动模式会自动推断 `artist / album_artist / album / cover`
- `year` 不参与自动推断，如需写入年份，请手动使用 `-y`
- `comment` 不参与自动推断，如需写入简介，请手动使用 `-m`
- 自动模式本身不会从文件名生成 `track/title`
- 可使用 `-p` 解析编号和标题，或使用 `-N` 将文件名作为标题
- 单文件模式下，若你同时手动传了 `-t/-s`，则以手动指定为准

例如：

```bash
python music-scraper.py -d ./music -u -N -y 2024 -m "自动模式下补充简介"
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
python music-scraper.py -N -n
```

或：

```bash
python music-scraper.py -u -p -n
```

输出中会显示将要写入的：

- `track`
- `title`
- `artist`
- `album_artist`
- `album`
- `year`
- `comment`
- `cover`

---

## 🏷 查看 tag

### 查看单个文件

```bash
python music-scraper.py -f "01 Opening.flac" --show
```

### 批量查看指定目录下所有音频文件

```bash
python music-scraper.py -d ./music --show
```

### 批量查看当前目录下所有音频文件

```bash
python music-scraper.py --show
```

说明：

- `--show` 模式下不要求文件名匹配规则
- 只要后缀是支持的音频文件即可：

  - `.mp3`
  - `.flac`
  - `.m4a`

- `-f` 时查看单文件
- `-d` 时查看目录
- 不带 `-d/-f` 时默认查看当前目录
- 目录查看会递归扫描子目录中的音频文件

示例输出：

```text
============================================================
文件       : /path/to/01 Opening.flac
格式       : FLAC
轨道号     : 1
标题       : Opening
艺术家     : 作者A; 作者B
专辑艺术家 : 专辑艺术家
专辑       : 专辑名
年份       : 2024
简介/注释  : 这是一首开场曲
封面       : 有 (1 张)
============================================================
```

---

## 🖼 提取音乐封面

### 提取单个文件封面

```bash
python music-scraper.py -f "01 Opening.flac" --extract-cover
```

默认输出到音频同目录，命名为：

```text
原文件名.cover.扩展名
```

例如：

```text
01 Opening.flac -> 01 Opening.cover.jpg
```

### 提取单个文件封面到指定路径

```bash
python music-scraper.py -f "01 Opening.flac" --extract-cover "./covers/opening.jpg"
```

### 批量提取指定目录下所有音频文件封面

```bash
python music-scraper.py -d ./music --extract-cover
```

### 批量提取当前目录下所有音频文件封面

```bash
python music-scraper.py --extract-cover
```

### 批量提取到指定目录

```bash
python music-scraper.py -d ./music --extract-cover ./covers
```

说明：

- `--extract-cover` 模式下不要求文件名匹配规则
- 只要后缀是支持的音频文件即可：

  - `.mp3`
  - `.flac`
  - `.m4a`

- 若音频没有内嵌封面，会跳过
- `-f` 时可指定输出文件路径
- `-d` 时可指定输出目录
- 不带 `-d/-f` 时默认处理当前目录
- 目录模式会递归扫描子目录中的音频文件

---

## ❗ 参数互斥说明

### 文件名策略

以下两个参数互斥，不能同时使用：

- `--parse-filename / -p`
- `--name-as-title / -N`

它们可以与 `--auto`、显式标签参数和 `--dry-run` 等适用参数组合使用。

### `--auto / -u` 与以下参数不能同时使用：

- `--artist / -a`
- `--album-artist / -A`
- `--album / -l`
- `--cover / -c`

说明：

- `--year / -y` **可以** 与 `--auto / -u` 同时使用
- `--comment / -m` **可以** 与 `--auto / -u` 同时使用
- 因为 `year/comment` 不会自动推断，手动指定是合理的

### `--track / -t` 与 `--title / -s`

这两个参数：

- **仅能配合 `-f / --file` 使用**
- 不能用于目录批量模式

---

## 🆘 帮助

```bash
python music-scraper.py -h
```

不带任何参数也会显示相同的帮助信息。

---

## 🔢 版本

```bash
python music-scraper.py -v
```

---

## ⚠️ 注意事项

- 支持 `.mp3` / `.flac` / `.m4a`
- 默认不会根据文件名改写 `track/title`
- 使用 `-p` 时，只有符合“数字 + 空格 + 标题”的文件名才能生成 `track/title`
- 使用 `-N` 时，文件名去掉后缀后会完整写入 `title`
- 两种文件名策略都不会阻止其他显式标签写入
- `--show` 模式下完全不检查文件名格式
- `--extract-cover` 模式下完全不检查文件名格式
- 封面写入会覆盖原有封面
- MP3 的注释会写入 `COMM`
- 年份要求为 4 位数字
- 不同播放器对“注释 / 简介”“专辑艺术家”“年份”等字段的显示方式可能不同
- 提取封面时，若文件本身没有内嵌封面，会跳过
- 建议先使用 `-n` 预览

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
python music-scraper.py -u -p
```

效果：

- `artist = 久石让`
- `album_artist = 久石让`
- `album = 龙族 OST`
- 自动写入封面
- 自动写入 `track + title`

如果再加上年份和简介：

```bash
python music-scraper.py -u -p -y 2024 -m "龙族 OST 原声集"
```

则还会写入：

- `year = 2024`
- `comment = 龙族 OST 原声集`

---

## 💡 单文件示例

### 示例 1：文件名可解析

```bash
python music-scraper.py -f "07 Ending.flac" -p
```

会自动写入：

- `track = 7`
- `title = Ending`

### 示例 2：文件名不可解析，手动补充

```bash
python music-scraper.py -f "Ending Final Version.flac" -t 7 -s "Ending"
```

会写入：

- `track = 7`
- `title = Ending`

### 示例 3：文件名不可解析，只写其他标签

```bash
python music-scraper.py -f "Ending Final Version.flac" -a "作者A" -A "专辑艺术家" -l "专辑名" -y 2024 -m "结尾曲"
```

会写入：

- `artist = 作者A`
- `album_artist = 专辑艺术家`
- `album = 专辑名`
- `year = 2024`
- `comment = 结尾曲`

### 示例 4：直接查看当前目录所有音频标签

```bash
python music-scraper.py --show
```

### 示例 5：直接提取当前目录所有音频封面

```bash
python music-scraper.py --extract-cover
```

---

## 📌 TODO（可扩展）

- 自动识别多种文件名格式（`01-xxx` / `01.xxx` / `01_xxx`）
- 自动拆分作者（`A,B,C`）
- 从网络刮削元数据（MusicBrainz）
- 导出 tag 信息为文本或 CSV
