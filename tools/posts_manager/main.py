from __future__ import annotations

import json
import os
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from datetime import datetime

try:
    import winreg
except ImportError:
    winreg = None

import signal
from PySide6.QtCore import QSortFilterProxyModel, Qt, QDateTime, QTimer, QSize, QSettings, QUrl
from PySide6.QtGui import QAction, QColor, QKeySequence, QPalette, QUndoCommand, QUndoStack, QFont, QSyntaxHighlighter, QTextCharFormat, QPainter, QTextFormat
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QComboBox,
    QPushButton,
    QStatusBar,
    QStackedWidget,
    QStyleFactory,
    QTableView,
    QTextEdit,
    QPlainTextEdit,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QTabWidget,
    QDateTimeEdit,
    QInputDialog,
    QFontComboBox,
)
from PySide6.QtCore import QAbstractTableModel, QModelIndex

APP_NAME = "RiffPointer Posts Manager"
APP_VERSION = "1.0.0"
ORG_NAME = "RiffPointer"
POST_COLUMNS = ("Title", "Date", "Categories", "Tags", "Filename")
THEME_OPTIONS = ("auto", "light", "dark")
REPOSITORY_URL = "https://github.com/riffpointer/riffpointer.github.io/"
COMPACT_ROW_HEIGHT = 22
DEFAULT_ROW_HEIGHT = 28


