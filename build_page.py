#!/usr/bin/env python3
"""Build the front page for 'Sum up 17 November's world news in one image'.

Draws an original 1024x1024 newspaper front page with PIL: masthead, hero
stories with generated photos, a card grid, a dot world map and an 'also'
list. Run:  python3 build_page.py   -> writes entry.png (JPEG bytes).
"""
import glob
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")

W, H = 1024, 1024
MARGIN = 24
CW = W - 2 * MARGIN  # 976

PAPER = (250, 246, 236)
INK = (17, 17, 17)
MUTED = (74, 74, 74)
RULE = (180, 172, 150)
CARD_BG = (255, 253, 246)
RED = (158, 27, 27)
SEA = (214, 228, 236)
LAND = (58, 84, 99)
PANEL = (28, 42, 54)

SERIF_B = [
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
]
SERIF = [
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
]
SERIF_I = [
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
]
SANS_B = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
SANS = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def font(paths, size):
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def photo_cover(path, w, h):
    """Center-crop an image to fill w x h, then resize."""
    im = Image.open(path).convert("RGB")
    sw, sh = im.size
    target = w / h
    src = sw / sh
    if src > target:  # too wide: crop sides
        nw = int(sh * target)
        x0 = (sw - nw) // 2
        im = im.crop((x0, 0, x0 + nw, sh))
    else:  # too tall: crop top/bottom
        nh = int(sw / target)
        y0 = (sh - nh) // 2
        im = im.crop((0, y0, sw, y0 + nh))
    return im.resize((w, h), Image.LANCZOS)


def find_asset(stem):
    hits = sorted(glob.glob(os.path.join(ASSETS, "media-generation-%s-*.webp" % stem)))
    if not hits:
        raise FileNotFoundError(stem)
    return hits[0]


def draw_kicker(draw, x, y, text, size=13):
    f = font(SANS_B, size)
    draw.text((x, y), text, font=f, fill=RED)
    return f


def draw_headline(draw, x, y, text, size, max_w, max_lines=3):
    f = font(SERIF_B, size)
    lines = wrap(draw, text, f, max_w)[:max_lines]
    for i, line in enumerate(lines):
        draw.text((x, y + i * int(size * 1.12)), line, font=f, fill=INK)
    return y + len(lines) * int(size * 1.12)


def draw_deck(draw, x, y, text, size, max_w, max_lines=3, fill=MUTED):
    f = font(SERIF, size)
    lines = wrap(draw, text, f, max_w)[:max_lines]
    for i, line in enumerate(lines):
        draw.text((x, y + i * int(size * 1.28)), line, font=f, fill=fill)
    return y + len(lines) * int(size * 1.28)


# ---- dot world map: land cells as (start, end) column ranges per row ----
# 52 columns, lon -170..+177; 22 rows, lat 72..-41.
MAP_ROWS = [
    [(2, 6), (8, 15), (17, 20), (28, 50)],
    [(1, 7), (8, 16), (17, 19), (25, 26), (27, 51)],
    [(2, 17), (22, 22), (24, 27), (28, 51)],
    [(6, 18), (22, 23), (24, 26), (27, 51)],
    [(6, 19), (23, 30), (31, 44), (46, 50)],
    [(5, 19), (23, 28), (31, 46), (49, 50)],
    [(5, 18), (23, 29), (33, 45), (48, 50)],
    [(6, 17), (22, 30), (31, 35), (36, 44), (48, 49)],
    [(6, 15), (21, 31), (32, 38), (39, 43), (45, 45)],
    [(6, 13), (21, 32), (33, 36), (37, 40), (41, 44)],
    [(7, 12), (21, 33), (38, 39), (41, 44)],
    [(8, 11), (22, 33), (41, 44)],
    [(9, 14), (22, 33), (42, 47)],
    [(10, 15), (22, 32), (43, 48), (49, 51)],
    [(10, 15), (23, 32), (44, 47)],
    [(10, 15), (23, 31), (46, 50)],
    [(10, 15), (23, 30), (45, 50)],
    [(10, 14), (24, 29), (45, 50)],
    [(10, 14), (24, 29), (45, 50)],
    [(10, 13), (24, 28), (46, 50)],
    [(10, 13), (25, 27), (46, 49), (51, 51)],
    [(10, 12), (50, 51)],
]

