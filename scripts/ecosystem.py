#!/usr/bin/env python3
"""Build the Valen ecosystem diagram as self-contained SVGs (English and Chinese, light and dark).

    python3 scripts/ecosystem.py            # writes profile/assets/valen-ecosystem*.svg

Needs fonttools[woff], brotli and Pillow. Logos and fonts are downloaded once from pinned
sources into ~/.cache/valen-ecosystem and embedded in each SVG, so the files render the
same on GitHub and Hugging Face without loading anything else.
"""
import base64
import io
import re
import sys
import urllib.request
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from PIL import Image

REPO = Path(__file__).resolve().parent.parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "profile" / "assets"
CACHE = Path.home() / ".cache" / "valen-ecosystem"

GF = "https://raw.githubusercontent.com/google/fonts/cc39c4c2c304bc368c9b7c311ea2bcc6013299fe/ofl/"
GH = "https://raw.githubusercontent.com/"
PREFIXES = {
    "lobe/": "https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@1.102.0/icons/",
    "si/": "https://cdn.jsdelivr.net/npm/simple-icons@16.38.0/icons/",
    "lucide/": "https://cdn.jsdelivr.net/npm/lucide-static@0.460.0/icons/",
}
URLS = {
    "fonts/Montserrat.ttf": GF + "montserrat/Montserrat%5Bwght%5D.ttf",
    "fonts/DMSans.ttf": GF + "dmsans/DMSans%5Bopsz,wght%5D.ttf",
    "fonts/DMMono-Medium.ttf": GF + "dmmono/DMMono-Medium.ttf",
    "fonts/NotoSansSC.ttf": GF + "notosanssc/NotoSansSC%5Bwght%5D.ttf",
    "other/sglang-square.png": GH + "sgl-project/sglang/b947a615f62bbb31e3b5e5165674930eef0cef33/assets/logo_square.png",
    "other/ggml.png": "https://avatars.githubusercontent.com/ggml-org?s=128",
    "other/roller-logo.png": GH + "Valen-Team/Roller/d6c91d7ecf53d06d81d95ba480e2d40cdf8f3e5a/assets/roller-logo.png",
    "other/roller-logo-dark.png": GH + "Valen-Team/Roller/d6c91d7ecf53d06d81d95ba480e2d40cdf8f3e5a/assets/roller-logo-dark.png",
}


def src(rel):
    """Local path of a logo or font, downloaded from its pinned source on first use."""
    if rel == "other/valen-mark.jpg":
        return REPO / "profile" / "assets" / "logo-new.jpg"
    path = CACHE / rel
    if not path.exists():
        prefix = next((p for p in PREFIXES if rel.startswith(p)), None)
        url = PREFIXES[prefix] + rel[len(prefix):] if prefix else URLS[rel]
        path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, path)
    return path

W = 1600

THEMES = {
    "light": dict(
        canvas="#F6F3EE", panel="#FFFFFF", line="#E4E1DB", line_soft="#ECE9E3",
        core="#E8EEFF", core_line="#B9C8FD", sub="#FFFFFF", chip="#F6F3EE",
        text="#1E232C", heading="#152443", muted="#696C72",
        primary="#3964FE", primary_text="#2B50DB", tile="#E8EEFF", tile_neutral="#EFEBE4",
        mono="#1E232C", track="#E6EAF5", roller="other/roller-logo.png",
    ),
    "dark": dict(
        canvas="#1B1B1D", panel="#232326", line="#36373D", line_soft="#2F3036",
        core="#22283D", core_line="#3E4D80", sub="#1D2030", chip="#2A2D3A",
        text="#E3E3E3", heading="#F0F2F8", muted="#A2A4AA",
        primary="#6B8BFF", primary_text="#86A0FF", tile="#2C3654", tile_neutral="#33343A",
        mono="#E3E3E3", track="#33395A", roller="other/roller-logo-dark.png",
    ),
}

PAPER = dict(route="#C3C9B2", adapt="#D9B8B0", evidence="#CAD3D4", select="#DDB878", verify="#E3A08A")

# ---------------------------------------------------------------- fonts

FONT_SPECS = {  # the website's DM Sans is the 9pt optical size
    ("display", 700): ("Montserrat.ttf", {"wght": 700}),
    ("body", 400): ("DMSans.ttf", {"opsz": 9, "wght": 400}),
    ("body", 500): ("DMSans.ttf", {"opsz": 9, "wght": 500}),
    ("body", 700): ("DMSans.ttf", {"opsz": 9, "wght": 700}),
    ("mono", 500): ("DMMono-Medium.ttf", None),
}
CJK_STACK = "VCJK, 'PingFang SC', 'Microsoft YaHei', 'Noto Sans SC'"
FAMILY = {
    "display": f"VDisplay, {CJK_STACK}, Montserrat, system-ui, sans-serif",
    "body": f"VBody, {CJK_STACK}, 'DM Sans', system-ui, -apple-system, 'Segoe UI', sans-serif",
    "mono": f"VMono, {CJK_STACK}, 'DM Mono', ui-monospace, Menlo, Consolas, monospace",
}
CJK_FILE = "NotoSansSC.ttf"
LANG = "en"
ZH = {}


