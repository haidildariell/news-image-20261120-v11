#!/usr/bin/env python3
"""Friday 20 November 2026 — one front page, 36 stories, 7 regions.

A newspaper front page drawn from scratch with PIL: masthead, six-number
strip, seven-region bar, three illustrated leads, ten illustrated feature
tiles, a dotted world map with numbered pins, a 23-brief "also" list, a
date-check box and a footer. Every story, number and source is baked into
the data tables below; nothing is fetched at render time.

Deterministic by construction: one fixed seed, no clock, no network, no
file reads outside the fonts. Two runs write identical bytes.
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 22
CW = W - 2 * MARGIN  # usable width: 980

# ---- palette: newsprint on cream -------------------------------------------
PAPER = (247, 243, 231)
PAPER_SHADE = (238, 232, 213)
INK = (26, 24, 22)
RED = (176, 32, 28)
RED_DARK = (138, 20, 18)
RED_SOFT = (214, 96, 88)
BLUE = (28, 68, 128)
TEAL = (14, 110, 110)
GOLD = (168, 124, 28)
GREY = (98, 94, 86)
FAINT = (188, 180, 162)
WHITE = (255, 255, 255)
SKY_TOP = (38, 52, 96)
SKY_MID = (196, 92, 52)
SKY_LOW = (244, 178, 96)

# ---- fonts ------------------------------------------------------------------
_FONT_DIR = "/usr/share/fonts/truetype"
_SERIF = os.path.join(_FONT_DIR, "noto", "NotoSerif-Bold.ttf")
_SERIF_IT = os.path.join(_FONT_DIR, "noto", "NotoSerif-Italic.ttf")
_SERIF_RG = os.path.join(_FONT_DIR, "noto", "NotoSerif-Regular.ttf")
_SANS = os.path.join(_FONT_DIR, "dejavu", "DejaVuSans.ttf")
_SANS_B = os.path.join(_FONT_DIR, "dejavu", "DejaVuSans-Bold.ttf")

_font_cache = {}


def serif(size):
    return _load(_SERIF, size)


def serif_it(size):
    return _load(_SERIF_IT, size)


def serif_rg(size):
    return _load(_SERIF_RG, size)


def sans(size):
    return _load(_SANS, size)


def sans_b(size):
    return _load(_SANS_B, size)


def _load(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


# ---- text helpers ------------------------------------------------------------
def text_w(draw, text, font):
    return draw.textlength(text, font=font)


def wrap(draw, text, font, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, x, y, lines, font, fill, leading=None):
    """Draw stacked lines; returns the y just below the last line."""
    if leading is None:
        leading = int(font.size * 1.22)
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def fit_text(draw, text, font, max_w):
    """Shrink font size until the text fits max_w (never below 7)."""
    size = font.size
    while size > 7 and draw.textlength(text, font=font) > max_w:
        size -= 1
        font = _load(font.path, size)
    return font


def rule(draw, x, y, w, weight=2, fill=INK):
    draw.rectangle([x, y, x + w - 1, y + weight - 1], fill=fill)


def hline(draw, x, y, w, fill=FAINT):
    draw.line([(x, y), (x + w, y)], fill=fill, width=1)


def vgrad(draw, x, y, w, h, top, bottom, steps=28):
    """Vertical gradient as stacked horizontal strips."""
    for i in range(steps):
        t = i / max(steps - 1, 1)
        col = tuple(int(top[c] + (bottom[c] - top[c]) * t) for c in range(3))
        y0 = y + int(h * i / steps)
        y1 = y + int(h * (i + 1) / steps)
        draw.rectangle([x, y0, x + w - 1, max(y1 - 1, y0)], fill=col)


def speckle(draw, rng, x0, y0, x1, y1, count, dark=(120, 110, 92), light=(255, 255, 250)):
    """Deterministic newsprint grain over a rectangle."""
    for _ in range(count):
        px = rng.randint(x0, x1)
        py = rng.randint(y0, y1)
        col = dark if rng.random() < 0.55 else light
        draw.point((px, py), fill=col)

# ---- data: every figure on the page, verified for 20 November 2026 ---------
# (Full per-story source list lives in SOURCES.md.)

STATS = [
    ("3", "bridges damaged in Kyiv"),
    ("370,000", "evacuated ahead of Akvan"),
    ("\u22126.2%", "Taiwan Taiex, Friday close"),
    ("100,000", "UK\u2013EU youth visas a year"),
    ("2.3%", "Japan Oct CPI; BoJ hike eyed"),
    ("118", "Phillips runs vs India"),
]

REGIONS = [
    ("EUROPE", 8, (28, 68, 128)),
    ("ASIA-PACIFIC", 8, (196, 92, 32)),
    ("MIDDLE EAST", 4, (14, 110, 110)),
    ("AFRICA", 3, (120, 96, 32)),
    ("AMERICAS", 7, (138, 20, 18)),
    ("OCEANIA", 4, (42, 110, 140)),
    ("GLOBAL", 2, (98, 94, 86)),
]

# Leads: num, place, beat, title, body lines, source, art key.
LEADS = [
    {
        "num": "01",
        "place": "KYIV, UKRAINE",
        "beat": "WAR",
        "title": "Russian barrage hits three Kyiv bridges",
        "body": [
            "Overnight ballistic-missile barrage kills 3, damages three",
            "bridges across the Dnipro and sets fires in three districts;",
            "110+ missiles fired.",
        ],
        "source": "REUTERS",
        "art": "kyiv",
    },
    {
        "num": "02",
        "place": "ODISHA, INDIA",
        "beat": "STORM",
        "title": "Cyclone Akvan makes landfall in eastern India",
        "body": [
            "Severe storm crosses near Gopalpur Friday morning;",
            "370,000 evacuated, 9,341 shelters, 423 rescue teams;",
            "winds 70\u201380, gusting 90 km/h; no deaths reported.",
        ],
        "source": "IMD",
        "art": "akvan",
    },
    {
        "num": "03",
        "place": "SEOUL \u00b7 TOKYO",
        "beat": "MARKETS",
        "title": "AI sell-off sinks Asia to worst week since 1991",
        "body": [
            "Nikkei \u22125.1%, Kospi \u22125.2%, Taiex \u22126.2%, SoftBank",
            "\u221214.5% on the week, worst since 1991.",
        ],
        "source": "REUTERS",
        "art": "markets",
    },
]

# Feature tiles 4-13: num, place, beat, title, body, big fact, source, art.
TILES = [
    {
        "num": "04", "place": "ANTALYA", "beat": "CLIMATE",
        "title": "COP31 reaches final day deadlocked",
        "body": "Draft omits fossil-fuel phase-out and $120bn adaptation target.",
        "fact": "DEADLOCK", "source": "REUTERS", "art": "cop",
    },
    {
        "num": "05", "place": "MERCURY", "beat": "SPACE",
        "title": "BepiColombo reaches Mercury after 8 years",
        "body": "ESA/JAXA probe ends 6bn-mile trip; orbit insertion Saturday.",
        "fact": "6BN MILES", "source": "ESA \u00b7 BBC", "art": "mercury",
    },
    {
        "num": "06", "place": "BRUSSELS", "beat": "EUROPE",
        "title": "Burnham holds second EU\u2013UK reset summit",
        "body": "Deals on food, emissions trading, youth mobility for 100,000.",
        "fact": "RESET TALKS", "source": "AP", "art": "brussels",
    },
    {
        "num": "07", "place": "TOKYO", "beat": "ECONOMY",
        "title": "Japan inflation hits 2.3%; BoJ hike eyed",
        "body": "Oct CPI 2.3%, up from 2.1%; core 2.2%.",
        "fact": "2.3%", "source": "STATISTICS BUREAU", "art": "tokyo",
    },
    {
        "num": "08", "place": "BEIJING", "beat": "RATES",
        "title": "China holds lending rates for 18th month",
        "body": "1-yr LPR 3.00%, 5-yr 3.50% as expected.",
        "fact": "3.00% \u00b7 3.50%", "source": "PBoC \u00b7 REUTERS", "art": "beijing",
    },
    {
        "num": "09", "place": "WELLINGTON", "beat": "CRICKET",
        "title": "Phillips makes history with 118 vs India",
        "body": "Centuries vs India in all 3 formats in one year; NZ 368.",
        "fact": "118", "source": "ICC", "art": "cricket",
    },
    {
        "num": "10", "place": "ROME", "beat": "LABOUR",
        "title": "Italy\u2019s CGIL holds 24-hr general strike",
        "body": "Unions rally across ~100 squares against the 2027 budget.",
        "fact": "100 SQUARES", "source": "ANSA", "art": "rome",
    },
    {
        "num": "11", "place": "MATO GROSSO", "beat": "LAND",
        "title": "Lula visits ailing Chief Raoni, 94",
        "body": "Kayapo and Yudja lands recognised (Kapot Nhinore).",
        "fact": "ANCESTRAL LANDS", "source": "ONE TURN", "art": "amazon",
    },
    {
        "num": "12", "place": "BARCELONA", "beat": "HEALTH",
        "title": "Daraxonrasib + chemo shrinks tumours in 60.7%",
        "body": "Early trial, 61 patients, presented Friday at ENA.",
        "fact": "60.7%", "source": "EORTC", "art": "health",
    },
    {
        "num": "13", "place": "TURIN", "beat": "TENNIS",
        "title": "Alcaraz\u2013Cobolli & Medvedev\u2013Tiafoe close ATP Finals groups",
        "body": "Group stage ends Friday; semi-finals Saturday.",
        "fact": "ATP FINALS", "source": "ATP", "art": "tennis",
    },
]

# Also-list briefs 14-36: (num, place, one sentence, source).
ALSO = [
    ("14", "FLORIDA", "St Johns River hits record 18.3 ft.", "AP"),
    ("15", "DOHA", "Australia stuns Argentina 2\u20130 at U17 World Cup.", "FIFA"),
    ("16", "SEOUL", "Move to impeach Chief Justice Cho Hee-dae.", "SBS"),
    ("17", "BOUGAINVILLE", "Rio Tinto pledges $370m Panguna repair.", "ABC"),
    ("18", "CANBERRA", "CBO: AUKUS sales may shrink US fleet.", "Reuters"),
    ("19", "IOWA", "Army to detonate 68 unstable explosive barrels.", "AP"),
    ("20", "TONGA", "El Ni\u00f1o drought bites.", "RNZ"),
    ("21", "COPENHAGEN", "Greenland defence bill approved.", "AFP"),
    ("22", "GLOBAL", "UN marks World Children\u2019s Day.", "UN News"),
    ("23", "DAKAR", "President Faye enacts budget by decree.", "AFP"),
    ("24", "HORMUZ", "Attacks on vessels in 96 hours.", "UKMTO"),
    ("25", "NEW DELHI", "Pakistan minister to lead SCO team.", "The Hindu"),
    ("26", "HONG KONG", "Badminton Open semifinals decided.", "BWF"),
    ("27", "TAIPEI", "Short-sell curbs in; bombers tracked.", "Reuters"),
    ("28", "EUROPE", "Youth strike in 25+ countries.", "One Turn"),
    ("29", "WASHINGTON", "Trump: open to NATO-like Ukraine deal.", "WTD"),
    ("30", "BOGOT\u00c1", "Protests over tax plans amid US row.", "WTD"),
    ("31", "LILONGWE", "Malawi fuel crisis sparks chaos nationwide.", "WTD"),
    ("32", "GAZA", "Civil Defence struggles as vehicles fail.", "WTD"),
    ("33", "BRAZIL", "Violent deaths at series low, \u221212.2%.", "1stHeadlines"),
    ("34", "ALGIERS", "World Bank: Algeria growth at 3.7%.", "1stHeadlines"),
    ("35", "SANTIAGO", "Fuel relief bill may cost $813m.", "1stHeadlines"),
    ("36", "BRUSSELS", "EU adopts \u20ac1bn military aid for Ukraine.", "Council of the EU"),
]

DATE_CHECK_ITEMS = [
    "Trump\u2013Xi\u2013Putin Shenzhen talks + \u2018peace declaration\u2019",
    "ICJ Myanmar Rohingya genocide verdict (9\u20136)",
    "GTA VI midnight launch / $190.4m Van Gogh sale",
    "Voyager 1 one-light-day confirmation",
    "Senate 48\u201351 Iran war-powers vote",
]

FOOTER = (
    "Every story here happened, or was first reported, on Friday 20 November 2026. "
    "Officials\u2019 counts are attributed. Sources named per story \u00b7 Full list in SOURCES.md "
    "\u00b7 Original drawings."
)

# ---- lead illustrations ------------------------------------------------------
# Each draws inside box (x, y, w, h) on the given ImageDraw.

def art_kyiv(d, x, y, w, h, rng):
    """Dusk over the Dnipro: orange horizon, dark skyline, lit windows,
    river with reflections, three arched bridges, KYIV banner."""
    vgrad(d, x, y, w, h, SKY_TOP, SKY_LOW, steps=30)
    # setting sun glow
    sx, sy = x + int(w * 0.72), y + int(h * 0.42)
    for r, col in ((34, (255, 214, 140)), (22, (255, 196, 110)), (12, (255, 226, 170))):
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=col)
    # high cloud streaks
    for cx, cy, cw in ((0.08, 0.14, 90), (0.42, 0.08, 70), (0.60, 0.20, 80)):
        d.ellipse([x + int(w * cx), y + int(h * cy),
                   x + int(w * cx) + cw, y + int(h * cy) + 9], fill=(255, 232, 200))
    # skyline: dark blocks with lit windows
    base = y + int(h * 0.62)
    bx0 = x + 4
    heights = [46, 62, 38, 70, 52, 44, 66, 40, 58, 48]
    bw = (w - 8) // len(heights)
    for i, bh in enumerate(heights):
        x0 = bx0 + i * bw
        d.rectangle([x0, base - bh, x0 + bw - 2, base], fill=(28, 30, 58))
        for wy in range(base - bh + 6, base - 4, 9):
            for wx in range(x0 + 3, x0 + bw - 5, 7):
                if rng.random() < 0.45:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 208, 110))
    # KYIV banner last, white with dark halo, across the skyline
    banner = serif(46)
    bx = x + (w - d.textlength("KYIV", font=banner)) // 2
    by = y + 6
    for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, 2)):
        d.text((bx + ox, by + oy), "KYIV", font=banner, fill=(40, 30, 60))
    d.text((bx, by), "KYIV", font=banner, fill=WHITE)
    # river band
    ry = base
    d.rectangle([x, ry, x + w - 1, y + h - 17], fill=(52, 96, 148))
    for i in range(26):
        rx = x + rng.randint(4, w - 30)
        ryy = ry + rng.randint(3, h - 24)
        d.line([(rx, ryy), (rx + rng.randint(12, 26), ryy)], fill=(150, 190, 225), width=2)
    # three bridges: arch + deck + pylons, spaced across the river
    for k, cx in enumerate((0.20, 0.50, 0.80)):
        cxp = x + int(w * cx)
        span = 62
        d.arc([cxp - span // 2, ry + 2, cxp + span // 2, ry + 34],
              start=180, end=360, fill=(240, 236, 224), width=4)
        d.line([(cxp - span // 2, ry + 12), (cxp + span // 2, ry + 12)],
               fill=(240, 236, 224), width=3)
        d.line([(cxp - 2, ry + 2), (cxp - 2, ry + 16)], fill=(240, 236, 224), width=3)
        d.line([(cxp + 2, ry + 2), (cxp + 2, ry + 16)], fill=(240, 236, 224), width=3)
    # dark name strip at the bottom of the art
    d.rectangle([x, y + h - 16, x + w - 1, y + h - 1], fill=(24, 26, 48))
    names = "PODILSKO-VOSKRESENSKYI    DARNYTSKYI    PIVDENNYI \u00b7 SOUTHERN"
    nf = sans_b(8)
    while d.textlength(names, font=nf) > w - 8 and nf.size > 6:
        nf = sans_b(nf.size - 1)
    d.text((x + (w - d.textlength(names, font=nf)) // 2, y + h - 14),
           names, font=nf, fill=(235, 230, 215))


def art_akvan(d, x, y, w, h, rng):
    """Odisha coast: green land left, pale sea right, cyclone spiral and
    radar rings over Gopalpur, rain streaks, evacuation box."""
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(206, 228, 232))
    # land mass (left): coastline curve
    coast = [(x, y + 10), (x + 78, y + 4), (x + 108, y + 34), (x + 96, y + 70),
             (x + 118, y + 96), (x + 92, y + h - 8), (x, y + h - 6)]
    d.polygon(coast, fill=(178, 208, 140))
    d.line(coast, fill=(120, 160, 90), width=2)
    # inland detail: small towns + roads
    for tx, ty in ((0.10, 0.30), (0.16, 0.55), (0.22, 0.75), (0.05, 0.82)):
        d.ellipse([x + int(w * tx) - 2, y + int(h * ty) - 2,
                   x + int(w * tx) + 2, y + int(h * ty) + 2], fill=(90, 110, 60))
    # sea waves
    for wy in range(y + 16, y + h - 6, 12):
        for wx in range(x + 130, x + w - 12, 26):
            d.arc([wx, wy, wx + 18, wy + 8], start=200, end=340, fill=(140, 180, 205), width=2)
    # cyclone spiral: arms of arcs around Gopalpur
    gx, gy = x + int(w * 0.42), y + int(h * 0.46)
    for r, start, end, col in (
            (62, 20, 200, (255, 255, 255)), (50, 140, 320, (235, 242, 245)),
            (36, 260, 80, (255, 255, 255)), (22, 60, 260, (220, 232, 238))):
        d.arc([gx - r, gy - r, gx + r, gy + r], start=start, end=end, fill=col, width=6)
    # radar rings + centre dot
    for r in (58, 42, 26):
        d.ellipse([gx - r, gy - r, gx + r, gy + r], outline=(176, 32, 28), width=2)
    d.ellipse([gx - 5, gy - 5, gx + 5, gy + 5], fill=RED)
    # rain streaks over the sea
    for _ in range(34):
        rx = x + rng.randint(int(w * 0.55), w - 6)
        ryy = y + rng.randint(6, h - 20)
        d.line([(rx, ryy), (rx - 4, ryy + 9)], fill=(110, 150, 180), width=2)
    # clouds
    for cx, cy, cw in ((0.55, 0.06, 80), (0.78, 0.14, 64), (0.30, 0.04, 56)):
        d.ellipse([x + int(w * cx), y + int(h * cy),
                   x + int(w * cx) + cw, y + int(h * cy) + 10], fill=WHITE)
    # Gopalpur label, clear of the rings
    lf = sans_b(9)
    d.text((gx + 66, gy - 30), "GOPALPUR", font=lf, fill=INK)
    d.line([(gx + 62, gy - 24), (gx + 10, gy - 8)], fill=INK, width=1)
    # evacuation box, bottom left
    bx0, by0, bw, bh = x + 8, y + h - 46, 196, 38
    d.rectangle([bx0, by0, bx0 + bw - 1, by0 + bh - 1], fill=WHITE, outline=RED, width=2)
    d.text((bx0 + 8, by0 + 4), "370,000 EVACUATED", font=sans_b(13), fill=RED)
    d.text((bx0 + 8, by0 + 21), "9,341 shelters \u00b7 423 teams", font=sans(10), fill=INK)


def art_markets(d, x, y, w, h, rng):
    """Falling red candlesticks on a pale grid, red trend line, and a
    2x2 results table at the foot of the art."""
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(250, 246, 236))
    # grid
    for gy in range(y + 12, y + h - 44, 14):
        d.line([(x + 8, gy), (x + w - 8, gy)], fill=(226, 220, 204), width=1)
    for gx in range(x + 12, x + w - 8, 26):
        d.line([(gx, y + 8), (gx, y + h - 48)], fill=(232, 226, 210), width=1)
    # candlesticks descending left to right
    top = y + 14
    bottom = y + h - 52
    n = 8
    step = (w - 30) // n
    prev_cy = None
    pts = []
    for i in range(n):
        cx = x + 16 + i * step + step // 2
        frac = i / max(n - 1, 1)
        cy = top + int((bottom - top) * (0.12 + 0.62 * frac))
        body_h = rng.randint(10, 18)
        # wick
        d.line([(cx, cy - body_h // 2 - 6), (cx, cy + body_h // 2 + 6)],
               fill=(176, 32, 28), width=2)
        # body
        d.rectangle([cx - 7, cy - body_h // 2, cx + 7, cy + body_h // 2],
                    fill=(196, 52, 44), outline=(138, 20, 18), width=1)
        pts.append((cx, cy))
        prev_cy = cy
    # red trend line through candle centres
    d.line(pts, fill=RED, width=3)
    d.polygon([(pts[-1][0], pts[-1][1]), (pts[-1][0] + 10, pts[-1][1] - 2),
               (pts[-1][0] + 2, pts[-1][1] + 8)], fill=RED)
    # results table
    tx0, ty0, tw, th = x + 8, y + h - 44, w - 16, 38
    d.rectangle([tx0, ty0, tx0 + tw - 1, ty0 + th - 1], fill=WHITE, outline=INK, width=1)
    d.line([(tx0 + tw // 2, ty0), (tx0 + tw // 2, ty0 + th)], fill=INK, width=1)
    d.line([(tx0, ty0 + th // 2), (tx0 + tw, ty0 + th // 2)], fill=INK, width=1)
    cells = [("TAIPEI", "\u22126.2%"), ("SEOUL", "\u22125.2%"),
             ("TOKYO", "\u22125.1%"), ("SOFTBANK", "\u221214.5%")]
    for i, (name, val) in enumerate(cells):
        cx = tx0 + (i % 2) * (tw // 2)
        cy = ty0 + (i // 2) * (th // 2)
        d.text((cx + 8, cy + 3), name, font=sans_b(10), fill=INK)
        vw = d.textlength(val, font=sans_b(11))
        d.text((cx + tw // 2 - vw - 8, cy + 2), val, font=sans_b(11), fill=RED)

# ---- feature-tile illustrations (small, bright, one scene each) --------------
def art_cop(d, x, y, w, h, rng):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(214, 232, 244))
    d.ellipse([x + 12, y + 8, x + 78, y + h - 8], fill=(64, 140, 190))
    d.ellipse([x + 26, y + 18, x + 52, y + 40], fill=(110, 190, 120))
    d.ellipse([x + 44, y + 38, x + 66, y + 56], fill=(110, 190, 120))
    # thermometer, right side
    tx = x + w - 34
    d.rounded_rectangle([tx, y + 10, tx + 12, y + h - 16], radius=6,
                        fill=WHITE, outline=INK, width=1)
    d.ellipse([tx - 5, y + h - 26, tx + 17, y + h - 4], fill=RED, outline=INK, width=1)
    d.rectangle([tx + 3, y + 16, tx + 9, y + h - 16], fill=RED)
    for i, gy in enumerate(range(y + 16, y + h - 30, 9)):
        d.line([(tx + 12, gy), (tx + 18, gy)], fill=INK, width=1)
    d.text((x + w - 62, y + 4), "38\u00b0", font=sans_b(11), fill=RED)


def art_mercury(d, x, y, w, h, rng):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(22, 26, 52))
    for _ in range(26):
        sx = x + rng.randint(2, w - 3)
        sy = y + rng.randint(2, h - 3)
        d.ellipse([sx, sy, sx + 2, sy + 2], fill=WHITE)
    # cratered planet, left
    px, py, pr = x + 34, y + h // 2, 26
    d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(168, 160, 148))
    for cx, cy, cr in ((0.35, 0.35, 7), (0.62, 0.55, 9), (0.45, 0.68, 5), (0.68, 0.30, 4)):
        d.ellipse([px + int(pr * (cx - 1)) - cr, py + int(pr * (cy - 1)) - cr,
                   px + int(pr * (cx - 1)) + cr, py + int(pr * (cy - 1)) + cr],
                  fill=(138, 130, 118))
    # probe with solar panels, right
    qx, qy = x + w - 62, y + 16
    d.rectangle([qx, qy, qx + 16, qy + 14], fill=(220, 220, 225), outline=INK, width=1)
    d.rectangle([qx - 24, qy + 2, qx - 2, qy + 12], fill=(40, 90, 180), outline=INK, width=1)
    d.rectangle([qx + 18, qy + 2, qx + 40, qy + 12], fill=(40, 90, 180), outline=INK, width=1)
    d.line([(qx + 8, qy + 14), (qx - 6, qy + 34)], fill=(220, 220, 225), width=2)
    d.line([(qx + 2, qy + 34), (qx + 16, qy + 30)], fill=(255, 220, 120), width=2)


def art_brussels(d, x, y, w, h, rng):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(30, 60, 140))
    # circle of twelve gold stars (EU)
    cx, cy, r = x + w // 2 - 14, y + h // 2, 24
    for k in range(12):
        ang = math.pi * 2 * k / 12 - math.pi / 2
        sx = cx + int(r * math.cos(ang))
        sy = cy + int(r * math.sin(ang))
        d.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(255, 210, 60))
    # small Union Jack corner flag (UK), right
    fx, fy, fw, fh = x + w - 46, y + h - 26, 38, 20
    d.rectangle([fx, fy, fx + fw, fy + fh], fill=(28, 48, 120), outline=WHITE, width=1)
    d.line([(fx, fy), (fx + fw, fy + fh)], fill=WHITE, width=2)
    d.line([(fx + fw, fy), (fx, fy + fh)], fill=WHITE, width=2)
    d.line([(fx + fw // 2, fy), (fx + fw // 2, fy + fh)], fill=(200, 40, 40), width=3)
    d.line([(fx, fy + fh // 2), (fx + fw, fy + fh // 2)], fill=(200, 40, 40), width=3)


def art_tokyo(d, x, y, w, h, rng):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(250, 246, 236))
    # rising bars: 2.1 then 2.3 highlighted
    vals = [26, 30, 28, 34, 40]
    bw = (w - 30) // len(vals)
    for i, v in enumerate(vals):
        bx = x + 12 + i * bw
        col = RED if i == len(vals) - 1 else BLUE
        d.rectangle([bx, y + h - 10 - v, bx + bw - 4, y + h - 10], fill=col)
    d.text((x + 12, y + 4), "\u00a5 CPI", font=sans_b(12), fill=INK)
    d.line([(x + 10, y + h - 10), (x + w - 8, y + h - 10)], fill=INK, width=2)
    # red arrow climbing
    d.line([(x + 14, y + 26), (x + w - 22, y + 8)], fill=RED, width=3)
    d.polygon([(x + w - 22, y + 8), (x + w - 32, y + 6), (x + w - 24, y + 16)], fill=RED)


def art_beijing(d, x, y, w, h, rng):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(240, 232, 214))
    # bank building with columns
    bx, by = x + 12, y + 12
    d.polygon([(bx, by + 12), (bx + 52, by), (bx + 104, by + 12)], fill=(176, 32, 28))
    for i in range(5):
        cx = bx + 8 + i * 20
        d.rectangle([cx, by + 14, cx + 8, by + 40], fill=(120, 100, 70))
    d.rectangle([bx, by + 40, bx + 104, by + 46], fill=(120, 100, 70))
    # flat rate line, right
    lx = x + w - 62
    for gy in range(y + 12, y + h - 8, 10):
        d.line([(lx, gy), (lx + 48, gy)], fill=(210, 200, 180), width=1)
    d.line([(lx, y + 30), (lx + 48, y + 30)], fill=BLUE, width=3)
    d.ellipse([lx + 44, y + 26, lx + 52, y + 34], fill=BLUE)
    d.text((lx, y + 36), "3.00%", font=sans_b(10), fill=BLUE)


def art_cricket(d, x, y, w, h, rng):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(140, 190, 90))
    # pitch strip
    d.rectangle([x + 20, y + 6, x + w - 20, y + h - 6], fill=(214, 186, 130))
    d.line([(x + 20, y + h // 2), (x + w - 20, y + h // 2)], fill=WHITE, width=2)
    # stumps, both ends
    for sx in (x + 30, x + w - 34):
        for k in range(3):
            d.line([(sx + k * 4, y + 12), (sx + k * 4, y + 26)], fill=(255, 220, 80), width=2)
        for k in range(3):
            d.line([(sx + k * 4, y + h - 26), (sx + k * 4, y + h - 12)],
                   fill=(255, 220, 80), width=2)
    # bat + red ball mid-pitch
    d.line([(x + w // 2 - 6, y + 22), (x + w // 2 + 8, y + 46)], fill=(150, 110, 60), width=5)
    d.ellipse([x + w // 2 + 2, y + h - 30, x + w // 2 + 12, y + h - 20], fill=RED)
    # crowd dots along the top edge
    for i in range(12):
        cx = x + 8 + i * 15
        d.ellipse([cx, y + 2, cx + 6, y + 8], fill=(90, 60, 40))


def art_rome(d, x, y, w, h, rng):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(232, 222, 196))
    # sun + colosseum-ish arches behind
    d.ellipse([x + w - 34, y + 6, x + w - 10, y + 30], fill=(255, 200, 90))
    for i in range(4):
        ax = x + 14 + i * 30
        d.arc([ax, y + 34, ax + 24, y + 58], start=180, end=360,
              fill=(150, 110, 70), width=3)
    # crowd: rows of heads + placards
    for row, yy in enumerate((0.62, 0.80)):
        for i in range(9 - row):
            cx = x + 12 + i * 19 + row * 8
            cy = y + int(h * yy)
            d.ellipse([cx, cy, cx + 10, cy + 10], fill=(60, 50, 44))
            d.rectangle([cx - 2, cy + 10, cx + 12, cy + 20], fill=(70, 90, 130) if i % 2 else (150, 60, 50))
    # placards on sticks
    for px, label in ((0.18, "24H"), (0.55, "CGIL"), (0.82, "!")):
        sx = x + int(w * px)
        d.line([(sx, y + 18), (sx, y + 38)], fill=INK, width=2)
        d.rectangle([sx - 12, y + 6, sx + 12, y + 18], fill=WHITE, outline=RED, width=1)
        d.text((sx - 7, y + 7), label, font=sans_b(8), fill=RED)


def art_amazon(d, x, y, w, h, rng):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(196, 224, 178))
    # sun
    d.ellipse([x + w - 36, y + 6, x + w - 12, y + 30], fill=(255, 200, 90))
    # river curve
    d.line([(x + 10, y + h - 6), (x + 60, y + h - 22), (x + 110, y + h - 10),
            (x + w - 8, y + h - 18)], fill=(80, 140, 190), width=6)
    # trees: layered triangles + trunks
    for tx, th in ((0.12, 30), (0.30, 38), (0.48, 28), (0.66, 36), (0.84, 30)):
        cx = x + int(w * tx)
        base = y + h - 8
        d.polygon([(cx - 14, base - th + 12), (cx, base - th - 6), (cx + 14, base - th + 12)],
                  fill=(40, 120, 60))
        d.polygon([(cx - 11, base - th + 22), (cx, base - th + 6), (cx + 11, base - th + 22)],
                  fill=(30, 100, 50))
        d.rectangle([cx - 2, base - th + 22, cx + 2, base], fill=(110, 80, 50))
    # small hut
    hx, hy = x + w - 66, y + h - 30
    d.polygon([(hx, hy), (hx + 20, hy - 12), (hx + 40, hy)], fill=(150, 100, 50))
    d.rectangle([hx + 4, hy, hx + 36, hy + 14], fill=(190, 160, 110))


def art_health(d, x, y, w, h, rng):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(240, 238, 250))
    # big capsule, diagonal
    cx, cy = x + 52, y + h // 2 + 4
    d.ellipse([cx - 34, cy - 13, cx + 34, cy + 13], fill=(220, 60, 60))
    d.ellipse([cx - 34, cy - 13, cx, cy + 13], fill=WHITE)
    d.ellipse([cx - 34, cy - 13, cx + 34, cy + 13], outline=INK, width=2)
    d.line([(cx, cy - 13), (cx, cy + 13)], fill=INK, width=2)
    # small pills + rising chart
    for px, py, col in ((0.72, 0.22, (60, 120, 200)), (0.82, 0.38, (220, 60, 60)),
                        (0.68, 0.55, (60, 160, 90))):
        d.ellipse([x + int(w * px) - 6, y + int(h * py) - 4,
                   x + int(w * px) + 6, y + int(h * py) + 4], fill=col, outline=INK, width=1)
    d.line([(x + w - 62, y + h - 12), (x + w - 40, y + 34), (x + w - 14, y + 16)],
           fill=RED, width=3)


def art_tennis(d, x, y, w, h, rng):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(90, 160, 90))
    # court lines
    d.rectangle([x + 10, y + 8, x + w - 10, y + h - 8], outline=WHITE, width=2)
    d.line([(x + w // 2, y + 8), (x + w // 2, y + h - 8)], fill=WHITE, width=2)
    d.line([(x + 10, y + h // 2), (x + w - 10, y + h // 2)], fill=WHITE, width=2)
    # net
    d.line([(x + 10, y + h // 2 - 3), (x + w - 10, y + h // 2 - 3)], fill=(40, 40, 40), width=3)
    # ball + racket
    d.ellipse([x + w - 34, y + 12, x + w - 18, y + 28], fill=(210, 230, 60), outline=INK, width=1)
    d.ellipse([x + 18, y + h - 30, x + 44, y + h - 6], outline=(200, 190, 170), width=3)
    d.line([(x + 44, y + h - 12), (x + 62, y + h - 2)], fill=(150, 110, 60), width=4)


TILE_ART = {
    "cop": art_cop, "mercury": art_mercury, "brussels": art_brussels,
    "tokyo": art_tokyo, "beijing": art_beijing, "cricket": art_cricket,
    "rome": art_rome, "amazon": art_amazon, "health": art_health,
    "tennis": art_tennis,
}
LEAD_ART = {"kyiv": art_kyiv, "akvan": art_akvan, "markets": art_markets}


# ---- dotted world map ---------------------------------------------------------
# Continent blobs as (lon, lat, rx, ry) ellipses on an equirectangular grid.
LAND_BLOBS = [
    (-105, 50, 46, 16), (-95, 63, 28, 9), (-82, 24, 11, 8), (-120, 40, 11, 9),
    (-60, -10, 18, 16), (-65, -30, 10, 14),
    (15, 52, 22, 10), (10, 62, 12, 7),
    (18, 5, 20, 20), (20, -18, 14, 12),
    (90, 50, 55, 18), (75, 25, 20, 12), (110, 35, 25, 12), (135, 60, 25, 10),
    (105, 12, 10, 8), (134, -25, 18, 9), (150, -38, 8, 6), (140, -8, 6, 5),
]

# (num, lon, lat, dx, dy) — dx/dy nudge pins apart where stories crowd.
MAP_PINS = [
    ("1", 30.5, 50.4, 0, 0), ("2", 84.9, 19.3, 0, 0), ("3", 128.0, 38.0, 0, 0),
    ("4", 30.7, 36.9, 0, 0), ("6", 4.4, 50.8, 0, 0), ("7", 142.0, 34.0, 0, 0),
    ("8", 116.4, 39.9, 0, 0), ("9", 174.8, -41.3, 0, 0), ("10", 12.5, 41.9, 3, -2),
    ("11", -55.0, -12.0, 0, 0), ("12", 2.2, 41.4, -4, 1), ("13", 7.7, 45.1, 0, -3),
    ("14", -81.7, 28.0, 0, 0), ("15", 51.5, 25.3, 0, 0),
]


def draw_world_map(d, x, y, w, h, rng):
    """Dotted continents + numbered red pins for stories 1-15 (no pin 5)."""
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(244, 240, 226),
                outline=INK, width=1)
    lon0, lon1, lat0, lat1 = -180.0, 180.0, 76.0, -58.0

    def proj(lon, lat):
        px = x + (lon - lon0) / (lon1 - lon0) * w
        py = y + (lat0 - lat) / (lat0 - lat1) * h
        return px, py

    # land dots on a 5px grid
    step = 5
    gx = x + 3
    while gx < x + w - 3:
        gy = y + 3
        while gy < y + h - 3:
            lon = lon0 + (gx - x) / w * (lon1 - lon0)
            lat = lat0 - (gy - y) / h * (lat0 - lat1)
            inside = False
            for clon, clat, rx, ry in LAND_BLOBS:
                if ((lon - clon) / rx) ** 2 + ((lat - clat) / ry) ** 2 <= 1.0:
                    inside = True
                    break
            if inside:
                jx = gx + rng.randint(-1, 1)
                jy = gy + rng.randint(-1, 1)
                d.ellipse([jx, jy, jx + 2, jy + 2], fill=(150, 142, 118))
            gy += step
        gx += step
    # pins
    pf = sans_b(8)
    for num, lon, lat, dx, dy in MAP_PINS:
        px, py = proj(lon, lat)
        px, py = int(px) + dx, int(py) + dy
        d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=RED, outline=WHITE, width=1)
        tw = d.textlength(num, font=pf)
        d.text((px - tw / 2, py - 5), num, font=pf, fill=WHITE)

# ---- page layout ---------------------------------------------------------------
def draw_masthead(d):
    y = 10
    d.text((MARGIN, y), "THE WORLD IN ONE DAY", font=sans_b(13), fill=RED)
    right = "36 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED FRIDAY 20 NOVEMBER 2026"
    rf = sans_b(11)
    d.text((W - MARGIN - d.textlength(right, font=rf), y + 1), right,
           font=rf, fill=INK)
    title = "Friday 20 November 2026"
    tf = serif(60)
    d.text((MARGIN, 30), title, font=tf, fill=INK)
    sub = ("Cyclone Akvan strikes India \u2022 Ballistic missiles hit Kyiv \u2022 "
           "COP31 deadlocked on final day \u2022 Asian AI sell-off")
    d.text((MARGIN, 100), sub, font=serif_it(17), fill=INK)
    rule(d, MARGIN, 122, CW, weight=2)


def draw_stats(d):
    y = 130
    col_w = CW // 6
    for i, (num, label) in enumerate(STATS):
        x = MARGIN + i * col_w
        if i:
            d.line([(x - 6, y + 2), (x - 6, y + 42)], fill=FAINT, width=1)
        d.text((x, y), num, font=sans_b(29), fill=RED)
        lab_lines = wrap(d, label, sans(10), col_w - 12)
        draw_lines(d, x, y + 34, lab_lines[:2], sans(10), GREY, leading=12)


def draw_regions(d):
    y = 178
    total = sum(c for _, c, _ in REGIONS)
    x = MARGIN
    for name, count, col in REGIONS:
        w = int(round(CW * count / total))
        d.rectangle([x, y, x + w - 1, y + 19], fill=col)
        label = "%s %d" % (name, count)
        lf = sans_b(10)
        while d.textlength(label, font=lf) > w - 6 and lf.size > 7:
            lf = sans_b(lf.size - 1)
        d.text((x + (w - d.textlength(label, font=lf)) // 2, y + 3),
               label, font=lf, fill=WHITE)
        x += w


def draw_leads(d, rng):
    y_art = 204
    art_h = 128
    col_w = 318
    gap = 13
    for i, lead in enumerate(LEADS):
        x = MARGIN + i * (col_w + gap)
        d.rectangle([x, y_art, x + col_w - 1, y_art + art_h - 1],
                    outline=INK, width=1)
        LEAD_ART[lead["art"]](d, x + 1, y_art + 1, col_w - 2, art_h - 2, rng)
        y = y_art + art_h + 6
        kicker = "%s \u00b7 %s \u2014 %s" % (lead["num"], lead["place"], lead["beat"])
        d.text((x, y), kicker, font=sans_b(11), fill=RED)
        y += 17
        title_lines = wrap(d, lead["title"], serif(19), col_w)
        y = draw_lines(d, x, y, title_lines[:2], serif(19), INK, leading=23)
        y += 3
        body = " ".join(lead["body"])
        body_lines = wrap(d, body, sans(10.5), col_w)
        y = draw_lines(d, x, y, body_lines[:3], sans(10.5), INK, leading=13)
        y += 5
        chip = "SOURCE: %s" % lead["source"]
        cf = sans_b(9)
        cw = int(d.textlength(chip, font=cf)) + 12
        d.rectangle([x, y, x + cw - 1, y + 15], fill=RED)
        d.text((x + 6, y + 2), chip, font=cf, fill=WHITE)


def draw_tiles(d, rng):
    col_w = 189
    gap_x = 8
    art_h = 56
    for row in range(2):
        y0 = 466 + row * 158
        for col in range(5):
            tile = TILES[row * 5 + col]
            x = MARGIN + col * (col_w + gap_x)
            d.rectangle([x, y0, x + col_w - 1, y0 + art_h - 1],
                        outline=INK, width=1)
            TILE_ART[tile["art"]](d, x + 1, y0 + 1, col_w - 2, art_h - 2, rng)
            y = y0 + art_h + 2
            # red fact bar below the art
            ff = sans_b(11)
            fact = tile["fact"]
            while d.textlength(fact, font=ff) > col_w - 8 and ff.size > 8:
                ff = sans_b(ff.size - 1)
            d.rectangle([x, y, x + col_w - 1, y + 15], fill=RED)
            d.text((x + 4, y + 2), fact, font=ff, fill=WHITE)
            y += 19
            # kicker line: number, place, beat left; source right (never overlap)
            kick = "%s \u00b7 %s \u2014 %s" % (tile["num"], tile["place"], tile["beat"])
            sf = sans(8)
            src_w = d.textlength(tile["source"], font=sf)
            kf = sans_b(9)
            while d.textlength(kick, font=kf) > col_w - src_w - 8 and kf.size > 7:
                kf = sans_b(kf.size - 1)
            d.text((x, y), kick, font=kf, fill=RED)
            d.text((x + col_w - src_w, y + 1), tile["source"], font=sf, fill=GREY)
            y += 13
            title_lines = wrap(d, tile["title"], serif(12), col_w)
            y = draw_lines(d, x, y, title_lines[:3], serif(12), INK, leading=14)
            y += 2
            body_lines = wrap(d, tile["body"], sans(9), col_w)
            draw_lines(d, x, y, body_lines[:2], sans(9), INK, leading=11)


def draw_also_item(d, x, y, num, place, text, source, col_w):
    """One brief on a single line; shrinks the font if it would overflow."""
    size = 9
    while size >= 8:
        bf, rf = sans_b(size), sans(size)
        prefix = "%s %s \u2014 " % (num, place)
        rest = "%s (%s)" % (text, source)
        if (d.textlength(prefix, font=bf) + d.textlength(rest, font=rf)) <= col_w:
            break
        size -= 0.5
    bf, rf = sans_b(size), sans(size)
    prefix = "%s %s \u2014 " % (num, place)
    d.text((x, y), prefix, font=bf, fill=INK)
    d.text((x + d.textlength(prefix, font=bf), y), rest, font=rf, fill=INK)


def draw_bottom(d, rng):
    y0 = 790
    # --- left: world map
    map_x, map_w = MARGIN, 322
    d.text((map_x, y0), "WHERE IT HAPPENED", font=sans_b(13), fill=INK)
    draw_world_map(d, map_x, y0 + 18, map_w, 104, rng)
    d.text((map_x, y0 + 126), "1\u20133 Lead \u00b7 4\u201313 Features.",
           font=sans(9), fill=GREY)
    d.text((map_x, y0 + 137), "5 Mercury is in space \u2014 no pin.",
           font=sans(9), fill=GREY)
    # --- right: also list, two columns
    ax = MARGIN + map_w + 12
    aw = W - MARGIN - ax
    d.text((ax, y0), "ALSO ON FRIDAY 20 NOVEMBER \u2014 23 MORE STORIES",
           font=sans_b(13), fill=INK)
    legend = [("Europe", BLUE), ("Asia-Pacific", (196, 92, 32)),
              ("Americas", RED_DARK), ("Africa", (120, 96, 32)),
              ("Middle East", TEAL), ("Sport & science", GREY)]
    lx = ax
    for name, col in legend:
        d.rectangle([lx, y0 + 19, lx + 7, y0 + 26], fill=col)
        d.text((lx + 10, y0 + 18), name, font=sans(8), fill=GREY)
        lx += 10 + int(d.textlength(name, font=sans(8))) + 10
    col_w = (aw - 14) // 2
    left_items, right_items = ALSO[:12], ALSO[12:]
    for ci, items in enumerate((left_items, right_items)):
        cx = ax + ci * (col_w + 14)
        cy = y0 + 34
        for num, place, text, source in items:
            draw_also_item(d, cx, cy, num, place, text, source, col_w)
            cy += 10


def draw_date_check(d):
    y0 = 936
    d.rectangle([MARGIN, y0, W - MARGIN - 1, y0 + 42], outline=RED, width=2)
    d.rectangle([MARGIN, y0, MARGIN + 88, y0 + 42], fill=RED)
    d.text((MARGIN + 10, y0 + 5), "DATE", font=sans_b(14), fill=WHITE)
    d.text((MARGIN + 10, y0 + 21), "CHECK", font=sans_b(14), fill=WHITE)
    tx = MARGIN + 98
    tw = W - MARGIN - tx - 8
    d.text((tx, y0 + 4), "First reported Thursday 19 Nov, so NOT shown as Friday\u2019s news:",
           font=sans_b(11), fill=INK)
    joined = " \u00b7 ".join(DATE_CHECK_ITEMS) + "."
    lines = wrap(d, joined, sans(10.5), tw)
    draw_lines(d, tx, y0 + 19, lines[:2], sans(10.5), INK, leading=12)


def draw_footer(d):
    lines = wrap(d, FOOTER, sans(9.5), CW)
    y = 986
    for line in lines:
        lw = d.textlength(line, font=sans(9.5))
        d.text(((W - lw) // 2, y), line, font=sans(9.5), fill=GREY)
        y += 12


def render(out_path):
    rng = random.Random(20261120)
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    speckle(d, rng, 0, 0, W - 1, H - 1, 4200)
    d.rectangle([6, 6, W - 7, H - 7], outline=INK, width=2)
    draw_masthead(d)
    draw_stats(d)
    draw_regions(d)
    draw_leads(d, rng)
    rule(d, MARGIN, 460, CW, weight=1, fill=FAINT)
    draw_tiles(d, rng)
    rule(d, MARGIN, 782, CW, weight=1, fill=FAINT)
    draw_bottom(d, rng)
    draw_date_check(d)
    draw_footer(d)
    img.save(out_path, format="PNG", optimize=True)


if __name__ == "__main__":
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", ".")
    os.makedirs(out_dir, exist_ok=True)
    render(os.path.join(out_dir, "entry.png"))