PREVIEW_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
        font-size: 16px;
        line-height: 1.6;
        word-wrap: break-word;
        padding: 2rem;
        transition: background-color 0.2s, color 0.2s;
    }
    img { max-width: 100%; height: auto; display: block; margin: 1em 0; }
    table { border-collapse: collapse; width: 100%; margin: 1em 0; }
    th, td { border: 1px solid #88888833; padding: 8px 13px; }
    tr:nth-child(even) { background-color: #88888811; }
    pre { border-radius: 6px; padding: 16px; overflow: auto; font-size: 85%; line-height: 1.45; }
    code { font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace; font-size: 85%; margin: 0; padding: 0.2em 0.4em; border-radius: 6px; }
    pre > code { padding: 0; margin: 0; font-size: 100%; word-break: normal; white-space: pre; background: transparent; border: 0; }
    blockquote { border-left: 0.25em solid #dfe2e5; padding: 0 1em; margin: 0 0 1.6em 0; }

    /* GitHub Light */
    body.github-light { color: #24292e; background-color: #ffffff; }
    body.github-light pre { background-color: #f6f8fa; }
    body.github-light code { background-color: rgba(27,31,35,0.05); }
    body.github-light blockquote { border-left-color: #dfe2e5; color: #6a737d; }
    body.github-light a { color: #0366d6; text-decoration: none; }
    body.github-light a:hover { text-decoration: underline; }
    body.github-light h1, body.github-light h2 { border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }

    /* GitHub Dark */
    body.github-dark { color: #c9d1d9; background-color: #0d1117; }
    body.github-dark pre { background-color: #161b22; }
    body.github-dark code { background-color: rgba(240,246,252,0.15); }
    body.github-dark blockquote { border-left-color: #30363d; color: #8b949e; }
    body.github-dark a { color: #58a6ff; text-decoration: none; }
    body.github-dark a:hover { text-decoration: underline; }
    body.github-dark h1, body.github-dark h2 { border-bottom: 1px solid #21262d; padding-bottom: 0.3em; }

    /* Solarized Light */
    body.solarized-light { color: #586e75; background-color: #fdf6e3; }
    body.solarized-light pre { background-color: #eee8d5; }
    body.solarized-light code { background-color: #eee8d5; }
    body.solarized-light blockquote { border-left-color: #93a1a1; color: #93a1a1; }
    body.solarized-light a { color: #268bd2; text-decoration: none; }
    body.solarized-light h1, body.solarized-light h2 { border-bottom: 1px solid #93a1a1; padding-bottom: 0.3em; }

    /* Dracula */
    body.dracula { color: #f8f8f2; background-color: #282a36; }
    body.dracula pre { background-color: #44475a; }
    body.dracula code { background-color: #1e1f29; }
    body.dracula blockquote { border-left-color: #6272a4; color: #6272a4; }
    body.dracula a { color: #ff79c6; text-decoration: none; }
    body.dracula h1, body.dracula h2 { border-bottom: 1px solid #44475a; padding-bottom: 0.3em; }

    /* Monokai */
    body.monokai { color: #f8f8f2; background-color: #272822; }
    body.monokai pre { background-color: #383830; }
    body.monokai code { background-color: #383830; }
    body.monokai blockquote { border-left-color: #75715e; color: #75715e; }
    body.monokai a { color: #f92672; text-decoration: none; }
    body.monokai h1, body.monokai h2 { border-bottom: 1px solid #383830; padding-bottom: 0.3em; }

    /* Nord */
    body.nord { color: #d8dee9; background-color: #2e3440; }
    body.nord pre { background-color: #3b4252; }
    body.nord code { background-color: #3b4252; }
    body.nord blockquote { border-left-color: #4c566a; color: #4c566a; }
    body.nord a { color: #88c0d0; text-decoration: none; }
    body.nord h1, body.nord h2 { border-bottom: 1px solid #3b4252; padding-bottom: 0.3em; }

    /* One Dark */
    body.one-dark { color: #abb2bf; background-color: #282c34; }
    body.one-dark pre { background-color: #2c313a; }
    body.one-dark code { background-color: #2c313a; }
    body.one-dark blockquote { border-left-color: #5c6370; color: #5c6370; }
    body.one-dark a { color: #61afef; text-decoration: none; }
    body.one-dark h1, body.one-dark h2 { border-bottom: 1px solid #2c313a; padding-bottom: 0.3em; }
  </style>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"></script>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/highlight.js@11.8.0/styles/github.min.css" id="hljs-theme">
  <script src="https://cdn.jsdelivr.net/npm/highlight.js@11.8.0/highlight.min.js"></script>
</head>
<body class="github-light">
  <div id="content"></div>
  <script>
    if (typeof marked !== 'undefined') {
        marked.setOptions({
            gfm: true,
            breaks: true,
            highlight: function(code, lang) {
                if (typeof hljs !== 'undefined') {
                    if (lang && hljs.getLanguage(lang)) {
                        try {
                            return hljs.highlight(code, { language: lang }).value;
                        } catch (__) {}
                    }
                    return hljs.highlightAuto(code).value;
                }
                return code;
            }
        });
    }
    
    function parseSimpleMarkdown(md) {
        let html = md;
        // Escape HTML
        html = html.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        // Headers
        html = html.replace(/^# (.*)$/gm, "<h1>$1</h1>");
        html = html.replace(/^## (.*)$/gm, "<h2>$1</h2>");
        html = html.replace(/^### (.*)$/gm, "<h3>$1</h3>");
        html = html.replace(/^#### (.*)$/gm, "<h4>$1</h4>");
        html = html.replace(/^##### (.*)$/gm, "<h5>$1</h5>");
        html = html.replace(/^###### (.*)$/gm, "<h6>$1</h6>");
        // Bold / Italic
        html = html.replace(/\\*\\*(.*?)\\*\\*/g, "<strong>$1</strong>");
        html = html.replace(/\\*(.*?)\\*/g, "<em>$1</em>");
        // Inline code
        html = html.replace(/`(.*?)`/g, "<code>$1</code>");
        // Code blocks
        html = html.replace(/```(.*?)\\n([\\s\\S]*?)```/g, "<pre><code>$2</code></pre>");
        // Links
        html = html.replace(/\\[(.*?)\\]\\((.*?)\\)/g, "<a href='$2'>$1</a>");
        // Paragraphs / Newlines
        html = html.replace(/\\n/g, "<br>");
        return html;
    }
    
    function updatePreview(md) {
        if (typeof marked !== 'undefined' && typeof marked.parse === 'function') {
            document.getElementById('content').innerHTML = marked.parse(md);
        } else {
            document.getElementById('content').innerHTML = parseSimpleMarkdown(md);
        }
        if (window.renderMathInElement) {
            renderMathInElement(document.getElementById('content'), {
                delimiters: [
                    {left: '$$', right: '$$', display: true},
                    {left: '$', right: '$', display: false},
                    {left: '\\(', right: '\\)', display: false},
                    {left: '\\[', right: '\\]', display: true}
                ],
                throwOnError: false
            });
        }
    }
    
    function setTheme(themeName) {
        document.body.className = themeName;
        // Switch highlight.js theme based on markdown theme dark/light mode
        let hljsTheme = document.getElementById('hljs-theme');
        if (themeName.includes('dark') || themeName === 'dracula' || themeName === 'monokai') {
            hljsTheme.href = "https://cdn.jsdelivr.net/npm/highlight.js@11.8.0/styles/github-dark.min.css";
        } else {
            hljsTheme.href = "https://cdn.jsdelivr.net/npm/highlight.js@11.8.0/styles/github.min.css";
        }
    }
  </script>
</body>
</html>
"""


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_posts_data_path() -> Path:
    return repo_root() / "_posts"


def default_settings_path() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / ORG_NAME / "PostsManager" / "settings.json"
    return Path.home() / ".riffpointer-posts-manager" / "settings.json"


def parse_front_matter(content: str) -> tuple[dict[str, Any], str]:
    if not content.startswith("---"):
        return {}, content
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
        
    yaml_part = parts[1]
    body = parts[2]
    
    metadata = {}
    for line in yaml_part.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip()
        
        # Parse value
        if val.startswith("[") and val.endswith("]"):
            items = []
            raw_items = val[1:-1].split(",")
            for item in raw_items:
                item = item.strip()
                if (item.startswith('"') and item.endswith('"')) or (item.startswith("'") and item.endswith("'")):
                    item = item[1:-1]
                if item:
                    items.append(item)
            metadata[key] = items
        else:
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            metadata[key] = val
            
    return metadata, body


def serialize_front_matter(metadata: dict[str, Any], body: str) -> str:
    lines = ["---"]
    ordered_keys = ["layout", "title", "date", "categories", "tags"]
    other_keys = [k for k in metadata.keys() if k not in ordered_keys]
    
    for key in (ordered_keys + other_keys):
        if key not in metadata:
            continue
        val = metadata[key]
        if isinstance(val, list):
            formatted_items = []
            for item in val:
                item_str = str(item)
                if not item_str.isalnum():
                    formatted_items.append(f'"{item_str}"')
                else:
                    formatted_items.append(item_str)
            lines.append(f"{key}: [{', '.join(formatted_items)}]")
        else:
            val_str = str(val)
            if ":" in val_str or val_str.startswith(" ") or val_str.endswith(" ") or '"' in val_str or "'" in val_str:
                escaped = val_str.replace('"', '\\"')
                lines.append(f'{key}: "{escaped}"')
            else:
                lines.append(f"{key}: {val_str}")
    lines.append("---")
    
    if body and not body.startswith("\n"):
        body = "\n" + body
    return "\n".join(lines) + body


def make_post_slug(title: str) -> str:
    s = title.strip().lower()
    s = re.sub(r"[^a-z0-9\s_-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s)
    return s.strip("-")


def get_post_filename(date_str: str, title: str) -> str:
    slug = make_post_slug(title) or "untitled"
    match = re.match(r"^(\d{4}-\d{2}-\d{2})", date_str.strip())
    if match:
        date_part = match.group(1)
    else:
        date_part = datetime.today().strftime("%Y-%m-%d")
    return f"{date_part}-{slug}.md"


def get_target_filepath(post: dict[str, Any], posts_dir: Path) -> Path:
    original_path = post.get("file_path")
    filename = post.get("filename")
    if not filename:
        filename = get_post_filename(post.get("date", ""), post.get("title", ""))
    
    if original_path:
        parent_dir = Path(original_path).parent
        return parent_dir / filename
    else:
        # Check subdirectories of posts_dir
        subdirs = [d for d in posts_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
        if subdirs:
            return subdirs[0] / filename
        return posts_dir / filename


def is_dark_mode_preferred() -> bool:
    if winreg is None:
        return False
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        ) as key:
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return int(value) == 0
    except OSError:
        return False


def apply_dark_fusion_palette(app: QApplication) -> None:
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(45, 45, 45))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(30, 30, 30))
    palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(45, 45, 45))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)


NATIVE_STYLE = ""


def apply_light_theme(app: QApplication) -> None:
    if sys.platform == "win32":
        available = {style.lower(): style for style in QStyleFactory.keys()}
        style_name = available.get("windowsvista") or available.get("windows") or "Fusion"
        app.setStyle(style_name)
    else:
        if NATIVE_STYLE:
            app.setStyle(NATIVE_STYLE)
    app.setPalette(QPalette())


def apply_theme(app: QApplication, theme: str) -> None:
    choice = theme.strip().lower()
    if choice == "dark":
        apply_dark_fusion_palette(app)
    elif choice == "light":
        apply_light_theme(app)
    else:
        if is_dark_mode_preferred():
            apply_dark_fusion_palette(app)
        else:
            apply_light_theme(app)


@dataclass
class SettingsManager:
    bootstrap_path: Path = field(default_factory=default_settings_path)
    settings_path: Path = field(init=False)
    values: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.settings_path = self.bootstrap_path
        self.load()

    def load(self) -> None:
        bootstrap = self._read_json(self.bootstrap_path)
        custom_path = bootstrap.get("settings_file")
        if custom_path:
            self.settings_path = Path(custom_path).expanduser()
        self.values = self._read_json(self.settings_path)
        if "posts_data_path" not in self.values:
            self.values["posts_data_path"] = str(default_posts_data_path())
        if "theme" not in self.values:
            self.values["theme"] = "auto"
        if "compact_mode" not in self.values:
            self.values["compact_mode"] = False
        if "confirm_delete" not in self.values:
            self.values["confirm_delete"] = True

    def save(self) -> None:
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        self.settings_path.write_text(json.dumps(self.values, indent=2), encoding="utf-8")
        if self.settings_path != self.bootstrap_path:
            self.bootstrap_path.parent.mkdir(parents=True, exist_ok=True)
            self.bootstrap_path.write_text(
                json.dumps({"settings_file": str(self.settings_path)}, indent=2),
                encoding="utf-8",
            )

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}


class PostsModel(QAbstractTableModel):
    def __init__(self, posts: list[dict[str, Any]] | None = None) -> None:
        super().__init__()
        self.posts = posts or []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.posts)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(POST_COLUMNS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None
        post = self.posts[index.row()]
        column = index.column()
        if role in (Qt.DisplayRole, Qt.EditRole):
            if column == 0:
                return post.get("title", "")
            if column == 1:
                return post.get("date", "")
            if column == 2:
                cats = post.get("categories", [])
                return ", ".join(cats) if isinstance(cats, list) else str(cats)
            if column == 3:
                tags = post.get("tags", [])
                return ", ".join(tags) if isinstance(tags, list) else str(tags)
            if column == 4:
                return post.get("relative_path") or Path(post.get("file_path", "")).name
        if role == Qt.ToolTipRole:
            body = post.get("body", "")
            return body[:300] + "..." if len(body) > 300 else body
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return POST_COLUMNS[section]
        return section + 1

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        base = super().flags(index)
        return base | Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def set_posts(self, posts: list[dict[str, Any]]) -> None:
        self.beginResetModel()
        self.posts = posts
        self.endResetModel()

    def add_post(self, post: dict[str, Any]) -> None:
        row = len(self.posts)
        self.beginInsertRows(QModelIndex(), row, row)
        self.posts.append(post)
        self.endInsertRows()

    def insert_post(self, row: int, post: dict[str, Any]) -> None:
        row = max(0, min(row, len(self.posts)))
        self.beginInsertRows(QModelIndex(), row, row)
        self.posts.insert(row, post)
        self.endInsertRows()

    def replace_post(self, row: int, post: dict[str, Any]) -> None:
        self.posts[row] = post
        self.dataChanged.emit(self.index(row, 0), self.index(row, self.columnCount() - 1))

    def remove_post(self, row: int) -> dict[str, Any]:
        self.beginRemoveRows(QModelIndex(), row, row)
        post = self.posts.pop(row)
        self.endRemoveRows()
        return post


class PostsProxyModel(QSortFilterProxyModel):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.search_text = ""
        self.filter_mode = "all"

    def set_search_text(self, text: str) -> None:
        self.search_text = text.strip().lower()
        self.invalidateFilter()

    def set_filter_mode(self, mode: str) -> None:
        self.filter_mode = mode
        self.invalidateFilter()

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
        left_data = self.sourceModel().data(left, Qt.DisplayRole)
        right_data = self.sourceModel().data(right, Qt.DisplayRole)
        if left_data is None:
            return True
        if right_data is None:
            return False
        return str(left_data).lower() < str(right_data).lower()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        if not self.search_text:
            return True
            
        model = self.sourceModel()
        post = model.posts[source_row]
        
        title = str(post.get("title", "")).lower()
        date = str(post.get("date", "")).lower()
        categories = ", ".join(post.get("categories", [])).lower()
        tags = ", ".join(post.get("tags", [])).lower()
        filename = str(post.get("relative_path") or "").lower()
        body = str(post.get("body", "")).lower()
        
        if self.filter_mode == "title":
            return self.search_text in title
        elif self.filter_mode == "categories":
            return self.search_text in categories
        elif self.filter_mode == "tags":
            return self.search_text in tags
        elif self.filter_mode == "content":
            return self.search_text in body
        else: # all
            return (
                self.search_text in title
                or self.search_text in date
                or self.search_text in categories
                or self.search_text in tags
                or self.search_text in filename
                or self.search_text in body
            )


class EditPostCommand(QUndoCommand):
    def __init__(self, window: MainWindow, row: int, before: dict[str, Any], after: dict[str, Any]) -> None:
        super().__init__(f"Edit {before.get('title', 'Post')}")
        self.window = window
        self.row = row
        self.before = before
        self.after = after

    def undo(self) -> None:
        self.window.model.replace_post(self.row, self.before)

    def redo(self) -> None:
        self.window.model.replace_post(self.row, self.after)


class AddPostCommand(QUndoCommand):
    def __init__(self, window: MainWindow, post: dict[str, Any]) -> None:
        super().__init__(f"Add {post.get('title', 'Post')}")
        self.window = window
        self.post = post
        self.row = len(window.model.posts)

    def undo(self) -> None:
        self.window.model.remove_post(self.row)

    def redo(self) -> None:
        self.window.model.insert_post(self.row, self.post)


class DeletePostCommand(QUndoCommand):
    def __init__(self, window: MainWindow, row: int, post: dict[str, Any]) -> None:
        super().__init__(f"Delete {post.get('title', 'Post')}")
        self.window = window
        self.row = row
        self.post = post

    def undo(self) -> None:
        self.window.model.insert_post(self.row, self.post)

    def redo(self) -> None:
        self.window.model.remove_post(self.row)


def parse_date_string(date_str: str) -> tuple[datetime, str]:
    date_str = date_str.strip()
    match = re.match(r"^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})(?:\s+([+-]\d{2}:?\d{2}|Z))?$", date_str)
    if match:
        dt_part = match.group(1)
        tz_part = match.group(2) or "+05:30"
        try:
            dt = datetime.strptime(dt_part, "%Y-%m-%d %H:%M:%S")
            return dt, tz_part
        except ValueError:
            pass
            
    match = re.match(r"^(\d{4}-\d{2}-\d{2})$", date_str)
    if match:
        try:
            dt = datetime.strptime(match.group(1), "%Y-%m-%d")
            return dt, "+05:30"
        except ValueError:
            pass
            
    return datetime.now(), "+05:30"


class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rules = []
        
        # Heading formats: different point sizes for H1 to H6
        self.heading_formats = {}
        heading_sizes = {
            1: 20.0,
            2: 17.0,
            3: 15.0,
            4: 13.0,
            5: 11.0,
            6: 10.0
        }
        for level, size in heading_sizes.items():
            fmt = QTextCharFormat()
            fmt.setForeground(QColor("#2A82DA"))  # Blue
            fmt.setFontWeight(QFont.Bold)
            fmt.setFontPointSize(size)
            self.heading_formats[level] = fmt
            
        # Code block format
        self.code_block_format = QTextCharFormat()
        self.code_block_format.setBackground(QColor(128, 128, 128, 30))  # Semi-transparent gray background
        mono_font = QFont("Courier New" if os.name == "nt" else "Monospace")
        mono_font.setStyleHint(QFont.Monospace)
        self.code_block_format.setFont(mono_font)
        
        # Bold format
        b_format = QTextCharFormat()
        b_format.setFontWeight(QFont.Bold)
        b_format.setForeground(QColor("#E06C75"))  # Rose/Pink
        self.rules.append((re.compile(r"\*\*[^*]+\*\*"), b_format))
        self.rules.append((re.compile(r"__[^*]+__"), b_format))
        
        # Italic format
        i_format = QTextCharFormat()
        i_format.setFontItalic(True)
        i_format.setForeground(QColor("#98C379"))  # Green
        self.rules.append((re.compile(r"\*[^*]+\*"), i_format))
        self.rules.append((re.compile(r"_[^*]+_"), i_format))
        
        # Inline code format
        code_format = QTextCharFormat()
        code_format.setForeground(QColor("#D19A66"))  # Orange
        font = QFont("Courier New" if os.name == "nt" else "Monospace")
        font.setStyleHint(QFont.Monospace)
        code_format.setFont(font)
        self.rules.append((re.compile(r"`[^`]+`"), code_format))
        
        # Link format
        link_format = QTextCharFormat()
        link_format.setForeground(QColor("#61AFEF"))  # Light Blue
        link_format.setFontUnderline(True)
        self.rules.append((re.compile(r"\[[^\]]+\]\([^)]+\)"), link_format))
        
        # Blockquote format
        quote_format = QTextCharFormat()
        quote_format.setForeground(QColor("#5C6370"))  # Gray
        quote_format.setFontItalic(True)
        self.rules.append((re.compile(r"^\s*>\s+.*$"), quote_format))
        
        # Front matter (YAML blocks) format
        yaml_format = QTextCharFormat()
        yaml_format.setForeground(QColor("#C678DD"))  # Purple
        self.rules.append((re.compile(r"^\s*---$"), yaml_format))
        self.rules.append((re.compile(r"^\s*[a-zA-Z0-9_-]+\s*:"), yaml_format))

    def highlightBlock(self, text):
        # 1. Handle code blocks using block states
        is_in_code_block = self.previousBlockState() == 1
        
        if "```" in text:
            if is_in_code_block:
                self.setCurrentBlockState(0)
            else:
                self.setCurrentBlockState(1)
            self.setFormat(0, len(text), self.code_block_format)
            return
            
        if is_in_code_block:
            self.setCurrentBlockState(1)
            self.setFormat(0, len(text), self.code_block_format)
            return
            
        self.setCurrentBlockState(0)
        
        # 2. Handle headings (H1 to H6) with different sizes
        match = re.match(r"^(#{1,6})\s+(.*)$", text)
        if match:
            level = len(match.group(1))
            heading_format = self.heading_formats.get(level)
            if heading_format:
                self.setFormat(0, len(text), heading_format)
                return
                
        # 3. Handle standard rules
        for pattern, fmt in self.rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, fmt)


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)


class MarkdownEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)
        self.show_line_numbers = True
        self.show_line_highlight = True
        
        # Connect signals
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        
        self.update_line_number_area_width(0)
        self.highlight_current_line()
        
    def line_number_area_width(self):
        if not self.show_line_numbers:
            return 0
        digits = 1
        max_blocks = max(1, self.blockCount())
        while max_blocks >= 10:
            max_blocks /= 10
            digits += 1
        space = 10 + self.fontMetrics().horizontalAdvance("9") * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            cr.left(), cr.top(), self.line_number_area_width(), cr.height()
        )

    def set_show_line_numbers(self, show: bool):
        self.show_line_numbers = show
        self.update_line_number_area_width(0)
        self.line_number_area.setVisible(show)
        self.line_number_area.update()

    def set_show_line_highlight(self, show: bool):
        self.show_line_highlight = show
        self.highlight_current_line()

    def highlight_current_line(self):
        extra_selections = []
        if not self.isReadOnly() and self.show_line_highlight:
            selection = QTextEdit.ExtraSelection()
            line_color = QColor(128, 128, 128, 20)  # Subtle translucent gray
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)

    def line_number_area_paint_event(self, event):
        if not self.show_line_numbers:
            return
            
        painter = QPainter(self.line_number_area)
        # Subtle background matching the theme
        bg_color = self.palette().color(QPalette.Window)
        painter.fillRect(event.rect(), bg_color)

        # Draw a fine separator on the right
        border_color = self.palette().color(QPalette.Midlight)
        painter.setPen(border_color)
        painter.drawLine(
            self.line_number_area.width() - 1,
            event.rect().top(),
            self.line_number_area.width() - 1,
            event.rect().bottom()
        )

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        # Muted text color for line numbers
        painter.setPen(self.palette().color(QPalette.PlaceholderText))
        painter.setFont(self.font())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.drawText(
                    0,
                    top,
                    self.line_number_area.width() - 5,
                    self.fontMetrics().height(),
                    Qt.AlignRight | Qt.AlignVCenter,
                    number
                )

            block = block.next()
            top = bottom
            if block.isValid():
                bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1


class PostDialog(QDialog):
    def __init__(self, parent: QWidget | None = None, post: dict[str, Any] | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Edit Post" if post else "New Post")
        
        # MANUAL HEIGHT CALCULATION:
        # -------------------------------------------------------------
        # Margin top + bottom around layout: 2 * 10 = 20px
        # QTabWidget header & framing: ~40px
        # Button box height & layout spacing: 30 + 15 = 45px
        # QFormLayout rows:
        #   - Title QLineEdit: 26px
        #   - Date QDateTimeEdit: 26px
        #   - Categories QLineEdit: 26px
        #   - Tags QLineEdit: 26px
        #   - Layout QLineEdit: 26px
        #   - Excerpt QTextEdit: 80px
        #   - Filename QLineEdit: 26px
        #   - Row vertical spacings (6 spaces * 8px): 48px
        # Total QFormLayout height: 26*6 + 80 + 48 = 284px
        # -------------------------------------------------------------
        # Calculated Minimum Height = 20 + 40 + 45 + 284 = 389px -> 400px
        self.setMinimumHeight(400)
        self.resize(750, 400)
        
        self._post = post
        self._filename_touched = post is not None
        self._preview_ready = False
        
        self.tabs = QTabWidget()
        
        # Tab 1: Metadata
        self.meta_tab = QWidget()
        self.meta_layout_outer = QVBoxLayout(self.meta_tab)
        self.meta_layout = QFormLayout()
        
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Post title")
        
        self.date_edit = QDateTimeEdit(self)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.timezone_offset = "+05:30"
        
        self.categories_edit = QLineEdit()
        self.categories_edit.setPlaceholderText("category-one, category-two")
        
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("tag-one, tag-two")
        
        self.layout_edit = QLineEdit()
        self.layout_edit.setText("post")
        self.layout_edit.setPlaceholderText("post")
        
        self.excerpt_edit = QTextEdit()
        self.excerpt_edit.setPlaceholderText("Optional short summary/excerpt")
        self.excerpt_edit.setMaximumHeight(80)
        
        self.filename_edit = QLineEdit()
        self.filename_edit.setPlaceholderText("YYYY-MM-DD-post-title-slug.md")
        self._update_filename_preview()
        
        self.meta_layout.addRow("Title", self.title_edit)
        self.meta_layout.addRow("Date", self.date_edit)
        self.meta_layout.addRow("Categories", self.categories_edit)
        self.meta_layout.addRow("Tags", self.tags_edit)
        self.meta_layout.addRow("Layout", self.layout_edit)
        self.meta_layout.addRow("Excerpt", self.excerpt_edit)
        self.meta_layout.addRow("Filename", self.filename_edit)
        
        self.meta_layout_outer.addLayout(self.meta_layout)
        self.meta_layout_outer.addStretch(1)
        
        # Tab 2: Content (Markdown Editor)
        self.content_tab = QWidget()
        self.content_layout = QVBoxLayout(self.content_tab)
        self.content_layout.setContentsMargins(4, 4, 4, 4)
        self.content_layout.setSpacing(4)
        
        # Build Formatting Toolbar
        self.toolbar = QToolBar(self.content_tab)
        self.toolbar.setMovable(False)
        self.toolbar.setStyleSheet("QToolBar { spacing: 4px; padding: 2px; background-color: transparent; }")
        
        bold_btn = QAction("Bold", self)
        bold_btn.setToolTip("Bold (Ctrl+B)")
        bold_btn.triggered.connect(lambda: self.insert_markdown("**", "**"))
        bold_btn.setShortcut(QKeySequence.Bold)
        self.toolbar.addAction(bold_btn)
        
        italic_btn = QAction("Italic", self)
        italic_btn.setToolTip("Italic (Ctrl+I)")
        italic_btn.triggered.connect(lambda: self.insert_markdown("*", "*"))
        italic_btn.setShortcut(QKeySequence.Italic)
        self.toolbar.addAction(italic_btn)
        
        self.toolbar.addSeparator()
        
        h2_btn = QAction("H2", self)
        h2_btn.setToolTip("Heading 2")
        h2_btn.triggered.connect(lambda: self.format_line_prefix("## "))
        self.toolbar.addAction(h2_btn)
        
        h3_btn = QAction("H3", self)
        h3_btn.setToolTip("Heading 3")
        h3_btn.triggered.connect(lambda: self.format_line_prefix("### "))
        self.toolbar.addAction(h3_btn)
        
        self.toolbar.addSeparator()
        
        link_btn = QAction("Link", self)
        link_btn.setToolTip("Insert Link")
        link_btn.triggered.connect(self.format_link)
        self.toolbar.addAction(link_btn)
        
        code_block_btn = QAction("Code Block", self)
        code_block_btn.setToolTip("Insert Code Block")
        code_block_btn.triggered.connect(self.format_code_block)
        self.toolbar.addAction(code_block_btn)
        
        code_inline_btn = QAction("Inline Code", self)
        code_inline_btn.setToolTip("Insert Inline Code")
        code_inline_btn.triggered.connect(lambda: self.insert_markdown("`", "`"))
        self.toolbar.addAction(code_inline_btn)
        
        self.toolbar.addSeparator()
        
        quote_btn = QAction("Quote", self)
        quote_btn.setToolTip("Insert Blockquote")
        quote_btn.triggered.connect(lambda: self.format_line_prefix("> "))
        self.toolbar.addAction(quote_btn)
        
        list_btn = QAction("List", self)
        list_btn.setToolTip("Insert Bullet List")
        list_btn.triggered.connect(lambda: self.format_line_prefix("* "))
        self.toolbar.addAction(list_btn)
        
        self.toolbar.addSeparator()
        
        font_label = QLabel("Font: ", self.toolbar)
        font_label.setStyleSheet("padding-left: 4px; padding-right: 2px;")
        self.toolbar.addWidget(font_label)
        
        # Load settings
        settings = QSettings(ORG_NAME, APP_NAME)
        
        def get_bool_setting(key, default):
            val = settings.value(key, default)
            if isinstance(val, bool):
                return val
            if isinstance(val, str):
                return val.lower() in ("true", "1", "yes")
            return bool(int(val)) if isinstance(val, int) else default
            
        show_ln = get_bool_setting("editor/show_line_numbers", True)
        show_lh = get_bool_setting("editor/show_line_highlight", True)
        word_wrap = get_bool_setting("editor/word_wrap", True)
        font_family = settings.value("editor/font_family", "")
        
        self.font_combo = QFontComboBox(self.toolbar)
        self.font_combo.setFontFilters(QFontComboBox.MonospacedFonts)
        self.font_combo.setMaximumWidth(140)
        self.toolbar.addWidget(self.font_combo)
        
        # Editor Settings Button & Menu
        settings_menu = QMenu(self)
        self.ln_action = QAction("Show Line Numbers", self)
        self.ln_action.setCheckable(True)
        self.ln_action.setChecked(show_ln)
        self.ln_action.triggered.connect(self.toggle_line_numbers)
        settings_menu.addAction(self.ln_action)
        
        self.lh_action = QAction("Highlight Current Line", self)
        self.lh_action.setCheckable(True)
        self.lh_action.setChecked(show_lh)
        self.lh_action.triggered.connect(self.toggle_line_highlight)
        settings_menu.addAction(self.lh_action)
        
        self.ww_action = QAction("Word Wrap Text", self)
        self.ww_action.setCheckable(True)
        self.ww_action.setChecked(word_wrap)
        self.ww_action.triggered.connect(self.toggle_word_wrap)
        settings_menu.addAction(self.ww_action)
        
        self.settings_btn = QToolButton(self.toolbar)
        self.settings_btn.setText("⚙️")
        self.settings_btn.setToolTip("Editor Settings")
        self.settings_btn.setPopupMode(QToolButton.InstantPopup)
        self.settings_btn.setMenu(settings_menu)
        self.toolbar.addWidget(self.settings_btn)
        
        self.content_layout.addWidget(self.toolbar)
        
        self.content_edit = MarkdownEditor()
        self.content_edit.set_show_line_numbers(show_ln)
        self.content_edit.set_show_line_highlight(show_lh)
        if word_wrap:
            self.content_edit.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        else:
            self.content_edit.setLineWrapMode(QPlainTextEdit.NoWrap)
            
        if font_family:
            initial_font = QFont(font_family)
        else:
            initial_font = QFont("Courier New" if os.name == "nt" else "Monospace")
        initial_font.setStyleHint(QFont.Monospace)
        initial_font.setPointSize(11)
        
        self.content_edit.setFont(initial_font)
        self.font_combo.setCurrentFont(initial_font)
        
        # Connect font combo signal after setting initial font
        self.font_combo.currentFontChanged.connect(self.change_editor_font)
        
        self.content_edit.setPlaceholderText("Write your markdown post content here...")
        self.content_layout.addWidget(self.content_edit)
        self.highlighter = MarkdownHighlighter(self.content_edit.document())
        
        # Tab 3: Preview
        self.preview_tab = QWidget()
        self.preview_layout = QVBoxLayout(self.preview_tab)
        self.preview_layout.setContentsMargins(4, 4, 4, 4)
        self.preview_layout.setSpacing(4)
        
        # Preview Toolbar
        self.preview_toolbar = QToolBar(self.preview_tab)
        self.preview_toolbar.setMovable(False)
        self.preview_toolbar.setStyleSheet("QToolBar { spacing: 4px; padding: 2px; background-color: transparent; }")
        
        # Theme Selector Label
        theme_label = QLabel("Theme: ", self.preview_toolbar)
        theme_label.setStyleSheet("padding-left: 4px; padding-right: 2px;")
        self.preview_toolbar.addWidget(theme_label)
        
        self.preview_theme_combo = QComboBox(self.preview_toolbar)
        self.preview_theme_combo.addItems(["GitHub Light", "GitHub Dark", "Solarized Light", "Dracula", "Monokai", "Nord", "One Dark"])
        self.preview_toolbar.addWidget(self.preview_theme_combo)
        
        self.preview_toolbar.addSeparator()
        
        # Reload Button
        reload_action = QAction("🔄 Reload", self)
        reload_action.setToolTip("Reload Preview")
        reload_action.triggered.connect(self.update_preview)
        self.preview_toolbar.addAction(reload_action)
        
        self.preview_toolbar.addSeparator()
        
        # Auto-update Checkbox
        self.auto_update_cb = QCheckBox("Auto-Update", self.preview_toolbar)
        self.auto_update_cb.setChecked(True)
        self.preview_toolbar.addWidget(self.auto_update_cb)
        
        self.preview_toolbar.addSeparator()
        
        # Zoom controls
        zoom_in_action = QAction("A+", self)
        zoom_in_action.setToolTip("Zoom In")
        zoom_in_action.triggered.connect(lambda: self.webview.setZoomFactor(self.webview.zoomFactor() + 0.1))
        self.preview_toolbar.addAction(zoom_in_action)
        
        zoom_out_action = QAction("A-", self)
        zoom_out_action.setToolTip("Zoom Out")
        zoom_out_action.triggered.connect(lambda: self.webview.setZoomFactor(max(0.2, self.webview.zoomFactor() - 0.1)))
        self.preview_toolbar.addAction(zoom_out_action)
        
        self.preview_layout.addWidget(self.preview_toolbar)
        
        # WebView
        self.webview = QWebEngineView(self.preview_tab)
        self.preview_layout.addWidget(self.webview)
        
        # Set up repo root Base URL
        repo_root_path = repo_root()
        self.preview_base_url = QUrl.fromLocalFile(str(repo_root_path) + "/")
        self.webview.setHtml(PREVIEW_HTML_TEMPLATE, self.preview_base_url)
        
        # Settings for auto update
        auto_up = get_bool_setting("preview/auto_update", True)
        self.auto_update_cb.setChecked(auto_up)
        self.auto_update_cb.toggled.connect(self.toggle_auto_update)
        
        # Hook up theme settings and preview update
        self.preview_theme_combo.currentTextChanged.connect(self.change_preview_theme)
        self.webview.loadFinished.connect(self.on_preview_load_finished)
        self.content_edit.textChanged.connect(self.on_editor_text_changed)
        
        self.tabs.addTab(self.meta_tab, "Metadata")
        self.tabs.addTab(self.content_tab, "Content (Markdown)")
        self.tabs.addTab(self.preview_tab, "Preview")
        
        # Listen for tab changes
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs)
        layout.addWidget(buttons)
        
        self.title_edit.textChanged.connect(self._update_filename_preview)
        self.date_edit.dateTimeChanged.connect(self._update_filename_preview)
        self.filename_edit.textEdited.connect(self._mark_filename_touched)
        
        if post:
            self.title_edit.setText(post.get("title", ""))
            
            dt, tz = parse_date_string(post.get("date", ""))
            qdt = QDateTime.fromString(dt.strftime("%Y-%m-%dT%H:%M:%S"), Qt.ISODate)
            self.date_edit.setDateTime(qdt)
            self.timezone_offset = tz
            
            cats = post.get("categories", [])
            self.categories_edit.setText(", ".join(cats) if isinstance(cats, list) else str(cats))
            tags = post.get("tags", [])
            self.tags_edit.setText(", ".join(tags) if isinstance(tags, list) else str(tags))
            self.layout_edit.setText(post.get("layout", "post"))
            self.excerpt_edit.setText(post.get("excerpt", ""))
            self.content_edit.setPlainText(post.get("body", ""))
            
            orig_filename = post.get("relative_path")
            if orig_filename:
                orig_filename = Path(orig_filename).name
            else:
                orig_filename = Path(post.get("file_path", "")).name
            self.filename_edit.setText(orig_filename)
            self._filename_touched = True
            
    def _mark_filename_touched(self) -> None:
        self._filename_touched = True
            
    def _update_filename_preview(self) -> None:
        if getattr(self, "_filename_touched", False):
            return
        title = self.title_edit.text().strip()
        dt_val = self.date_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        filename = get_post_filename(dt_val, title)
        self.filename_edit.setText(filename)
 
    def insert_markdown(self, prefix: str, suffix: str = "") -> None:
        cursor = self.content_edit.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            cursor.insertText(f"{prefix}{selected_text}{suffix}")
        else:
            cursor.insertText(f"{prefix}{suffix}")
            if suffix:
                cursor.movePosition(cursor.Left, cursor.MoveAnchor, len(suffix))
            self.content_edit.setTextCursor(cursor)
        self.content_edit.setFocus()
        
    def format_link(self) -> None:
        cursor = self.content_edit.textCursor()
        selected = cursor.selectedText()
        
        url, ok1 = QInputDialog.getText(self, "Insert Link", "Link URL:", QLineEdit.Normal, "https://")
        if not ok1 or not url:
            return
            
        if selected:
            cursor.insertText(f"[{selected}]({url})")
        else:
            text, ok2 = QInputDialog.getText(self, "Insert Link", "Link Text:")
            if ok2 and text:
                cursor.insertText(f"[{text}]({url})")
            else:
                cursor.insertText(f"[{url}]({url})")
        self.content_edit.setFocus()
        
    def format_code_block(self) -> None:
        cursor = self.content_edit.textCursor()
        selected = cursor.selectedText()
        selected = selected.replace("\u2029", "\n")
        if selected:
            cursor.insertText(f"```\n{selected}\n```")
        else:
            cursor.insertText("```\n\n```")
            cursor.movePosition(cursor.Up)
            self.content_edit.setTextCursor(cursor)
        self.content_edit.setFocus()
        
    def format_line_prefix(self, prefix: str) -> None:
        cursor = self.content_edit.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        
        cursor.setPosition(start)
        cursor.movePosition(cursor.StartOfLine)
        start_pos = cursor.position()
        
        cursor.setPosition(end)
        cursor.movePosition(cursor.EndOfLine)
        end_pos = cursor.position()
        
        cursor.setPosition(start_pos)
        cursor.setPosition(end_pos, cursor.KeepAnchor)
        
        text = cursor.selectedText()
        lines = text.split("\u2029")
        prefixed_lines = [f"{prefix}{line}" for line in lines]
        cursor.insertText("\n".join(prefixed_lines))
        self.content_edit.setFocus()

    def change_editor_font(self, font: QFont) -> None:
        font.setPointSize(11)
        self.content_edit.setFont(font)
        # Update line number area font and width
        self.content_edit.line_number_area.setFont(font)
        self.content_edit.update_line_number_area_width(0)
        settings = QSettings(ORG_NAME, APP_NAME)
        settings.setValue("editor/font_family", font.family())
        
    def toggle_line_numbers(self, checked: bool) -> None:
        self.content_edit.set_show_line_numbers(checked)
        settings = QSettings(ORG_NAME, APP_NAME)
        settings.setValue("editor/show_line_numbers", checked)
        
    def toggle_line_highlight(self, checked: bool) -> None:
        self.content_edit.set_show_line_highlight(checked)
        settings = QSettings(ORG_NAME, APP_NAME)
        settings.setValue("editor/show_line_highlight", checked)
        
    def toggle_word_wrap(self, checked: bool) -> None:
        if checked:
            self.content_edit.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        else:
            self.content_edit.setLineWrapMode(QPlainTextEdit.NoWrap)
        settings = QSettings(ORG_NAME, APP_NAME)
        settings.setValue("editor/word_wrap", checked)

    def change_preview_theme(self, theme_text: str) -> None:
        if not getattr(self, "_preview_ready", False):
            return
        theme_class = theme_text.lower().replace(" ", "-")
        self.webview.page().runJavaScript(f"setTheme('{theme_class}');")
        settings = QSettings(ORG_NAME, APP_NAME)
        settings.setValue("preview/theme", theme_text)
        
    def on_preview_load_finished(self, ok: bool) -> None:
        self._preview_ready = True
        settings = QSettings(ORG_NAME, APP_NAME)
        saved_theme = settings.value("preview/theme", "GitHub Light")
        idx = self.preview_theme_combo.findText(saved_theme)
        if idx >= 0:
            self.preview_theme_combo.setCurrentIndex(idx)
        else:
            self.preview_theme_combo.setCurrentIndex(0)
            
        theme_class = self.preview_theme_combo.currentText().lower().replace(" ", "-")
        self.webview.page().runJavaScript(f"setTheme('{theme_class}');")
        self.update_preview()
        
    def update_preview(self) -> None:
        if not getattr(self, "_preview_ready", False):
            return
        markdown_text = self.content_edit.toPlainText()
        if markdown_text.startswith("---\n"):
            end_idx = markdown_text.find("---\n", 4)
            if end_idx != -1:
                markdown_text = markdown_text[end_idx + 4:]
        self.webview.page().runJavaScript(f"updatePreview({json.dumps(markdown_text)});")
        
    def on_editor_text_changed(self) -> None:
        if self.auto_update_cb.isChecked():
            self.update_preview()
            
    def on_tab_changed(self, index: int) -> None:
        if index == 2:  # Preview tab
            self.update_preview()
            
    def toggle_auto_update(self, checked: bool) -> None:
        settings = QSettings(ORG_NAME, APP_NAME)
        settings.setValue("preview/auto_update", checked)
        if checked:
            self.update_preview()
 
    def accept(self) -> None:
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "Missing Post Title", "Title is required.")
            return
        filename = self.filename_edit.text().strip()
        if not filename:
            QMessageBox.warning(self, "Missing Filename", "Filename is required.")
            return
        super().accept()
 
    def get_post_data(self) -> dict[str, Any]:
        cats = [c.strip() for c in self.categories_edit.text().split(",") if c.strip()]
        tags = [t.strip() for t in self.tags_edit.text().split(",") if t.strip()]
        filename = self.filename_edit.text().strip()
        if not (filename.endswith(".md") or filename.endswith(".markdown")):
            filename += ".md"
            
        dt_str = self.date_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        date_val = f"{dt_str} {self.timezone_offset}"
        
        data = {
            "title": self.title_edit.text().strip(),
            "date": date_val,
            "categories": cats,
            "tags": tags,
            "layout": self.layout_edit.text().strip() or "post",
            "excerpt": self.excerpt_edit.toPlainText().strip(),
            "body": self.content_edit.toPlainText(),
            "filename": filename,
        }
        if self._post:
            data["file_path"] = self._post.get("file_path")
            data["relative_path"] = self._post.get("relative_path")
        return data


class PreferencesDialog(QDialog):
    def __init__(self, parent: QWidget, settings: SettingsManager) -> None:
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setMinimumWidth(500)
        self.settings = settings

        self.posts_path_edit = QLineEdit(settings.values["posts_data_path"])
        self.posts_path_browse = QPushButton("Browse...")
        self.posts_path_browse.clicked.connect(self.browse_posts_path)
        
        posts_row = QHBoxLayout()
        posts_row.addWidget(self.posts_path_edit, 1)
        posts_row.addWidget(self.posts_path_browse)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(THEME_OPTIONS)
        self.theme_combo.setCurrentText(settings.values["theme"])

        self.compact_check = QCheckBox("Use compact mode")
        self.compact_check.setChecked(settings.values["compact_mode"])

        self.confirm_delete_check = QCheckBox("Confirm before deleting items")
        self.confirm_delete_check.setChecked(settings.values["confirm_delete"])

        form = QFormLayout()
        form.addRow("Posts Folder", posts_row)
        form.addRow("Theme", self.theme_combo)
        form.addRow("", self.compact_check)
        form.addRow("", self.confirm_delete_check)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def browse_posts_path(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select _posts Folder", self.posts_path_edit.text())
        if path:
            self.posts_path_edit.setText(path)

    def accept(self) -> None:
        self.settings.values["posts_data_path"] = self.posts_path_edit.text()
        self.settings.values["theme"] = self.theme_combo.currentText()
        self.settings.values["compact_mode"] = self.compact_check.isChecked()
        self.settings.values["confirm_delete"] = self.confirm_delete_check.isChecked()
        self.settings.save()
        super().accept()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.settings = SettingsManager()
        self.posts_dir = Path(self.settings.values["posts_data_path"]).expanduser()
        self.loaded_filepaths: set[Path] = set()
        self.dirty = False
        self.undo_stack = QUndoStack(self)
        self.undo_stack.indexChanged.connect(self._sync_dirty_state)

        self.setWindowTitle(APP_NAME)
        self.resize(1080, 680)

        self.model = PostsModel()
        self.model.modelReset.connect(self.update_empty_state)
        self.model.rowsInserted.connect(self.update_empty_state)
        self.model.rowsRemoved.connect(self.update_empty_state)
        
        self.proxy = PostsProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy.setFilterKeyColumn(-1)
        
        self.table = QTableView()
        self.table.setModel(self.proxy)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.ExtendedSelection)
        self.table.setSortingEnabled(True)
        self.table.doubleClicked.connect(self.edit_selected_post)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionsClickable(True)
        self.table.selectionModel().selectionChanged.connect(self._sync_selection_actions)
        
        self.empty_label = QLabel("No posts found in the configured directory.")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: #808080; font-size: 18px;")
        self.empty_label.setWordWrap(True)
        
        self.central_stack = QStackedWidget()
        self.central_stack.addWidget(self.table)
        self.central_stack.addWidget(self.empty_label)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search posts...")
        self.search_edit.textChanged.connect(self.proxy.set_search_text)
        
        self.filter_button = QToolButton()
        self.filter_button.setText("Filter")
        self.filter_button.setPopupMode(QToolButton.InstantPopup)
        self.filter_button.setToolTip("Search filter options")
        self._build_filter_menu()

        top = QToolBar("Quick Actions")
        top.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, top)
        self._build_actions()
        
        top.addWidget(self.search_edit)
        top.addWidget(self.filter_button)
        top.addAction(self.undo_action)
        top.addAction(self.redo_action)
        top.addSeparator()
        top.addAction(self.new_action)
        top.addAction(self.edit_action)
        top.addAction(self.delete_action)
        top.addSeparator()
        top.addAction(self.save_action)
        top.addAction(self.reload_action)

        self.setCentralWidget(self.central_stack)
        self.setStatusBar(QStatusBar())
        self._build_menus()
        self.apply_compact_mode(bool(self.settings.values.get("compact_mode", False)))
        self.load_posts_data()
        self._sync_selection_actions()

    def _build_filter_menu(self) -> None:
        menu = QMenu(self)
        
        all_act = QAction("All Columns", self)
        all_act.setCheckable(True)
        all_act.setChecked(True)
        all_act.triggered.connect(lambda: self._set_filter_mode("all", all_act))
        menu.addAction(all_act)
        
        title_act = QAction("Title Only", self)
        title_act.setCheckable(True)
        title_act.triggered.connect(lambda: self._set_filter_mode("title", title_act))
        menu.addAction(title_act)
        
        cats_act = QAction("Categories Only", self)
        cats_act.setCheckable(True)
        cats_act.triggered.connect(lambda: self._set_filter_mode("categories", cats_act))
        menu.addAction(cats_act)
        
        tags_act = QAction("Tags Only", self)
        tags_act.setCheckable(True)
        tags_act.triggered.connect(lambda: self._set_filter_mode("tags", tags_act))
        menu.addAction(tags_act)
        
        content_act = QAction("Content/Body Only", self)
        content_act.setCheckable(True)
        content_act.triggered.connect(lambda: self._set_filter_mode("content", content_act))
        menu.addAction(content_act)
        
        self.filter_actions = [all_act, title_act, cats_act, tags_act, content_act]
        self.filter_button.setMenu(menu)

    def _set_filter_mode(self, mode: str, active_act: QAction) -> None:
        for act in self.filter_actions:
            act.setChecked(act == active_act)
        self.proxy.set_filter_mode(mode)
        self.search_edit.setPlaceholderText(f"Search posts ({mode})...")

    def _build_actions(self) -> None:
        self.new_action = QAction("New", self)
        self.new_action.setShortcut(QKeySequence.New)
        self.new_action.triggered.connect(self.new_post)

        self.undo_action = self.undo_stack.createUndoAction(self, "Undo")
        self.undo_action.setShortcut(QKeySequence.Undo)

        self.redo_action = self.undo_stack.createRedoAction(self, "Redo")
        self.redo_action.setShortcut(QKeySequence.Redo)

        self.edit_action = QAction("Edit", self)
        self.edit_action.setShortcut(QKeySequence("Ctrl+E"))
        self.edit_action.triggered.connect(self.edit_selected_post)

        self.delete_action = QAction("Delete", self)
        self.delete_action.setShortcut(QKeySequence.Delete)
        self.delete_action.triggered.connect(self.delete_selected_post)

        self.save_action = QAction("Save", self)
        self.save_action.setShortcut(QKeySequence.Save)
        self.save_action.triggered.connect(self.save_posts)

        self.reload_action = QAction("Reload", self)
        self.reload_action.triggered.connect(self.reload_posts)

    def _build_menus(self) -> None:
        file = self.menuBar().addMenu("File")
        file.addAction(self.save_action)
        file.addAction(self.reload_action)
        file.addSeparator()
        
        pref_act = QAction("Preferences...", self)
        pref_act.triggered.connect(self.show_preferences)
        file.addAction(pref_act)
        file.addSeparator()
        
        exit_act = QAction("Exit", self)
        exit_act.triggered.connect(self.close)
        file.addAction(exit_act)

        edit = self.menuBar().addMenu("Edit")
        edit.addAction(self.undo_action)
        edit.addAction(self.redo_action)
        edit.addSeparator()
        edit.addAction(self.new_action)
        edit.addAction(self.edit_action)
        edit.addAction(self.delete_action)

        help_menu = self.menuBar().addMenu("Help")
        about_act = QAction("About...", self)
        about_act.triggered.connect(self.show_about)
        help_menu.addAction(about_act)

    def show_about(self) -> None:
        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            f"<h4>{APP_NAME} v{APP_VERSION}</h4>"
            "<p>A PySide6 desktop tool for editing, managing and creating Jekyll blog posts.</p>"
            "<p>© 2026 RiffPointer.</p>"
        )

    def show_preferences(self) -> None:
        dlg = PreferencesDialog(self, self.settings)
        if dlg.exec() == QDialog.Accepted:
            self.posts_dir = Path(self.settings.values["posts_data_path"]).expanduser()
            apply_theme(QApplication.instance(), self.settings.values["theme"])
            self.apply_compact_mode(self.settings.values["compact_mode"])
            self.load_posts_data()

    def apply_compact_mode(self, enabled: bool) -> None:
        height = COMPACT_ROW_HEIGHT if enabled else DEFAULT_ROW_HEIGHT
        self.table.verticalHeader().setDefaultSectionSize(height)

    def update_empty_state(self) -> None:
        has_rows = self.model.rowCount() > 0
        self.central_stack.setCurrentWidget(self.table if has_rows else self.empty_label)

    def load_posts_data(self) -> None:
        posts = []
        self.loaded_filepaths.clear()
        if self.posts_dir.exists():
            for path in self.posts_dir.rglob("*"):
                if path.is_file() and path.suffix.lower() in (".md", ".markdown"):
                    try:
                        content = path.read_text(encoding="utf-8")
                        metadata, body = parse_front_matter(content)
                        post = {
                            "file_path": path,
                            "relative_path": str(path.relative_to(self.posts_dir)),
                            "title": metadata.get("title", path.stem),
                            "date": metadata.get("date", ""),
                            "categories": metadata.get("categories", []),
                            "tags": metadata.get("tags", []),
                            "layout": metadata.get("layout", "post"),
                            "excerpt": metadata.get("excerpt", ""),
                            "body": body,
                        }
                        posts.append(post)
                        self.loaded_filepaths.add(path)
                    except Exception as e:
                        print(f"Error loading post {path}: {e}")
            posts.sort(key=lambda x: str(x.get("date", "")), reverse=True)
            
        self.model.set_posts(posts)
        self.undo_stack.clear()
        self.dirty = False
        self._sync_dirty_state()
        self.statusBar().showMessage(f"Loaded {len(posts)} posts from {self.posts_dir}", 6000)

    def save_posts(self) -> bool:
        saved_filepaths: set[Path] = set()
        try:
            self.posts_dir.mkdir(parents=True, exist_ok=True)
            for post in self.model.posts:
                target_path = get_target_filepath(post, self.posts_dir)
                
                metadata = {
                    "layout": post.get("layout", "post"),
                    "title": post.get("title", ""),
                    "date": post.get("date", ""),
                    "categories": post.get("categories", []),
                    "tags": post.get("tags", []),
                }
                if post.get("excerpt"):
                    metadata["excerpt"] = post["excerpt"]
                    
                body = post.get("body", "")
                payload = serialize_front_matter(metadata, body)
                
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(payload, encoding="utf-8")
                
                orig_path = post.get("file_path")
                if orig_path and Path(orig_path) != target_path:
                    try:
                        Path(orig_path).unlink(missing_ok=True)
                    except OSError:
                        pass
                
                post["file_path"] = target_path
                post["relative_path"] = str(target_path.relative_to(self.posts_dir))
                saved_filepaths.add(target_path)
                
            for prev_path in self.loaded_filepaths:
                if prev_path not in saved_filepaths:
                    try:
                        prev_path.unlink(missing_ok=True)
                    except OSError:
                        pass
                        
            self.loaded_filepaths = saved_filepaths
            self.undo_stack.setClean()
            self._sync_dirty_state()
            self.model.layoutChanged.emit()
            self.statusBar().showMessage(f"Saved {len(self.model.posts)} posts", 6000)
            return True
        except OSError as exc:
            QMessageBox.critical(self, "Unable to Save Posts", f"Could not save posts:\n\n{exc}")
            return False

    def reload_posts(self) -> None:
        if self.dirty:
            res = QMessageBox.question(
                self,
                "Discard Changes?",
                "You have unsaved changes. Do you want to discard them and reload from disk?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if res != QMessageBox.Yes:
                return
        self.load_posts_data()

    def new_post(self) -> None:
        dlg = PostDialog(self)
        if dlg.exec() == QDialog.Accepted:
            post = dlg.get_post_data()
            cmd = AddPostCommand(self, post)
            self.undo_stack.push(cmd)

    def edit_selected_post(self) -> None:
        indexes = self.table.selectionModel().selectedRows()
        if not indexes:
            return
        proxy_idx = indexes[0]
        source_idx = self.proxy.mapToSource(proxy_idx)
        row = source_idx.row()
        post = self.model.posts[row]
        
        dlg = PostDialog(self, post)
        if dlg.exec() == QDialog.Accepted:
            new_post = dlg.get_post_data()
            cmd = EditPostCommand(self, row, post, new_post)
            self.undo_stack.push(cmd)

    def delete_selected_post(self) -> None:
        indexes = self.table.selectionModel().selectedRows()
        if not indexes:
            return
            
        if self.settings.values["confirm_delete"]:
            count = len(indexes)
            word = "post" if count == 1 else "posts"
            res = QMessageBox.question(
                self,
                "Delete Confirmation",
                f"Are you sure you want to delete the selected {count} {word}?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if res != QMessageBox.Yes:
                return

        rows = sorted([self.proxy.mapToSource(idx).row() for idx in indexes], reverse=True)
        self.undo_stack.beginMacro("Delete Items")
        for row in rows:
            post = self.model.posts[row]
            cmd = DeletePostCommand(self, row, post)
            self.undo_stack.push(cmd)
        self.undo_stack.endMacro()

    def show_context_menu(self, pos) -> None:
        menu = QMenu(self)
        menu.addAction(self.new_action)
        
        has_selection = bool(self.table.selectionModel().selectedRows())
        if has_selection:
            menu.addAction(self.edit_action)
            menu.addAction(self.delete_action)
            
        menu.exec(self.table.viewport().mapToGlobal(pos))

    def closeEvent(self, event) -> None:
        if self.dirty:
            res = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save them before exiting?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            )
            if res == QMessageBox.Yes:
                if self.save_posts():
                    event.accept()
                else:
                    event.ignore()
            elif res == QMessageBox.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.adjust_column_widths()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.adjust_column_widths()

    def adjust_column_widths(self) -> None:
        table_width = self.table.width()
        if table_width > 100:
            target_width = int(table_width * 0.33)
            if self.table.columnWidth(0) < target_width:
                self.table.setColumnWidth(0, target_width)

    def _sync_dirty_state(self, *_args: object) -> None:
        self.dirty = not self.undo_stack.isClean()
        title = f"{APP_NAME}*" if self.dirty else APP_NAME
        self.setWindowTitle(title)

    def _sync_selection_actions(self) -> None:
        has_selection = bool(self.table.selectionModel().selectedRows())
        self.edit_action.setEnabled(has_selection)
        self.delete_action.setEnabled(has_selection)


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORG_NAME)
    
    global NATIVE_STYLE
    NATIVE_STYLE = app.style().objectName()
    
    settings = SettingsManager()
    apply_theme(app, settings.values.get("theme", "auto"))
    
    # Gracefully exit on KeyboardInterrupt (Ctrl+C)
    signal.signal(signal.SIGINT, lambda sig, frame: app.quit())
    timer = QTimer()
    timer.start(200)
    timer.timeout.connect(lambda: None)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