def tr(s):
    return ZH.get(s, s) if LANG == "zh" else s
_fonts = {}


def font(key):
    if key not in _fonts:
        file, axes = FONT_SPECS[key]
        f = TTFont(src("fonts/" + file))
        if axes:
            f = instancer.instantiateVariableFont(f, axes)
        _fonts[key] = f
    return _fonts[key]


USED = {k: set() for k in FONT_SPECS}
USED_CJK = {400: set(), 500: set(), 700: set()}


def measure(s, size, fam="body", wt=400, ls=0.0):
    s = tr(s)
    f = font((fam, wt))
    cmap, hmtx, upm = f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm
    total = 0
    for ch in s:
        g = cmap.get(ord(ch))
        total += hmtx[g][0] if g else upm  # CJK glyphs are one em wide
    return total * size / upm + ls * len(s)


def cjk_faces():
    wanted = {w: c for w, c in USED_CJK.items() if c}
    if not wanted:
        return ""
    base = TTFont(src("fonts/" + CJK_FILE))
    opts = subset.Options()
    opts.name_IDs = []
    sub_ = subset.Subsetter(opts)
    sub_.populate(text="".join(sorted(set().union(*wanted.values()))))
    sub_.subset(base)
    buf = io.BytesIO()
    base.save(buf)
    css = []
    for w, chars in wanted.items():
        buf.seek(0)
        f = instancer.instantiateVariableFont(TTFont(buf), {"wght": w})
        s2 = subset.Subsetter(opts)
        s2.populate(text="".join(sorted(chars)))
        s2.subset(f)
        f.flavor = "woff2"
        out = io.BytesIO()
        f.save(out)
        b64 = base64.b64encode(out.getvalue()).decode()
        css.append(f"@font-face{{font-family:VCJK;font-weight:{w};src:url(data:font/woff2;base64,{b64}) format('woff2')}}")
    return "".join(css)


def font_face_css():
    css = []
    for (fam, wt), _ in FONT_SPECS.items():
        chars = USED[(fam, wt)]
        if not chars:
            continue
        f = font((fam, wt))
        buf = io.BytesIO()
        f.save(buf)
        buf.seek(0)
        sub = TTFont(buf)
        opts = subset.Options()
        opts.flavor = "woff2"
        opts.layout_features = ["kern", "liga"]
        opts.name_IDs = []
        opts.notdef_outline = True
        sub_ = subset.Subsetter(opts)
        sub_.populate(text="".join(sorted(chars)) + " ")
        sub_.subset(sub)
        out = io.BytesIO()
        sub.flavor = "woff2"
        sub.save(out)
        b64 = base64.b64encode(out.getvalue()).decode()
        name = {"display": "VDisplay", "body": "VBody", "mono": "VMono"}[fam]
        css.append(
            f"@font-face{{font-family:{name};font-weight:{wt};"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}"
        )
    return "".join(css) + cjk_faces()


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=17, fam="body", wt=400, fill="text", anchor="start", ls=0.0, opacity=None):
    s = tr(s)
    cmap = font((fam, wt)).getBestCmap()
    for ch in s:
        if ord(ch) in cmap:
            USED[(fam, wt)].add(ch)
        else:
            USED_CJK[{400: 400, 500: 500}.get(wt, 700)].add(ch)
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    l = f' letter-spacing="{ls}"' if ls else ""
    o = f' opacity="{opacity}"' if opacity else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FAMILY[fam]}" font-size="{size}" '
            f'font-weight="{wt}" fill="{C[fill] if fill in C else fill}"{a}{l}{o}>{esc(s)}</text>')


# ---------------------------------------------------------------- icons

ICONS = {
    # lobehub/icons-static-svg (colour or currentColor)
    "claudecode": "lobe/claudecode-color.svg", "codex": "lobe/codex-color.svg", "cursor": "lobe/cursor.svg",
    "n8n": "lobe/n8n-color.svg", "langchain": "lobe/langchain-color.svg", "dify": "lobe/dify-color.svg",
    "coze": "lobe/coze.svg", "hf": "lobe/huggingface-color.svg", "vllm": "lobe/vllm-color.svg",
    "ollama": "lobe/ollama.svg", "qwen": "lobe/qwen-color.svg", "openai": "lobe/openai.svg",
    "claude": "lobe/claude-color.svg", "gemini": "lobe/gemini-color.svg", "openclaw": "lobe/openclaw-color.svg",
    "hermes": "lobe/hermesagent.svg", "opencode": "lobe/opencode.svg", "deepseek": "lobe/deepseek-color.svg",
    # simple-icons (filled with the brand colour)
    "python": ("si/python.svg", "#3776AB"), "cpp": ("si/cplusplus.svg", "#00599C"),
    "onnx": ("si/onnx.svg", "#005CED"), "docker": ("si/docker.svg", "#2496ED"),
    "javascript": ("si/javascript.svg", "#F7DF1E", "#1E232C"), "typescript": ("si/typescript.svg", "#3178C6", "#FFFFFF"),
}
PNGS = {"sglang": "other/sglang-square.png"}
MONO_PNGS = {"ggml": "other/ggml.png"}


