# Music Scraper

一个基于文件名的音乐标签刮削工具（MP3 / FLAC / M4A），支持：

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
- 从文件名中提取 `track` 和 `title`
- 将完整文件名作为 `title`
- 提取音乐内嵌封面
- 按名称或缩写删除指定标签
- 一次清空全部内嵌标签

---

## 📋 参数对照表

| 短参数 | 长参数 | 值 | 用途 | 备注 |
|---|---|---|---|---|
| `-a` | `--artist` | `ARTIST` | 写入艺术家 | 可重复使用；传入 `""` 删除标签 |
| `-A` | `--album-artist` | `ALBUM_ARTIST` | 写入专辑艺术家 | 传入 `""` 删除标签 |
| `-b` | `--album` | `ALBUM` | 写入专辑名 | 传入 `""` 删除标签 |
| `-c` | `--cover` | `COVER` | 写入封面文件 | 传入 `""` 删除内嵌封面 |
| `-C` | `--comment` | `COMMENT` | 写入简介或注释 | 传入 `""` 删除标签 |
| `-y` | `--year` | `YEAR` | 写入年份 | 必须为 4 位数字；传入 `""` 删除标签 |
| `-T` | `--track` | `TRACK` | 写入音轨号 | 仅单文件模式可用；传入 `""` 删除标签 |
| `-t` | `--title` | `TITLE` | 写入标题 | 仅单文件模式可用；传入 `""` 删除标签 |
| `-d` | `--dir` | `DIR` | 递归处理指定目录 | 与 `-f` 互斥 |
| `-f` | `--file` | `FILE` | 处理指定单个音频文件 | 与 `-d` 互斥 |
| `-n` | `--name-as-title` | 无 | 将完整文件名写入标题 | 自动去除扩展名；与 `-p` 互斥 |
| `-p` | `--parse-filename` | 无 | 从文件名解析音轨号和标题 | 文件名格式为“音轨号 + 空格 + 标题”；与 `-n` 互斥 |
| `-u` | `--auto` | 无 | 根据目录自动推断标签 | 推断艺术家、专辑艺术家、专辑和封面 |
| `-U` | `--unset` | `TAG...` | 删除指定标签 | 缩写必须使用 `@`，例如 `--unset @aAc` |
| `-e` | `--clear` | 无 | 清空全部内嵌标签 | 支持单文件和目录递归处理 |
| `-s` | `--show` | 无 | 查看已有标签 | 未指定 `-d/-f` 时查看当前目录 |
| `-x` | `--extract-cover` | `[OUTPUT_PATH]` | 提取内嵌封面 | 输出路径可省略 |
| `-D` | `--dry-run` | 无 | 预览将要执行的操作 | 不写入文件 |
| `-h` | `--help` | 无 | 显示帮助信息 | 显示后退出 |
| `-v` | `--version` | 无 | 显示版本信息 | 显示后退出 |

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
01 第一首.mp3
02 第二首.mp3
03 第三首.flac
04 第四首.m4a
```

匹配成功后会自动提取：

- `tracknumber`
- `title`

不匹配时不会生成 `track/title`，但不会阻止其他显式标签写入。

### 将文件名作为标题

使用：

```bash
-n / --name-as-title
```

音乐文件名去掉最后的扩展名后，会完整写入 `title`：

```text
示例歌曲.mp3
-> title = 示例歌曲
```

此策略不会生成 `tracknumber`。

例如，处理当前目录可使用：

```bash
python music-scraper.py -a "示例艺术家" -b "示例专辑" -d . -n
```

### 不选择文件名策略

可以只写入明确提供的其他标签。例如：

```bash
python music-scraper.py -d ./music -a "示例艺术家" -b "示例专辑"
```

这会递归处理目录中的音频，但保持原有 `track/title` 不变。

### 查看 / 提取封面模式说明

在以下模式下，**不要求文件名匹配**：

- `-s / --show`
- `-x / --extract-cover`

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
python music-scraper.py -n
```

