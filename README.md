# Music Scraper

一个基于文件名的音乐标签刮削工具（MP3 / FLAC / M4A）。

支持从文件名中提取：

`音轨号 音乐名.mp3`

例如：

`82 龍族の記憶.mp3`

自动写入：

- `tracknumber`
- `title`

并支持：

- 多作者
- 专辑名
- 专辑封面
- 自动识别（目录推断）
- 单文件 / 批量处理
- dry-run 预览模式

---

## 🚀 安装

### 1. 安装依赖

```bash
pip install mutagen
```

### 2. 使用脚本

```bash
python music-scraper.py
```

---

## 📦 文件名格式

必须符合：

`音轨号 空格 标题.mp3`

例如：

```text
01 Opening.mp3
82 龍族の記憶.mp3
```

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

- `jpg` / `jpeg`
- `png`
- `webp`

---

### 🔗 组合使用

```bash
python music-scraper.py -d ./music -a "A" -a "B" -l "专辑名" -c cover.jpg
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

| 项目 | 来源 |
|------|------|
| album | 当前目录名 |
| artist | 父目录名 |
| cover | 自动查找封面文件 |

---

## 🖼 自动封面文件名

按顺序查找：

```text
cover.jpg / cover.png / cover.webp
folder.jpg / folder.png / folder.webp
front.jpg / front.png / front.webp
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

---

## ❗ 参数互斥说明

`--auto / -u` 与以下参数不能同时使用：

- `--artist / -a`
- `--album / -l`
- `--cover / -c`

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

- 仅支持 `.mp3`
- 文件名必须符合规则，否则跳过
- 封面会覆盖原有封面
- 建议先使用 `-n` 预览

---

## 💡 示例目录结构（推荐）

```text
久石让/
└── 龙族 OST/
    ├── cover.jpg
    ├── 01 Opening.mp3
    ├── 02 Theme.mp3
    └── 82 龍族の記憶.mp3
```

运行：

```bash
python music-scraper.py -u
```

效果：

- `artist = 久石让`
- `album = 龙族 OST`
- 自动写入封面
- 自动写入 `track + title`

---

## 📌 TODO（可扩展）

- 自动识别多种文件名格式（`01-xxx` / `01.xxx`）
- 自动拆分作者（`A,B,C`）
- 从网络刮削元数据（MusicBrainz）