def _parts(path):
    raw = src(path).read_text()
    raw = re.sub(r"<!--.*?-->", "", raw, flags=re.S)
    m = re.search(r"<svg\b([^>]*)>(.*)</svg>", raw, re.S)
    attrs, inner = m.groups()
    inner = re.sub(r"<title>.*?</title>", "", inner, flags=re.S).strip()
    inner = re.sub(r"\s+", " ", inner)
    vb = re.search(r'viewBox="([^"]+)"', attrs).group(1)
    keep = {}
    for k in ("fill", "stroke", "stroke-width", "stroke-linecap", "stroke-linejoin", "fill-rule", "clip-rule"):
        mm = re.search(rf'\s{k}="([^"]+)"', attrs)
        if mm:
            keep[k] = mm.group(1)
    return vb, keep, inner


def svg_icon(path, x, y, s, color, fill=None, stroke_width=None):
    vb, keep, inner = _parts(path)
    if fill:
        keep["fill"] = fill
    if stroke_width:
        keep["stroke-width"] = stroke_width
    a = "".join(f' {k}="{v}"' for k, v in keep.items())
    return f'<svg x="{x:.1f}" y="{y:.1f}" width="{s}" height="{s}" viewBox="{vb}"{a} color="{color}">{inner}</svg>'


_png_cache = {}


def png_data(path, px, mono=None):
    key = (path, px, mono)
    if key not in _png_cache:
        im = Image.open(src(path)).convert("RGBA")
        im.thumbnail((px, px), Image.LANCZOS)
        if mono:  # dark-on-white mark: ink becomes alpha, painted in the theme colour
            r, g, b = (int(mono[i:i + 2], 16) for i in (1, 3, 5))
            alpha = im.convert("L").point(lambda v: 255 - v)
            im = Image.new("RGBA", im.size, (r, g, b, 255))
            im.putalpha(alpha)
        buf = io.BytesIO()
        im.save(buf, "PNG", optimize=True)
        _png_cache[key] = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    return _png_cache[key]


def image(path, x, y, w, h, px=None, mono=None):
    return (f'<image x="{x:.1f}" y="{y:.1f}" width="{w}" height="{h}" '
            f'href="{png_data(path, px or int(max(w, h) * 3), mono)}"/>')


def logo(key, x, y, s):
    """Third-party or project logo, drawn in an s x s box."""
    if key in PNGS:
        return image(PNGS[key], x, y, s, s)
    if key in MONO_PNGS:
        return image(MONO_PNGS[key], x, y, s, s, mono=C["mono"])
    spec = ICONS[key]
    if isinstance(spec, tuple):
        path, brand = spec[0], spec[1]
        under = ""
        if len(spec) > 2:  # letters cut out of a square: put the letter colour behind them
            under = f'<rect x="{x + s * .1:.1f}" y="{y + s * .1:.1f}" width="{s * .8:.1f}" height="{s * .8:.1f}" fill="{spec[2]}"/>'
        return under + svg_icon(path, x, y, s, C["mono"], fill=brand)
    return svg_icon(spec, x, y, s, C["mono"])


def lucide(name, x, y, s, color="primary", sw=2):
    return svg_icon(f"lucide/{name}.svg", x, y, s, C[color] if color in C else color, stroke_width=sw)


def tile(name, x, y, s, neutral=False):
    """Valen's own resources: a Lucide icon on a soft blue tile."""
    bg = C["tile_neutral"] if neutral else C["tile"]
    col = "muted" if neutral else "primary"
    pad = s * 0.2
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{s}" height="{s}" rx="{s * .26:.1f}" fill="{bg}"/>'
            + lucide(name, x + pad, y + pad, s - 2 * pad, col, sw=2.2))


def jevalkit_mark(x, y, s):
    k = s / 96
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.4f})">'
            '<rect x="1.5" y="1.5" width="93" height="93" rx="23" fill="#E7F7F2" stroke="#009C83" stroke-width="3"/>'
            '<g fill="#009C83"><circle cx="22" cy="27" r="4"/><rect x="34" y="23" width="40" height="8" rx="4"/>'
            '<circle cx="22" cy="47" r="4"/><rect x="34" y="43" width="27" height="8" rx="4" opacity=".7"/>'
            '<circle cx="22" cy="67" r="4"/><rect x="34" y="63" width="16" height="8" rx="4" opacity=".45"/>'
            '<circle cx="79" cy="79" r="18"/></g>'
            '<path d="m71 79 5.5 5.5L87 73" fill="none" stroke="#E7F7F2" stroke-width="4" '
            'stroke-linecap="round" stroke-linejoin="round"/></g>')


def valen_mark(x, y, s):
    """The Valen V keeps its white carrier surface."""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{s}" height="{s}" rx="{s * .24:.1f}" fill="#FFFFFF" stroke="{C["core_line"]}"/>'
            + image("other/valen-mark.jpg", x + 2, y + 2, s - 4, s - 4))


def pi_mark(x, y, s):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{s}" height="{s}" rx="{s * .24:.1f}" fill="{C["mono"]}"/>'
            + text(x + s / 2, y + s * .74, "π", s * .78, "body", 700, C["panel"], "middle"))