# (number, name, lat, lon, legend text)
MARKERS = [
    (1, "Kerch Bridge", 45.3, 36.5, "Kerch Bridge — road span down"),
    (2, "Bahrain", 26.0, 50.5, "Bahrain — drones fired at U.S. radar"),
    (3, "Manila", 14.6, 121.0, "Manila — Quad mineral deals"),
    (4, "Paris", 48.8, 2.3, "Paris — strike over pay"),
    (5, "Ulaanbaatar", 47.9, 106.9, "Ulaanbaatar — president quits"),
    (6, "DR Congo", -2.9, 23.7, "DR Congo — Ebola tops 11,000"),
    (7, "Andhra Pradesh", 15.9, 80.0, "Andhra Pradesh — cyclone nears"),
    (8, "Tokyo", 35.7, 139.7, "Tokyo — jets scrambled"),
    (9, "Washington", 38.9, -77.0, "Washington — Dow −849; audit fails"),
    (10, "Dakar", 14.7, -17.4, "Dakar — Youth Olympics open"),
    (11, "Brasilia", -15.8, -47.9, "Brasília — tourism target hit"),
    (12, "Jerusalem", 31.8, 35.2, "Jerusalem — unity talks collapse"),
]


def draw_map(draw, x0, y0, w, h):
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=SEA, outline=RULE, width=1)
    cw, ch = w / 52.0, h / 22.0
    for r, ranges in enumerate(MAP_ROWS):
        cy = y0 + (r + 0.5) * ch
        for a, b in ranges:
            for c in range(a, b + 1):
                cx = x0 + (c + 0.5) * cw
                draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=LAND)
    fnum = font(SANS_B, 10)
    for num, _name, lat, lon, _leg in MARKERS:
        col = (lon + 170) / 6.8
        row = (72 - lat) / 5.4
        cx = x0 + (col + 0.5) * cw
        cy = y0 + (row + 0.5) * ch
        draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=RED, outline=(255, 255, 255), width=1)
        t = str(num)
        tw = draw.textlength(t, font=fnum)
        draw.text((cx - tw / 2, cy - 6), t, font=fnum, fill=(255, 255, 255))