### 📁 指定目录

```bash
python music-scraper.py -d ./music -p
```

### 🎵 单个文件

```bash
python music-scraper.py -f "02 第二首.mp3" -p
```

如果文件名可解析，则自动写入：

- `tracknumber`
- `title`

---

## ✍️ 手动指定信息

### 👤 多作者 / 艺术家

```bash
python music-scraper.py -a "艺术家一" -a "艺术家二"
```

对应参数：

```bash
-a / --artist
```

### 👥 专辑艺术家

```bash
python music-scraper.py -A "示例专辑艺术家"
```

对应参数：

```bash
-A / --album-artist
```

### 💿 专辑

```bash
python music-scraper.py -b "示例专辑"
```

对应参数：

```bash
-b / --album
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
python music-scraper.py -C "这是一段歌曲简介"
```

可与其他参数组合使用：

```bash
python music-scraper.py -f "01 第一首.flac" -a "示例艺术家" -A "示例专辑艺术家" -b "示例专辑" -y 2024 -C "示例注释"
```

不同音频格式中，“简介 / 注释”对应的标签字段不同：

- MP3：`COMM`
- FLAC：`comment`
- M4A：`©cmt`

因此不同播放器里可能显示为“注释”“评论”或“简介”。

---

## 🗑 删除已有标签

可写参数支持传入空字符串 `""`。空字符串表示删除对应标签；未提供参数时则保留原标签不变。

例如，删除单个文件的标题、年份、注释和封面：

```bash
python music-scraper.py -f "示例歌曲.mp3" -t "" -y "" -C "" -c ""
```

删除目录中所有音频的艺术家、专辑艺术家和专辑标签：

```bash
python music-scraper.py -d ./music -a "" -A "" -b ""
```

支持空值删除的参数：

- `-a / --artist`
- `-A / --album-artist`
- `-b / --album`
- `-y / --year`
- `-C / --comment`
- `-c / --cover`
- `-T / --track`（仅单文件模式）
- `-t / --title`（仅单文件模式）

建议先组合 `-D / --dry-run` 预览。待删除的字段会显示为 `<DELETE>`：

```bash
python music-scraper.py -f "示例歌曲.mp3" -t "" -c "" -D
```

---

## 🗑 按名称删除指定标签

使用 `-U / --unset` 可以一次删除一个或多个指定标签：

```bash
python music-scraper.py -f "示例歌曲.mp3" --unset artist album cover
python music-scraper.py -d ./music -U track title
```

也可以使用带 `@` 前缀的紧凑缩写，字符顺序不限：

```bash
python music-scraper.py -f "示例歌曲.mp3" --unset @aAc
python music-scraper.py -d ./music -U @Tt
```

不带 `@` 前缀的参数只按完整标签名称解析，因此 `--unset aAc` 会报错。完整名称和缩写可以混合使用：

```bash
python music-scraper.py -f "示例歌曲.mp3" --unset artist @Ac
```

缩写映射：

| 缩写 | 标签 |
|---|---|
| `a` | `artist` |
| `A` | `album_artist` |
| `b` | `album` |
| `y` | `year` |
| `C` | `comment` |
| `c` | `cover` |
| `T` | `track` |
| `t` | `title` |

完整名称还支持 `album-artist`、`date` 和 `tracknumber` 别名。目录模式下也可以批量删除 `track/title`。

建议先使用 `-D` 预览，待删除字段会显示为 `<DELETE>`：

```bash
python music-scraper.py -d ./music --unset @aAbc -D
```

`--unset / -U` 不能与具体标签参数、`--auto`、`--clear`、`--show`、`--extract-cover` 或文件名策略同时使用。

---

## 🧹 清空全部标签

使用 `-e / --clear` 可一次清空音频中的全部内嵌标签：

```bash
python music-scraper.py -f "示例歌曲.mp3" --clear
python music-scraper.py -d ./music -e
```