# ---------------------------------------------------------------- primitives


def rect(x, y, w, h, r=16, fill="panel", stroke="line", sw=1, dash=None, extra=""):
    f = C.get(fill, fill)
    s = C.get(stroke, stroke)
    d = f' stroke-dasharray="{dash}"' if dash else ""
    st = f' stroke="{s}" stroke-width="{sw}"' if stroke else ""
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" fill="{f}"{st}{d}{extra}/>'


def label(x, y, s, paper):
    """Section label: paper-colour swatch + small caps."""
    return (rect(x, y - 11, 12, 12, 3, PAPER[paper], None)
            + text(x + 20, y, tr(s).upper() if LANG == "en" else tr(s), 14, "body", 700, "muted", ls=1.4))


def chip(x, y, s, h=30, size=15, fam="body", wt=500, fill="chip", stroke="line", color="text", icon=None, dash=None):
    tw = measure(s, size, fam, wt)
    pad = 12
    iw = 0
    out = []
    if icon:
        iw = h - 12 + 7
    w = tw + 2 * pad + iw
    out.append(rect(x, y, w, h, h / 2, fill, stroke, dash=dash))
    if icon:
        out.append(icon(x + pad - 2, y + 6, h - 12))
    out.append(text(x + pad + iw, y + h / 2 + size * .36, s, size, fam, wt, color))
    return "".join(out), w


def item(x, cy, name, ico, size=17, wt=500, isz=24, gap=10):
    return ico(x, cy - isz / 2, isz) + text(x + isz + gap, cy + size * .36, name, size, "body", wt, "text")


def item_w(name, size=17, wt=500, isz=24, gap=10):
    return isz + gap + measure(name, size, "body", wt)


def arrow(x1, y1, x2, y2, color="primary", dash=None, sw=2, head=True):
    c = C.get(color, color)
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = ' marker-end="url(#ah)"' if head else ""
    return f'<path d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}" stroke="{c}" stroke-width="{sw}" fill="none"{d}{m}/>'


# ---------------------------------------------------------------- sections

LX, LW = 32, 260
CX, CW = 328, 944
RX, RW = 1308, 260
TY, TH = 32, 160
CY, CH = 228, 500
BY, BH = 764, 300
H = BY + BH + 32