def draw_panel_number(draw, x, y, w, h, big, small):
    draw.rectangle([x, y, x + w, y + h], fill=PANEL)
    # shrink the big text until it fits the panel width
    size = 26
    fb = font(SERIF_B, size)
    while size > 13 and draw.textlength(big, font=fb) > w - 8:
        size -= 1
        fb = font(SERIF_B, size)
    tw = draw.textlength(big, font=fb)
    draw.text((x + (w - tw) / 2, y + 12), big, font=fb, fill=(255, 255, 255))
    fs = font(SANS_B, 10)
    lines = wrap(draw, small, fs, w - 12)
    ly = y + h - 8 - len(lines) * 12
    for line in lines:
        lw = draw.textlength(line, font=fs)
        draw.text((x + (w - lw) / 2, ly), line, font=fs, fill=(196, 210, 220))
        ly += 12


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---------- header ----------
    d.line([(MARGIN, 8), (W - MARGIN, 8)], fill=INK, width=2)
    f_top = font(SANS, 11)
    d.text((MARGIN, 12), "WORLD EDITION", font=f_top, fill=MUTED)
    right = "ONE DAY · ONE PAGE · THE WHOLE WORLD"
    d.text((W - MARGIN - d.textlength(right, font=f_top), 12), right, font=f_top, fill=MUTED)

    f_mast = font(SERIF_B, 64)
    title = "THE WORLD TODAY"
    tw = d.textlength(title, font=f_mast)
    d.text(((W - tw) / 2, 24), title, font=f_mast, fill=INK)
    d.line([(MARGIN, 96), (W - MARGIN, 96)], fill=INK, width=3)
    d.line([(MARGIN, 100), (W - MARGIN, 100)], fill=INK, width=1)

    # date band
    d.rectangle([MARGIN, 104, W - MARGIN, 128], fill=INK)
    f_date = font(SERIF_B, 18)
    date = "TUESDAY, 17 NOVEMBER 2026"
    dw = d.textlength(date, font=f_date)
    d.text(((W - dw) / 2, 108), date, font=f_date, fill=(255, 255, 255))

    # ---------- hero 1: Kerch Bridge ----------
    hx, hy = MARGIN, 136
    photo = photo_cover(find_asset("hero-bridge"), 596, 200)
    img.paste(photo, (hx, hy))
    d.rectangle([hx, hy, hx + 596, hy + 200], outline=RULE, width=1)

    tx = hx + 612
    tw_ = W - MARGIN - tx
    draw_kicker(d, tx, hy, "UKRAINE · WAR IN EUROPE")
    y = draw_headline(d, tx, hy + 18, "UKRAINE DROPS THE KERCH BRIDGE", 32, tw_, 2)
    draw_deck(d, tx, y + 8,
              "Drones and missiles collapse the road arch of the Crimea link in a "
              "seven-stage operation Zelenskyy calls \u201cunprecedented\u201d — as "
              "Russian strikes hit Kyiv\u2019s Dnipro bridges.",
              14, tw_, 4)

    # ---------- heroes 2 & 3 ----------
    hy2 = 344
    col_w = (CW - 12) // 2
    heroes = [
        ("hero-carrier", "MIDDLE EAST · GULF TENSIONS",
         "IRAN FIRES ON U.S. RADAR IN BAHRAIN",
         "Drones intercepted, no casualties; tankers hit mines near Hormuz as a "
         "third U.S. carrier arrives."),
        ("hero-summit", "ASIA · DIPLOMACY",
         "QUAD STRIKES MINERAL DEALS IN MANILA",
         "Trump says the four nations will match China on rare earths in 10 months; "
         "Xi, Trump and Putin to meet Thursday."),
    ]
    for i, (stem, kicker, head, deck) in enumerate(heroes):
        x = MARGIN + i * (col_w + 12)
        p = photo_cover(find_asset(stem), col_w, 104)
        img.paste(p, (x, hy2))
        d.rectangle([x, hy2, x + col_w, hy2 + 104], outline=RULE, width=1)
        draw_kicker(d, x, hy2 + 110, kicker, 12)
        # shrink headline until the whole thing fits on one line (never truncate)
        hsize = 22
        while hsize > 15 and d.textlength(head, font=font(SERIF_B, hsize)) > col_w:
            hsize -= 1
        y = draw_headline(d, x, hy2 + 126, head, hsize, col_w, 1)
        draw_deck(d, x, y + 4, deck, 12, col_w, 2)

    # ---------- card grid: 4 cols x 2 rows ----------
    gy = 548
    gap = 8
    cw2 = (CW - 3 * gap) // 4
    ch2 = 92
    cards = [
        ("photo", "card-traders", "MARKETS",
         "DOW TUMBLES 849 POINTS",
         "Fourth straight down day; S&P −1.03%, Nasdaq −0.74%."),
        ("panel", ("$115.8B", "NVIDIA RECORD QUARTER"), "TECH",
         "NVIDIA POSTS RECORD QUARTER",
         "Sales double in first report since Huang\u2019s exit."),
        ("photo", "card-vaccine", "HEALTH",
         "U.S. LOSES MEASLES-FREE STATUS",
         "PAHO also strips Mexico and Bolivia."),
        ("panel", ("11,000", "EBOLA CASES IN CONGO"), "HEALTH",
         "EBOLA PASSES 11,000 CASES",
         "More than 5,400 dead in the Bundibugyo outbreak."),
        ("photo", "card-protest", "EUROPE",
         "FRANCE STRIKES OVER PAY",
         "146,000 march in third stoppage over pay."),
        ("photo", "card-cyclone", "WEATHER",
         "CYCLONE AKVAN NEARS INDIA",
         "Andhra Pradesh braces for Friday landfall."),
        ("photo", "card-football", "SPORT",
         "SENEGAL FIRST INTO AFCON 2027",
         "Morocco qualify too; Nigeria held 0–0 by Tanzania."),
        ("panel", ("RESIGNS", "MONGOLIA PRESIDENT"), "ASIA",
         "MONGOLIA\u2019S PRESIDENT RESIGNS",
         "Khurelsukh quits over graft claims, denies wrongdoing."),
    ]
    for i, (kind, art, kicker, head, deck) in enumerate(cards):
        cx = MARGIN + (i % 4) * (cw2 + gap)
        cy = gy + (i // 4) * (ch2 + gap)
        d.rectangle([cx, cy, cx + cw2, cy + ch2], fill=CARD_BG, outline=RULE, width=1)
        tw2 = 88
        if kind == "photo":
            p = photo_cover(find_asset(art), tw2, ch2)
            img.paste(p, (cx, cy))
        else:
            draw_panel_number(d, cx, cy, tw2, ch2, art[0], art[1])
        tx2 = cx + tw2 + 7
        tw3 = cw2 - tw2 - 13
        draw_kicker(d, tx2, cy + 5, kicker, 10)
        y = draw_headline(d, tx2, cy + 19, head, 13, tw3, 2)
        draw_deck(d, tx2, y + 3, deck, 10, tw3, 2)

    # ---------- world map + legend ----------
    my = 748
    d.line([(MARGIN, my), (W - MARGIN, my)], fill=INK, width=2)
    draw_kicker(d, MARGIN, my + 6, "WHERE IT HAPPENED · 17 NOVEMBER 2026", 13)
    map_x, map_y, map_w, map_h = MARGIN, my + 26, 400, 110
    draw_map(d, map_x, map_y, map_w, map_h)
    lx = map_x + map_w + 16
    lw = W - MARGIN - lx
    f_leg = font(SANS, 12)
    half = 6
    for i, (_n, _nm, _la, _lo, leg) in enumerate(MARKERS):
        col = 0 if i < half else 1
        row = i % half
        x = lx + col * (lw // 2)
        y = map_y + 4 + row * 18
        d.text((x, y), leg, font=f_leg, fill=INK)

    # ---------- also list ----------
    ay = 894
    d.line([(MARGIN, ay), (W - MARGIN, ay)], fill=INK, width=2)
    draw_kicker(d, MARGIN, ay + 6, "ALSO ON TUESDAY", 13)
    also = [
        "Japan scrambles jets as Russian planes enter airspace",
        "Knesset elects Kahana speaker; no vote-buying found",
        "UK sanctions firms building West Bank settlements",
        "Houthis advance in Yemen; government retreats to Aden",
        "Pentagon fails its audit for a ninth straight year",
        "Sözcü TV seized in Turkey; trustee takes over",
        "COP31 launches ocean pact; Gaza climate line proposed",
        "Five EU states press Rwanda return-hub plan",
        "Chase bug slows U.S. payments; Zelle delays",
        "Voyager 1 nears one light-day from Earth",
        "Cosmic dust hints at hidden water beyond Neptune",
        "Brazil 7–0 Singapore as Vinícius nets hat-trick",
        "White House: agencies need OK before testifying",
        "Latin America: Catholics fall to 55% in 30 years",
        "UN: 128 states debate a ban on killer robots",
        "Salesforce −9% as software sell-off deepens",
    ]
    f_also = font(SERIF, 12)
    per_col = 6
    colw = CW // 3
    for i, item in enumerate(also):
        col = i // per_col
        row = i % per_col
        x = MARGIN + col * colw
        y = ay + 26 + row * 14
        d.text((x, y), "•  " + item, font=f_also, fill=INK)

    # ---------- footer ----------
    d.line([(MARGIN, 1008), (W - MARGIN, 1008)], fill=RULE, width=1)
    f_foot = font(SANS, 9)
    foot = ("All stories verified against reporting of Tuesday 17 November 2026  ·  "
            "Illustrations rendered for this edition  ·  THE WORLD TODAY")
    fw = d.textlength(foot, font=f_foot)
    d.text(((W - fw) / 2, 1011), foot, font=f_foot, fill=MUTED)

    out = os.path.join(HERE, "entry.png")
    img.save(out, "JPEG", quality=88, optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