清空范围包括音轨号、标题、艺术家、专辑、年份、注释、封面，以及流派、作曲者等其他现有标签。目录模式会递归处理全部支持的音频文件。

建议先使用 dry-run 预览：

```bash
python music-scraper.py -d ./music --clear -D
```

`--clear / -e` 不能与具体标签参数、`--unset`、`--auto`、`--show`、`--extract-cover` 或文件名策略同时使用。

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

- `-T / --track`：手动指定音轨号
- `-t / --title`：手动指定标题

### 文件名可匹配时

```bash
python music-scraper.py -f "01 第一首.flac" -p
```

会自动提取：

- `track = 1`
- `title = 第一首`

### 文件名不可匹配时，手动指定

```bash
python music-scraper.py -f "未编号歌曲.flac" -T 1 -t "第一首"
```

这时不会跳过，而是使用你手动指定的值。

### 文件名不可匹配，但只写其他标签

```bash
python music-scraper.py -f "未编号歌曲.flac" -a "示例艺术家" -A "示例专辑艺术家" -b "示例专辑" -y 2024 -C "示例注释"
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
python music-scraper.py -d ./music -n -a "艺术家一" -a "艺术家二" -A "示例专辑艺术家" -b "示例专辑" -y 2024 -c cover.jpg -C "示例注释"
```

单文件组合示例：

```bash
python music-scraper.py -f "示例歌曲.flac" -T 7 -t "示例标题" -a "艺术家一" -a "艺术家二" -A "示例专辑艺术家" -b "示例专辑" -y 2024 -c cover.jpg -C "示例注释"
```

---

## 🤖 自动模式（推荐）

```bash
python music-scraper.py -u
```

该命令只自动推断 `artist / album_artist / album / cover`。如需同时从文件名生成标签，请组合 `-p` 或 `-n`：

```bash
python music-scraper.py -d ./music -u -p
python music-scraper.py -f "xxx.mp3" -u -n
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
- `comment` 不参与自动推断，如需写入简介，请手动使用 `-C`
- 自动模式本身不会从文件名生成 `track/title`
- 可使用 `-p` 解析编号和标题，或使用 `-n` 将文件名作为标题
- 单文件模式下，若你同时手动传了 `-T/-t`，则以手动指定为准

例如：

```bash
python music-scraper.py -d ./music -u -n -y 2024 -C "自动模式下补充简介"
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
python music-scraper.py -n -D
```

或：

```bash
python music-scraper.py -u -p -D
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

对应参数：`-s / --show`

### 查看单个文件

```bash
python music-scraper.py -f "01 第一首.flac" -s
```

### 批量查看指定目录下所有音频文件

```bash
python music-scraper.py -d ./music --show
```

### 批量查看当前目录下所有音频文件

```bash
python music-scraper.py -s
```

说明：