def build_band():
    x0, w0 = LX, RX + RW - LX
    out = [rect(x0, TY, w0, TH), label(x0 + 24, TY + 34, "Build with Valen", "route")]
    groups = [
        ("Agent skill", [("Claude Code", "claudecode"), ("Codex", "codex"), ("Cursor", "cursor"),
                         ("Other agents", ("tile", "terminal"))]),
        ("Workflows", [("n8n", "n8n"), ("LangChain", "langchain"), ("Dify", "dify"), ("Coze", "coze")]),
        ("SDKs", [("Python", "python"), ("JavaScript", "javascript"), ("TypeScript", "typescript"), ("C++", "cpp")]),
        ("Web & docs", [("Web chat", ("tile", "message-square")), ("Playground", "hf"),
                        ("OpenAPI", ("tile", "braces")), ("llms.txt", ("tile", "file-text"))]),
        ("Community", [("vLLM Jev", ("tile", "git-branch")), ("System1-Omni", ("tile", "git-branch")),
                       ("JevLight", ("tile", "git-branch")), ("tasksource", ("tile", "git-branch"))]),
    ]
    colgap = 20
    widths = []
    for title, items in groups:
        c1 = max(item_w(n) for n, _ in items[0::2])
        c2 = max(item_w(n) for n, _ in items[1::2])
        widths.append((c1, c2, max(c1 + colgap + c2, measure(title, 16, "body", 700))))
    inner = w0 - 48
    spare = (inner - sum(w for *_, w in widths)) / (len(groups) - 1)
    x = x0 + 24
    for gi, ((title, items), (c1, c2, gw)) in enumerate(zip(groups, widths)):
        out.append(text(x, TY + 70, title, 16, "body", 700, "heading"))
        for i, (name, key) in enumerate(items):
            ix = x + (0 if i % 2 == 0 else c1 + colgap)
            cy = TY + 98 + (i // 2) * 38
            neutral = gi == len(groups) - 1
            ico = (lambda k, n=neutral: (lambda a, b, s: tile(k[1], a, b, s, n)))(key) if isinstance(key, tuple) else \
                (lambda k: (lambda a, b, s: logo(k, a, b, s)))(key)
            out.append(item(ix, cy, name, ico))
        if gi < len(groups) - 1:
            sx = x + gw + spare / 2
            out.append(f'<path d="M{sx:.1f} {TY + 52} V{TY + TH - 16}" stroke="{C["line"]}" stroke-width="1"/>')
        x += gw + spare
    return "".join(out)


def subpanel(x, y, w, h, title, caption=None):
    out = [rect(x, y, w, h, 14, "sub", "core_line"), text(x + 18, y + 30, title, 16, "body", 700, "heading")]
    if caption:
        out.append(text(x + w - 18, y + 30, caption, 14, "body", 500, "muted", "end"))
    return "".join(out)


def build_core():
    out = [rect(CX, CY, CW, CH, 20, "core", "core_line", 1.5)]
    out.append(valen_mark(CX + 24, CY + 22, 56))
    out.append(text(CX + 96, CY + 52, "Valen-Decision-1.5", 30, "display", 700, "heading", ls=-0.6))
    out.append(text(CX + 97, CY + 76, "Multimodal System One decision model", 17, "body", 500, "muted"))
    # sizes and formats
    sizes = ["0.8B", "2B", "4B", "9B", "27B"]
    x = CX + CW - 24
    pills = []
    for s in reversed(sizes):
        w = measure(s, 15, "body", 700) + 22
        x -= w
        pills.append(rect(x, CY + 24, w, 28, 14, "primary", None)
                     + text(x + w / 2, CY + 24 + 14 + 5.4, s, 15, "body", 700, "#FFFFFF", "middle"))
        x -= 6
    out += pills
    out.append(text(CX + CW - 24, CY + 78, "Transformers · ONNX · GGUF", 15, "body", 500, "muted", "end"))

    # flow row
    fy, fh = CY + 100, 222
    ws = [252, 300, 300]
    gap = (CW - 48 - sum(ws)) / 2
    xs = [CX + 24, CX + 24 + ws[0] + gap, CX + 24 + ws[0] + gap + ws[1] + gap]

    out.append(subpanel(xs[0], fy, ws[0], fh, "Inputs"))
    rows = [("Text", "type"), ("Images", "image"), ("Video", "film")]
    for i, (n, ic) in enumerate(rows):
        out.append(item(xs[0] + 18, fy + 64 + i * 36, n, lambda a, b, s, ic=ic: tile(ic, a, b, s), isz=26))
    out.append(f'<path d="M{xs[0] + 18} {fy + 164} H{xs[0] + ws[0] - 18}" stroke="{C["line"]}" stroke-dasharray="3 4"/>')
    out.append(item(xs[0] + 18, fy + 192, "Questions + candidates", lambda a, b, s: tile("list-checks", a, b, s), size=16, isz=26))

    out.append(subpanel(xs[1], fy, ws[1], fh, "Decision model"))
    rows = [
        ("Qwen3.5 backbone", lambda a, b, s: logo("qwen", a + 2, b + 2, s - 4)),
        ("Block-bidirectional attention", lambda a, b, s: tile("layers", a, b, s)),
        ("Dual head: decisions + bbox", lambda a, b, s: tile("split", a, b, s)),
        ("One forward pass, shared state", lambda a, b, s: tile("zap", a, b, s)),
    ]
    for i, (n, ico) in enumerate(rows):
        out.append(item(xs[1] + 18, fy + 66 + i * 41, n, ico, size=16, isz=26))

    out.append(subpanel(xs[2], fy, ws[2], fh, "Typed answers"))
    rows = [("predicate", "probability"), ("choice", "distribution"),
            ("score", "level probabilities"), ("bbox", "box · point")]
    vx = xs[2] + ws[2] - 18 - 60
    for i, (t, cap) in enumerate(rows):
        cy = fy + 66 + i * 41
        out.append(text(xs[2] + 18, cy + 5.5, t, 16, "mono", 500, "primary_text"))
        out.append(text(xs[2] + 18 + measure(t, 16, "mono", 500) + 10, cy + 5.5, cap, 15, "body", 400, "muted"))
        out.append(mini_viz(t, vx, cy - 11, 60, 22))

    for i in range(2):
        out.append(arrow(xs[i] + ws[i] + 3, fy + fh / 2, xs[i + 1] - 5, fy + fh / 2, sw=2.2))

    # lower row
    ly = fy + fh + 16
    lh = CY + CH - 22 - ly
    lower = [
        ("Protocols", [("/v1/decisions", "braces", "mono"), ("/v1/systemone", "braces", "mono"),
                       ("OpenAPI spec", "file-text", "body")]),
        ("Training & export", [("SFT and LoRA fine-tuning", "wrench", "body"), ("RLCD (experimental)", "flask-conical", "body"),
                               ("ONNX and GGUF export", "box", "body")]),
        ("Thresholds & routing", [("Calibrated thresholds", "gauge", "body"), ("Human-review band", "users", "body"),
                                  ("\u201cNone of these\u201d route", "route", "body")]),
    ]
    for i, (title, rows) in enumerate(lower):
        out.append(subpanel(xs[i], ly, ws[i], lh, title))
        for j, (s, ic, fam) in enumerate(rows):
            cy = ly + 58 + j * 29
            out.append(tile(ic, xs[i] + 18, cy - 11, 22))
            out.append(text(xs[i] + 50, cy + 5.2, s, 15 if fam == "mono" else 15, fam, 500,
                            "primary_text" if fam == "mono" else "text"))
    return "".join(out)


def mini_viz(kind, x, y, w, h):
    p, t = C["primary"], C["track"]
    if kind == "predicate":
        return (rect(x, y + h / 2 - 4, w, 8, 4, t, None) + rect(x, y + h / 2 - 4, w * .82, 8, 4, p, None))
    if kind == "choice":
        out = ""
        for i, v in enumerate((.78, .32, .14)):
            out += rect(x, y + i * 8, w * v, 5, 2.5, p if i == 0 else t, None)
        return out
    if kind == "score":
        out = ""
        vals = (.18, .4, .95, .55, .22)
        bw = (w - 4 * 4) / 5
        for i, v in enumerate(vals):
            bh = h * v
            out += rect(x + i * (bw + 4), y + h - bh, bw, bh, 2, p if i == 2 else t, None)
        return out
    if kind == "bbox":
        return (rect(x + 10, y, w - 20, h, 4, "none", "muted", 1.2)
                + rect(x + 22, y + 4, 26, 14, 2, "none", p, 2)
                + f'<circle cx="{x + 35}" cy="{y + 11}" r="2.4" fill="{p}"/>')
    return ""


def side_rows(x, w, top, bottom, rows):
    out = []
    step = (bottom - top) / len(rows)
    for i, (n, d, ico) in enumerate(rows):
        cy = top + step * (i + .5)
        out.append(ico(x + 20, cy - 16, 32))
        out.append(text(x + 64, cy - 2, n, 17, "body", 700, "text"))
        out.append(text(x + 64, cy + 18, d, 15, "body", 400, "muted"))
        if i:
            out.append(f'<path d="M{x + 22} {top + step * i:.1f} H{x + w - 22}" stroke="{C["line_soft"]}"/>')
    return "".join(out)


def build_left():
    out = [rect(LX, CY, LW, CH), label(LX + 22, CY + 34, "Run anywhere", "adapt")]
    rows = [
        ("Hosted API", "Free, no key", lambda a, b, s: tile("globe", a, b, s)),
        ("Transformers", "Native weights", lambda a, b, s: logo("hf", a, b, s)),
        ("vLLM", "Plugin or Docker image", lambda a, b, s: logo("vllm", a, b, s)),
        ("SGLang", "Plugin or Docker image", lambda a, b, s: logo("sglang", a, b, s)),
        ("ONNX Runtime", "CPU · CUDA · WebGPU", lambda a, b, s: logo("onnx", a, b, s)),
        ("llama.cpp", "Valen-patched · GGUF", lambda a, b, s: logo("ggml", a, b, s)),
        ("Ollama", "Valen-patched · GGUF", lambda a, b, s: logo("ollama", a, b, s)),
    ]
    out.append(side_rows(LX, LW, CY + 52, CY + CH - 8, rows))
    return "".join(out)


def build_right():
    eh = 300
    out = [rect(RX, CY, RW, eh), label(RX + 22, CY + 34, "Evaluate", "evidence")]
    rows = [
        ("JevalKit", "25 model families", lambda a, b, s: jevalkit_mark(a, b, s)),
        ("Leaderboard", "JevalKit on HF Spaces", lambda a, b, s: tile("chart-column", a, b, s)),
        ("VisualDecisionBench", "Image and video subsets", lambda a, b, s: tile("image", a, b, s)),
        ("Jev Decision Index", "Vision and text tracks", lambda a, b, s: tile("trophy", a, b, s, neutral=True)),
    ]
    out.append(side_rows(RX, RW, CY + 50, CY + eh - 6, rows))

    y2 = CY + eh + 16
    h2 = CY + CH - y2
    out.append(rect(RX, y2, RW, h2))
    out.append(label(RX + 22, y2 + 34, "Compare with LLMs", "verify"))
    llms = [("GPT", "openai"), ("Claude", "claude"), ("Gemini", "gemini")]
    cw = (RW - 44) / 3
    for i, (n, k) in enumerate(llms):
        cx = RX + 22 + cw * (i + .5)
        out.append(logo(k, cx - 15, y2 + 60, 30))
        out.append(text(cx, y2 + 114, n, 16, "body", 700, "text", "middle"))
    out.append(text(RX + RW / 2, y2 + 154, "via Valen.llm() and JevalKit", 14, "body", 400, "muted", "middle"))
    return "".join(out)


def build_bottom():
    out = []
    rw = 1088
    x0, y0 = LX, BY
    out.append(rect(x0, y0, rw, BH))
    out.append(label(x0 + 22, y0 + 34, "Agents", "select"))
    out.append(image(C["roller"], x0 + 22, y0 + 52, 44, 44))
    out.append(text(x0 + 78, y0 + 84, "Roller", 26, "display", 700, "heading", ls=-0.4))
    tx = x0 + 78 + measure("Roller", 26, "display", 700) + 18
    out.append(text(tx, y0 + 83, "Agent trajectory collection across models and Harnesses", 16, "body", 500, "muted"))
    cap = "One Docker container per rollout"
    cw_ = measure(cap, 15, "body", 500)
    out.append(logo("docker", x0 + rw - 22 - cw_ - 34, y0 + 64, 26))
    out.append(text(x0 + rw - 22, y0 + 83, cap, 15, "body", 500, "muted", "end"))

    by = y0 + 112
    bh = BH - 112 - 20
    ws = [306, 420, 280]
    gap = (rw - 44 - sum(ws)) / 2
    xs = [x0 + 22, x0 + 22 + ws[0] + gap, x0 + 22 + ws[0] + gap + ws[1] + gap]
    for i, t in enumerate(["Tasks & benchmarks", "Harnesses", "Outputs"]):
        out.append(rect(xs[i], by, ws[i], bh, 14, "canvas", "line_soft"))
        out.append(text(xs[i] + 16, by + 28, t, 15, "body", 700, "heading"))
    out.append(text(xs[1] + ws[1] - 16, by + 28, "Task agent or user simulator", 13, "body", 500, "muted", "end"))
    for i in range(2):
        out.append(arrow(xs[i] + ws[i] + 3, by + bh / 2, xs[i + 1] - 5, by + bh / 2, sw=2.2))

    cx, cy = xs[0] + 16, by + 42
    for s in ["WildClawBench", "SkillsBench", "PinchBench", "QwenClawBench", "SWE-Bench Pro", "Your own tasks"]:
        own = s == "Your own tasks"
        kw = dict(h=28, size=14, wt=500, fill="panel", dash="4 3" if own else None, color="muted" if own else "text")
        svg, w = chip(cx, cy, s, **kw)
        if cx + w > xs[0] + ws[0] - 14:
            cx, cy = xs[0] + 16, cy + 36
            svg, w = chip(cx, cy, s, **kw)
        out.append(svg)
        cx += w + 8

    hs = [("OpenClaw", "openclaw"), ("Codex", "codex"), ("Claude Code", "claudecode"), ("Hermes", "hermes"),
          ("OpenCode", "opencode"), ("DeepSeek", "deepseek"), ("Pi Agent", "pi")]
    cols = 3
    cwid = (ws[1] - 32 - (cols - 1) * 8) / cols
    for i, (n, k) in enumerate(hs):
        hx = xs[1] + 16 + (i % cols) * (cwid + 8)
        hy = by + 42 + (i // cols) * 36
        out.append(rect(hx, hy, cwid, 28, 14, "panel", "line"))
        ico = pi_mark(hx + 6, hy + 5, 18) if k == "pi" else logo(k, hx + 6, hy + 5, 18)
        out.append(ico + text(hx + 31, hy + 19.4, n, 14, "body", 500, "text"))

    outs = [("Native session", "terminal"), ("Unified trace", "list-tree"), ("SFT training data", "database"),
            ("Graded in its container", "circle-check")]
    for i, (n, ic) in enumerate(outs):
        out.append(item(xs[2] + 16, by + 56 + i * 30, n, lambda a, b, s, ic=ic: tile(ic, a, b, s), size=15, isz=22, gap=9))

    ax = x0 + rw + 16
    aw = RX + RW - ax
    out.append(rect(ax, y0, aw, BH))
    out.append(label(ax + 22, y0 + 34, "Recursive self-improvement", "verify"))
    out.append(tile("infinity", ax + 22, y0 + 52, 44))
    out.append(text(ax + 78, y0 + 84, "Awesome-RSI", 26, "display", 700, "heading", ls=-0.4))
    pillars = [("Experience accumulation", "Prompts · context · skills · memory", "layers"),
               ("System modification", "Harnesses · tools · agent architecture", "wrench"),
               ("Model parameters", "Fine-tuning · RL · self-play", "brain")]
    for i, (n, d, ic) in enumerate(pillars):
        py = y0 + 112 + i * 56
        out.append(rect(ax + 22, py, aw - 44, 48, 12, "canvas", "line_soft"))
        out.append(tile(ic, ax + 32, py + 8, 32))
        out.append(text(ax + 76, py + 21, n, 15, "body", 700, "text"))
        out.append(text(ax + 76, py + 39, d, 14, "body", 400, "muted"))
    return "".join(out)


def build_connectors():
    out = []
    mid = CX + CW / 2
    out.append(arrow(mid, TY + TH + 4, mid, CY - 6, dash="5 5"))
    out.append(text(mid + 12, (TY + TH + CY) / 2 + 5, "call /v1/decisions", 14, "mono", 500, "primary_text"))
    yy = CY + CH / 2
    out.append(arrow(LX + LW + 4, yy, CX - 6, yy, dash="4 4"))
    yy = CY + 150
    out.append(arrow(CX + CW + 4, yy, RX - 6, yy, dash="4 4"))
    yy = CY + 400
    out.append(arrow(RX - 4, yy, CX + CW + 6, yy, dash="4 4"))
    gy = (CY + CH + BY) / 2 + 5
    out.append(arrow(mid - 40, CY + CH + 4, mid - 40, BY - 6, dash="5 5"))
    out.append(text(mid - 52, gy, "decisions", 14, "body", 700, "primary_text", "end"))
    out.append(arrow(mid + 40, BY - 4, mid + 40, CY + CH + 6, dash="5 5"))
    out.append(text(mid + 52, gy, "experience & feedback", 14, "body", 700, "primary_text"))
    return "".join(out)


def build(theme, lang):
    global C, LANG
    C, LANG = THEMES[theme], lang
    for k in USED:
        USED[k] = set()
    for k in USED_CJK:
        USED_CJK[k] = set()
    body = "".join([build_band(), build_left(), build_right(), build_core(), build_bottom(), build_connectors()])
    css = font_face_css()
    title, desc = tr("Valen ecosystem"), tr(DESC)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="img" aria-labelledby="t d"><title id="t">{esc(title)}</title><desc id="d">{esc(desc)}</desc>'
            f'<defs><style>{css}</style>'
            f'<marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0 0 10 5 0 10z" fill="{C["primary"]}"/></marker></defs>'
            f'<rect width="{W}" height="{H}" rx="28" fill="{C["canvas"]}"/>'
            f'{body}</svg>')


DESC = ("Valen-Decision-1.5 at the centre: text, images and video plus questions go in, typed answers "
        "(predicate, choice, score, bbox) come out. Around it: SDKs, agent skill and workflow integrations; "
        "runtimes from the hosted API to vLLM, SGLang, ONNX Runtime, llama.cpp and Ollama; evaluation with "
        "JevalKit and VisualDecisionBench; and Roller and Awesome-RSI for agents and recursive self-improvement.")

ZH.update({
    DESC: ("Valen-Decision-1.5 居中：输入文本、图像、视频与问题，输出 predicate、choice、score、bbox 类型化回答。"
           "四周是 SDK、Agent skill 与工作流集成；从托管 API 到 vLLM、SGLang、ONNX Runtime、llama.cpp 和 Ollama 的运行方式；"
           "JevalKit 与 VisualDecisionBench 评测；以及面向 Agent 与递归自我改进的 Roller 和 Awesome-RSI。"),
    "Valen ecosystem": "Valen 生态",
    "Build with Valen": "用 Valen 构建", "Other agents": "其他 Agent", "Workflows": "工作流", "SDKs": "SDK",
    "Web & docs": "网页与文档", "Web chat": "网页对话", "Community": "社区项目",
    "Run anywhere": "随处运行", "Hosted API": "托管 API", "Free, no key": "免费，无需密钥",
    "Native weights": "原生权重", "Plugin or Docker image": "插件或 Docker 镜像", "Valen-patched · GGUF": "Valen 补丁版 · GGUF",
    "Evaluate": "评测", "25 model families": "25 个模型系列 · 8 套评测",
    "Leaderboard": "排行榜", "JevalKit on HF Spaces": "JevalKit · HF Space",
    "Image and video subsets": "图像与视频子集", "Vision and text tracks": "视觉榜与文本榜",
    "Compare with LLMs": "对比 LLM", "via Valen.llm() and JevalKit": "通过 Valen.llm() 与 JevalKit",
    "Multimodal System One decision model": "多模态 System One 决策模型",
    "Inputs": "输入", "Text": "文本", "Images": "图像", "Video": "视频", "Questions + candidates": "问题与候选项",
    "Decision model": "决策模型", "Qwen3.5 backbone": "Qwen3.5 主干", "Block-bidirectional attention": "分块双向注意力",
    "Dual head: decisions + bbox": "双头：决策 + bbox", "One forward pass, shared state": "共享 state，一次前向",
    "Typed answers": "类型化回答", "probability": "概率", "distribution": "概率分布",
    "level probabilities": "各档概率", "box · point": "框 · 中心点",
    "Protocols": "协议", "OpenAPI spec": "OpenAPI 规范",
    "Training & export": "训练与导出", "SFT and LoRA fine-tuning": "SFT 与 LoRA 微调",
    "RLCD (experimental)": "RLCD（实验性）", "ONNX and GGUF export": "导出 ONNX 与 GGUF",
    "Thresholds & routing": "阈值与分流", "Calibrated thresholds": "校准阈值", "Human-review band": "人工复核区间",
    "\u201cNone of these\u201d route": "\u201c都不适用\u201d候选",
    "call /v1/decisions": "调用 /v1/decisions", "decisions": "决策", "experience & feedback": "经验与反馈",
    "Agents": "Agent 智能体",
    "Agent trajectory collection across models and Harnesses": "面向多模型、多 Harness 的 Agent 轨迹采集框架",
    "One Docker container per rollout": "每个 rollout 一个 Docker 容器",
    "Tasks & benchmarks": "任务与 Benchmark", "Harnesses": "Harness", "Task agent or user simulator": "可作任务 Agent 或用户模拟器",
    "Outputs": "产物", "Your own tasks": "自定义任务", "Native session": "原生 session", "Unified trace": "统一轨迹",
    "SFT training data": "SFT 训练数据", "Graded in its container": "在运行容器内评分",
    "Recursive self-improvement": "递归自我改进",
    "Experience accumulation": "经验积累", "Prompts · context · skills · memory": "提示词 · 上下文 · 技能 · 记忆",
    "System modification": "系统修改", "Harnesses · tools · agent architecture": "运行框架 · 工具 · 智能体架构",
    "Model parameters": "模型参数", "Fine-tuning · RL · self-play": "微调 · 强化学习 · 自博弈",
})


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for lang in ("en", "zh"):
        for theme in THEMES:
            svg = build(theme, lang)
            name = "valen-ecosystem" + ("-zh" if lang == "zh" else "") + ("-dark" if theme == "dark" else "") + ".svg"
            (OUT / name).write_text(svg)
            print(name, f"{len(svg) / 1024:.0f} KB")
