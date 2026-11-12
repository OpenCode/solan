# Copyright 2019 Francesco Apruzzese <cescoap@gmail.com>
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import io
import os
import sys
from datetime import datetime
from html import escape
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler
from urllib.parse import quote, unquote, urlsplit

CATEGORIES = {
    "image": {"jpg", "jpeg", "png", "gif", "bmp", "svg", "webp", "heic", "ico", "tif", "tiff"},
    "video": {"mp4", "mkv", "avi", "mov", "webm", "wmv", "flv", "m4v"},
    "audio": {"mp3", "wav", "flac", "ogg", "m4a", "aac", "opus"},
    "archive": {"zip", "tar", "gz", "bz2", "xz", "7z", "rar", "tgz", "zst"},
    "doc": {"pdf", "doc", "docx", "odt", "txt", "md", "rtf", "xls", "xlsx", "ods", "csv", "ppt", "pptx", "odp", "epub"},
    "code": {
        "py",
        "js",
        "ts",
        "html",
        "css",
        "json",
        "xml",
        "yml",
        "yaml",
        "sh",
        "c",
        "cpp",
        "h",
        "java",
        "go",
        "rs",
        "rb",
        "php",
        "sql",
        "toml",
        "ini",
    },
}

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · Solan</title>
<style>
:root {{
  --bg: #f5f6fa; --card: #fff; --text: #1f2330; --muted: #6b7185;
  --border: #e4e6ee; --hover: #f0f2f8; --accent: #4f6bed;
  --folder: #f0b429; --image: #e5508a; --video: #8e5cf0;
  --audio: #12a594; --archive: #c97a2b; --doc: #4f6bed;
  --code: #2f9e44; --file: #8a90a3;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #14161d; --card: #1c1f29; --text: #e8eaf2; --muted: #9298ab;
    --border: #2a2e3b; --hover: #242836; --accent: #7d93ff;
  }}
}}
* {{ box-sizing: border-box; }}
[hidden] {{ display: none !important; }}
body {{
  margin: 0; background: var(--bg); color: var(--text);
  font: 15px/1.5 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
}}
.wrap {{ max-width: 960px; margin: 0 auto; padding: 32px 16px 48px; }}
header {{ display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }}
.logo {{
  width: 40px; height: 40px; border-radius: 12px; background: var(--accent);
  color: #fff; display: grid; place-items: center; font-weight: 700;
  font-size: 20px; flex: none;
}}
h1 {{ font-size: 20px; margin: 0; }}
.sub {{ color: var(--muted); font-size: 13px; }}
.bar {{
  display: flex; gap: 12px; align-items: center; flex-wrap: wrap;
  margin-bottom: 12px;
}}
.crumbs {{ flex: 1; min-width: 0; font-size: 14px; overflow-wrap: anywhere; }}
.crumbs a {{ color: var(--accent); text-decoration: none; }}
.crumbs a:hover {{ text-decoration: underline; }}
.crumbs span {{ color: var(--muted); margin: 0 6px; }}
input[type=search] {{
  width: 220px; max-width: 100%; padding: 8px 12px; border-radius: 10px;
  border: 1px solid var(--border); background: var(--card);
  color: var(--text); font: inherit;
}}
input[type=search]:focus {{ outline: 2px solid var(--accent); border-color: transparent; }}
.card {{
  background: var(--card); border: 1px solid var(--border);
  border-radius: 14px; overflow: hidden;
}}
.row {{
  display: grid; grid-template-columns: 36px 1fr 90px 150px 40px;
  align-items: center; gap: 12px; padding: 10px 16px;
  border-top: 1px solid var(--border); color: inherit; text-decoration: none;
}}
.row:first-child {{ border-top: 0; }}
a.row:hover {{ background: var(--hover); }}
.head {{
  color: var(--muted); font-size: 12px; text-transform: uppercase;
  letter-spacing: .04em; padding-top: 12px; padding-bottom: 12px;
}}
.icon {{
  width: 36px; height: 36px; border-radius: 9px; display: grid;
  place-items: center; color: #fff; font-size: 10px; font-weight: 700;
  text-transform: uppercase; overflow: hidden;
}}
.icon svg {{ width: 20px; height: 20px; }}
.name {{ min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
.size, .date {{ color: var(--muted); font-size: 13px; text-align: right; }}
.dl {{
  width: 32px; height: 32px; border-radius: 8px; display: grid;
  place-items: center; color: var(--muted);
}}
.dl:hover {{ background: var(--border); color: var(--accent); }}
.dl svg {{ width: 18px; height: 18px; }}
.empty {{ padding: 40px 16px; text-align: center; color: var(--muted); }}
footer {{ margin-top: 16px; color: var(--muted); font-size: 12px; text-align: center; }}
.meta {{ display: none; color: var(--muted); font-size: 12px; }}
@media (max-width: 640px) {{
  .row {{ grid-template-columns: 36px 1fr 40px; }}
  .size, .date {{ display: none; }}
  .meta {{ display: block; }}
  input[type=search] {{ width: 100%; }}
}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="logo">S</div>
    <div>
      <h1>{title}</h1>
      <div class="sub">{summary}</div>
    </div>
  </header>
  <div class="bar">
    <nav class="crumbs">{crumbs}</nav>
    <input type="search" id="q" placeholder="Search files…"
           aria-label="Search files" autocomplete="off">
  </div>
  <div class="card" id="list">
    <div class="row head"><span></span><span>Name</span>
      <span class="size">Size</span><span class="date">Modified</span>
      <span></span></div>
    {rows}
    <div class="empty" id="none" hidden>No matching files</div>
  </div>
  <footer>Shared with Solan</footer>
</div>
<script>
const q = document.getElementById('q');
const rows = [...document.querySelectorAll('.entry')];
const none = document.getElementById('none');
q.addEventListener('input', () => {{
  const t = q.value.trim().toLowerCase();
  let shown = 0;
  rows.forEach(r => {{
    const ok = r.dataset.name.includes(t);
    r.hidden = !ok; shown += ok;
  }});
  none.hidden = shown > 0 || rows.length === 0;
}});
</script>
</body>
</html>
"""

FOLDER_SVG = (
    '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 6.5A2.5'
    " 2.5 0 0 1 5.5 4h3.6l2 2h7.4A2.5 2.5 0 0 1 21 8.5v9a2.5 2.5 0 0"
    ' 1-2.5 2.5h-13A2.5 2.5 0 0 1 3 17.5z"/></svg>'
)
UP_SVG = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M12 19V5M5 12l7-7 7 7"/></svg>'
)
DOWNLOAD_SVG = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" '
    'stroke-linejoin="round"><path d="M12 4v11m-5-5 5 5 5-5M5 '
    '20h14"/></svg>'
)


def human_size(size):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024


def category(name):
    ext = os.path.splitext(name)[1].lstrip(".").lower()
    for cat, exts in CATEGORIES.items():
        if ext in exts:
            return cat, ext
    return "file", ext


class SolanHandler(SimpleHTTPRequestHandler):
    """Static file handler with a friendlier directory listing."""

    def list_directory(self, path):
        try:
            names = os.listdir(path)
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "No permission to list directory")
            return None
        url_path = unquote(urlsplit(self.path).path, errors="surrogatepass")

        entries = []
        for name in names:
            full = os.path.join(path, name)
            try:
                st = os.stat(full)
            except OSError:
                continue
            entries.append((os.path.isdir(full), name, st))
        # Folders first, then case-insensitive alphabetical order
        entries.sort(key=lambda e: (not e[0], e[1].lower()))

        rows = []
        if url_path.rstrip("/"):
            rows.append(
                '<a class="row" href="../">'
                '<span class="icon" style="background:var(--file)">'
                f'{UP_SVG}</span><span class="name">Parent folder</span>'
                '<span class="size"></span><span class="date"></span>'
                "<span></span></a>"
            )
        n_dirs = n_files = 0
        for is_dir, name, st in entries:
            href = quote(name, errors="surrogatepass") + ("/" if is_dir else "")
            label = escape(name, quote=False)
            date = datetime.fromtimestamp(st.st_mtime).strftime("%d %b %Y, %H:%M")
            if is_dir:
                n_dirs += 1
                icon = f'<span class="icon" style="background:var(--folder)">{FOLDER_SVG}</span>'
                size = "—"
                action = "<span></span>"
            else:
                n_files += 1
                cat, ext = category(name)
                icon = f'<span class="icon" style="background:var(--{cat})">{escape(ext[:4]) or "file"}</span>'
                size = human_size(st.st_size)
                action = (
                    f'<a class="dl" href="{href}" download '
                    f'title="Download {escape(name)}" '
                    f'aria-label="Download {escape(name)}">'
                    f"{DOWNLOAD_SVG}</a>"
                )
            rows.append(
                f'<div class="row entry" '
                f'data-name="{escape(name.lower())}">{icon}'
                f'<a class="name" href="{href}" style="color:inherit;'
                f'text-decoration:none">{label}'
                f'<span class="meta">'
                f"{date if is_dir else f'{size} · {date}'}</span></a>"
                f'<span class="size">{size}</span>'
                f'<span class="date">{date}</span>{action}</div>'
            )
        if not entries:
            rows.append('<div class="empty">This folder is empty</div>')

        # Breadcrumbs
        parts = [p for p in url_path.split("/") if p]
        crumbs = ['<a href="/">Home</a>']
        for i, part in enumerate(parts):
            href = "/" + "/".join(quote(p) for p in parts[: i + 1]) + "/"
            crumbs.append(f'<span>/</span><a href="{href}">{escape(part, quote=False)}</a>')

        title = escape(parts[-1] if parts else os.path.basename(os.path.abspath(self.directory)) or "/", quote=False)
        summary = f"{n_dirs} folder{'s' * (n_dirs != 1)} · {n_files} file{'s' * (n_files != 1)}"

        enc = sys.getfilesystemencoding()
        body = PAGE.format(title=title, summary=summary, crumbs="".join(crumbs), rows="".join(rows))
        encoded = body.encode(enc, "surrogateescape")
        f = io.BytesIO(encoded)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", f"text/html; charset={enc}")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return f