- `-s / --show` 模式下不要求文件名匹配规则
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
文件       : /path/to/01 第一首.flac
格式       : FLAC
轨道号     : 1
标题       : 第一首
艺术家     : 艺术家一; 艺术家二
专辑艺术家 : 示例专辑艺术家
专辑       : 示例专辑
年份       : 2024
简介/注释  : 示例注释
封面       : 有 (1 张)
============================================================
```

---

## 🖼 提取音乐封面

对应参数：`-x / --extract-cover`

### 提取单个文件封面

```bash
python music-scraper.py -f "01 第一首.flac" -x
```

默认输出到音频同目录，命名为：

```text
原文件名.cover.扩展名
```

例如：

```text
01 第一首.flac -> 01 第一首.cover.jpg
```

### 提取单个文件封面到指定路径

```bash
python music-scraper.py -f "01 第一首.flac" --extract-cover "./covers/first.jpg"
```

### 批量提取指定目录下所有音频文件封面

```bash
python music-scraper.py -d ./music -x
```

### 批量提取当前目录下所有音频文件封面

```bash
python music-scraper.py --extract-cover
```

### 批量提取到指定目录

```bash
python music-scraper.py -d ./music -x ./covers
```

说明：

- `-x / --extract-cover` 模式下不要求文件名匹配规则
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
- `--name-as-title / -n`

它们可以与 `--auto`、显式标签参数和 `--dry-run` 等适用参数组合使用。

### `--auto / -u` 与以下参数不能同时使用：

- `--artist / -a`
- `--album-artist / -A`
- `--album / -b`
- `--cover / -c`

说明：

- `--year / -y` **可以** 与 `--auto / -u` 同时使用
- `--comment / -C` **可以** 与 `--auto / -u` 同时使用
- 因为 `year/comment` 不会自动推断，手动指定是合理的

### `--track / -T` 与 `--title / -t`

这两个参数：

- **仅能配合 `-f / --file` 使用**
- 不能用于目录批量模式

### `--clear / -e`

清空模式不能与指定标签删除、其他标签、自动识别、查看标签、提取封面或文件名策略参数同时使用。

### `--unset / -U`

指定标签删除模式不能与具体标签参数、自动识别、清空、查看标签、提取封面或文件名策略参数同时使用。

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
- 使用 `-n` 时，文件名去掉后缀后会完整写入 `title`
- 两种文件名策略都不会阻止其他显式标签写入
- `-s / --show` 模式下完全不检查文件名格式
- `-x / --extract-cover` 模式下完全不检查文件名格式
- 封面写入会覆盖原有封面
- 可写参数传入 `""` 时会删除对应标签；未提供参数时保持原标签不变
- `-U / --unset` 可按完整名称或紧凑缩写删除指定标签
- `-e / --clear` 会清空音频中的全部内嵌标签，建议先配合 `-D` 预览
- MP3 的注释会写入 `COMM`
- 年份要求为 4 位数字
- 不同播放器对“注释 / 简介”“专辑艺术家”“年份”等字段的显示方式可能不同
- 提取封面时，若文件本身没有内嵌封面，会跳过
- 建议先使用 `-D` 预览

---

## 💡 示例目录结构（推荐）

```text
示例艺术家/
└── 示例专辑/
    ├── cover.jpg
    ├── 01 第一首.mp3
    ├── 02 第二首.flac
    └── 03 第三首.m4a
```

运行：

```bash
python music-scraper.py -u -p
```

效果：

- `artist = 示例艺术家`
- `album_artist = 示例艺术家`
- `album = 示例专辑`
- 自动写入封面
- 自动写入 `track + title`

如果再加上年份和简介：

```bash
python music-scraper.py -u -p -y 2024 -C "示例注释"
```

则还会写入：

- `year = 2024`
- `comment = 示例注释`

---

## 💡 单文件示例

### 示例 1：文件名可解析

```bash
python music-scraper.py -f "07 第七首.flac" -p
```

会自动写入：

- `track = 7`
- `title = 第七首`

### 示例 2：文件名不可解析，手动补充

```bash
python music-scraper.py -f "未编号歌曲.flac" -T 7 -t "第七首"
```

会写入：

- `track = 7`
- `title = 第七首`

### 示例 3：文件名不可解析，只写其他标签

```bash
python music-scraper.py -f "未编号歌曲.flac" -a "示例艺术家" -A "示例专辑艺术家" -b "示例专辑" -y 2024 -C "示例注释"
```

会写入：

- `artist = 示例艺术家`
- `album_artist = 示例专辑艺术家`
- `album = 示例专辑`
- `year = 2024`
- `comment = 示例注释`

### 示例 4：直接查看当前目录所有音频标签

```bash
python music-scraper.py -s
```

### 示例 5：直接提取当前目录所有音频封面

```bash
python music-scraper.py -x
```

---

## 📌 TODO（可扩展）

- 自动识别多种文件名格式（`01-xxx` / `01.xxx` / `01_xxx`）
- 自动拆分作者（`A,B,C`）
- 从网络刮削元数据（MusicBrainz）
- 导出 tag 信息为文本或 CSV
