"""Render entry.png: a one-page front page for Saturday 21 November 2026.

Run with Pillow installed:  python3 draw_entry.py
Everything is drawn with plain PIL shapes and DejaVu fonts; no network.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (245, 238, 222)
INK = (24, 22, 20)
GREY = (92, 88, 82)
RED = (196, 30, 36)
NIGHT = (30, 32, 44)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
SANS_B = FONT_DIR + "DejaVuSans-Bold.ttf"
SANS = FONT_DIR + "DejaVuSans.ttf"
SERIF_B = FONT_DIR + "DejaVuSerif-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(d, s, f):
    b = d.textbbox((0, 0), s, font=f)
    return b[2] - b[0]


def wrap(d, s, f, max_w):
    lines, cur = [], ""
    for word in s.split():
        trial = (cur + " " + word).strip()
        if text_w(d, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(d, s, path, max_w, max_lines, start, smallest):
    """Largest size (<= start) where s wraps into max_lines within max_w."""
    for size in range(start, smallest - 1, -1):
        f = font(path, size)
        lines = wrap(d, s, f, max_w)
        if len(lines) <= max_lines and all(text_w(d, l, f) <= max_w for l in lines):
            return f, lines
    raise SystemExit("does not fit: " + s)


def block(d, x, y, lines, f, fill, gap=1.12):
    asc, desc = f.getmetrics()
    step = int((asc + desc) * gap)
    for line in lines:
        d.text((x, y), line, font=f, fill=fill)
        y += step
    return y


# ---------------------------------------------------------------- pictograms

def star(d, cx, cy, r_out, r_in, n, fill):
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.pi * i / n - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=fill)


def curve(d, p0, p1, p2, fill, width, steps=40):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        pts.append((x, y))
    d.line(pts, fill=fill, width=width, joint="curve")


def riyadh_panel(d, x0, y0, x1, y1):
    d.rectangle((x0, y0, x1, y1), fill=NIGHT)
    w, h = x1 - x0, y1 - y0
    # crescent moon
    mx, my = x0 + 60, y0 + 55
    d.ellipse((mx - 24, my - 24, mx + 24, my + 24), fill=PAPER)
    d.ellipse((mx - 14, my - 30, mx + 30, my + 18), fill=NIGHT)
    # missile trails from the south, ending in interception bursts
    bursts = [(x0 + 0.30 * w, y0 + 0.22 * h), (x0 + 0.56 * w, y0 + 0.14 * h),
              (x0 + 0.80 * w, y0 + 0.30 * h)]
    for i, (bx, by) in enumerate(bursts):
        sx = x1 - 10 - i * 28
        curve(d, (sx, y1 - 120), (bx + 80, by + 40), (bx, by), (170, 170, 178), 5)
        star(d, bx, by, 40, 16, 8, RED)
        star(d, bx, by, 18, 8, 8, (255, 214, 120))
    # skyline
    base = y1 - 70
    heights = [70, 110, 85, 140, 95, 60, 120, 80, 100, 65]
    bx = x0
    bw = (w - 60) // len(heights)
    for i, bh in enumerate(heights):
        left = bx + i * bw + (60 if i >= 4 else 0)
        d.rectangle((left, base - bh, left + bw - 6, y1), fill=(58, 60, 74))
        for wy in range(int(base - bh + 12), y1 - 10, 22):
            d.rectangle((left + 8, wy, left + 14, wy + 8), fill=(214, 190, 120))
    # PIF tower: the tallest, with notched crown
    tx = x0 + 4 * bw + 4
    d.polygon([(tx, y1), (tx + 4, base - 230), (tx + 26, base - 262),
               (tx + 48, base - 230), (tx + 52, y1)], fill=(78, 80, 96))
    d.rectangle((x0, y1 - 34, x1, y1), fill=INK)
    f = font(SANS_B, 22)
    label = "3 BALLISTIC MISSILES INTERCEPTED"
    d.text((x0 + (w - text_w(d, label, f)) // 2, y1 - 30), label, font=f, fill=PAPER)


def cop_icon(d, x, y, s):
    # globe
    r = s * 0.36
    cx, cy = x + s * 0.40, y + s * 0.50
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=INK, width=4)
    d.ellipse((cx - r * 0.45, cy - r, cx + r * 0.45, cy + r), outline=INK, width=3)
    d.line((cx - r, cy, cx + r, cy), fill=INK, width=3)
    # thermometer
    tx = x + s * 0.92
    d.rounded_rectangle((tx - 9, y + s * 0.12, tx + 9, y + s * 0.78), 9, outline=INK, width=3)
    d.rectangle((tx - 3, y + s * 0.30, tx + 3, y + s * 0.80), fill=RED)
    d.ellipse((tx - 16, y + s * 0.72, tx + 16, y + s * 0.92), fill=RED)
    # clock running past time
    ccx, ccy, cr = x + s * 1.45, y + s * 0.50, s * 0.30
    d.ellipse((ccx - cr, ccy - cr, ccx + cr, ccy + cr), fill=PAPER, outline=INK, width=4)
    d.line((ccx, ccy, ccx, ccy - cr * 0.75), fill=INK, width=4)
    d.line((ccx, ccy, ccx + cr * 0.55, ccy + cr * 0.25), fill=RED, width=4)


def quake_icon(d, x, y, s):
    d.polygon([(x, y + s * 0.95), (x + s * 0.45, y + s * 0.25), (x + s * 0.75, y + s * 0.60),
               (x + s * 1.05, y + s * 0.10), (x + s * 1.60, y + s * 0.95)], fill=(120, 112, 100))
    d.polygon([(x + s * 0.97, y + s * 0.22), (x + s * 1.05, y + s * 0.10),
               (x + s * 1.13, y + s * 0.22)], fill=PAPER)
    pts, base = [], y + s * 0.70
    amps = [0, 2, -3, 4, -10, 22, -14, 18, -12, 8, -4, 2, 0]
    for i, a in enumerate(amps):
        pts.append((x + i * s * 1.6 / (len(amps) - 1), base - a))
    d.line(pts, fill=RED, width=5, joint="curve")
    f = font(SANS_B, int(s * 0.42))
    d.text((x + s * 1.18, y - 4), "6.7", font=f, fill=RED)


def cyclone_icon(d, x, y, s):
    # the weather-map cyclone symbol: a ring with two curling arms
    cx, cy, r = x + s * 0.55, y + s * 0.50, s * 0.20
    for k in (0, 1):
        pts = []
        for i in range(40):
            t = i / 39
            a = k * math.pi + t * 2.4
            rr = r + t * s * 0.30
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        d.line(pts, fill=RED, width=10, joint="curve")
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=RED, width=10)
    # small islands on the sea line
    sea = y + s * 0.92
    d.line((x + s * 1.05, sea, x + s * 1.85, sea), fill=INK, width=3)
    for ix, iw, ih in ((1.12, 0.20, 0.12), (1.40, 0.12, 0.08), (1.60, 0.18, 0.10)):
        d.chord((x + s * ix, sea - s * ih, x + s * (ix + iw), sea + s * ih), 180, 360, fill=(120, 112, 100))
    # palm on the largest island
    px = x + s * 1.22
    d.line((px, sea - s * 0.10, px + 4, sea - s * 0.48), fill=INK, width=4)
    for dx, dy in ((-22, 6), (22, 4), (-14, -10), (16, -12)):
        d.line((px + 4, sea - s * 0.48, px + 4 + dx, sea - s * 0.48 + dy + 8), fill=INK, width=4)


def factory_icon(d, x, y, s):
    base = y + s * 0.95
    d.rectangle((x, y + s * 0.45, x + s * 1.05, base), fill=(120, 112, 100))
    for i in range(3):
        lx = x + i * s * 0.35
        d.polygon([(lx, y + s * 0.45), (lx + s * 0.35, y + s * 0.22), (lx + s * 0.35, y + s * 0.45)],
                  fill=(120, 112, 100))
    d.rectangle((x + s * 0.80, y + s * 0.02, x + s * 0.92, y + s * 0.45), fill=(120, 112, 100))
    for i in range(3):
        d.rectangle((x + s * (0.10 + i * 0.32), y + s * 0.60, x + s * (0.28 + i * 0.32), y + s * 0.78), fill=PAPER)
    # school desk with a chalkboard
    bx = x + s * 1.18
    d.rectangle((bx, y + s * 0.20, bx + s * 0.62, y + s * 0.58), fill=(46, 74, 58), outline=INK, width=3)
    fb = font(SANS_B, int(s * 0.18))
    d.text((bx + s * 0.10, y + s * 0.28), "ABC", font=fb, fill=PAPER)
    d.rectangle((bx + s * 0.05, y + s * 0.70, bx + s * 0.57, y + s * 0.76), fill=INK)
    d.line((bx + s * 0.10, y + s * 0.76, bx + s * 0.10, base), fill=INK, width=4)
    d.line((bx + s * 0.52, y + s * 0.76, bx + s * 0.52, base), fill=INK, width=4)
    # red star badge (state emblem cue)
    d.ellipse((x + s * 1.30, y - s * 0.34, x + s * 1.62, y - s * 0.02), fill=PAPER, outline=RED, width=3)
    star(d, x + s * 1.46, y - s * 0.18, s * 0.12, s * 0.05, 5, RED)


def cricket_icon(d, x, y, s):
    """Rahul's 136: the final score over a tilted bat and ball."""
    f = font(SERIF_B, int(s * 0.46))
    d.text((x + s * 0.20, y - s * 0.40), "136", font=f, fill=RED)
    a = math.radians(-35)

    def rot(px, py):
        return (x + s * 0.70 + px * math.cos(a) - py * math.sin(a),
                y + s * 0.55 + px * math.sin(a) + py * math.cos(a))
    blade = [rot(-14, -10), rot(14, -10), rot(16, 70), rot(-16, 70)]
    handle = [rot(-5, -55), rot(5, -55), rot(5, -10), rot(-5, -10)]
    d.polygon(blade, fill=(214, 182, 120), outline=INK)
    d.polygon(handle, fill=INK)
    bx, by = x + s * 1.30, y + s * 0.95
    d.ellipse((bx - 12, by - 12, bx + 12, by + 12), fill=RED)


# ---------------------------------------------------------------- page

def story(d, x, y, w, tag, head, deck, head_size, head_lines, deck_size=19, limit=H):
    """Tag, headline and deck; the headline shrinks until the block fits above limit."""
    ft = font(SANS_B, 16)
    for size in range(head_size, 19, -1):
        fh, lines = fit(d, head, SANS_B, w, head_lines, size, 20)
        asc, desc = fh.getmetrics()
        hy = y + 24 + len(lines) * int((asc + desc) * 1.05) + 6
        fd, dl = fit(d, deck, SANS, w, 2, deck_size, 15)
        a2, d2 = fd.getmetrics()
        end = hy + len(dl) * int((a2 + d2) * 1.12)
        if end <= limit:
            break
    else:
        raise SystemExit("overflow: " + head)
    d.text((x, y), tag, font=ft, fill=RED)
    block(d, x, y + 24, lines, fh, INK, 1.05)
    return block(d, x, hy, dl, fd, GREY, 1.12)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 28

    # masthead
    fm, _ = fit(d, "THE WORLD IN ONE DAY", SERIF_B, W - 2 * M, 1, 76, 40)
    mw = text_w(d, "THE WORLD IN ONE DAY", fm)
    d.text(((W - mw) // 2, 14), "THE WORLD IN ONE DAY", font=fm, fill=INK)
    d.line((M, 104, W - M, 104), fill=INK, width=3)
    # date band
    d.rectangle((M, 112, W - M, 166), fill=RED)
    fdte = font(SANS_B, 40)
    date = "SATURDAY 21 NOVEMBER 2026"
    d.text(((W - text_w(d, date, fdte)) // 2, 116), date, font=fdte, fill=PAPER)

    # lead story: about 40% of the page
    top, bottom = 180, 516
    riyadh_panel(d, M, top, M + 450, bottom)
    tx = M + 472
    tw = W - M - tx
    y = story(d, tx, top + 2, tw, "TOP STORY · MIDDLE EAST",
              "HOUTHI MISSILES DOWNED OVER RIYADH",
              "Saudi-led coalition intercepts 3 ballistic missiles fired at the capital; a Houthi drone downed hours later",
              58, 4, 23, bottom - 56)
    fx = font(SANS_B, 20)
    extra = wrap(d, "Second strike on the capital in days, after the PIF Tower was hit on Thursday", fx, tw)
    d.line((tx, y + 6, tx + 60, y + 6), fill=RED, width=3)
    block(d, tx, y + 14, extra, fx, INK, 1.1)
    d.line((M, bottom + 12, W - M, bottom + 12), fill=INK, width=2)

    # row one: two wide cells, pictogram left of the text
    g = 18
    cw2 = (W - 2 * M - g) // 2
    ry = bottom + 24
    row_end = ry + 224
    cells = [
        (cop_icon, "CLIMATE · TÜRKIYE", "COP31 TALKS MISS DEADLINE, NO DEAL",
         "Third draft due Saturday; COP32 goes to Addis Ababa in 2027"),
        (quake_icon, "AMERICAS · PERU", "M6.7 QUAKE HURTS 8 IN JUNÍN",
         "128 homes hit, 4 destroyed; felt in Lima, no deaths"),
    ]
    for i, (icon, tag, head, deck) in enumerate(cells):
        cx = M + i * (cw2 + g)
        icon(d, cx + 2, ry + 60, 84 if icon is quake_icon else 92)
        story(d, cx + 176, ry + 8, cw2 - 176, tag, head, deck, 32, 3, 18, row_end)
        if i:
            d.line((cx - g // 2, ry, cx - g // 2, row_end), fill=(180, 172, 158), width=1)
    d.line((M, row_end + 8, W - M, row_end + 8), fill=INK, width=2)

    # row two: two wide cells, pictogram left of the text
    ry2 = row_end + 20
    wide = [
        (factory_icon, "ASIA · NORTH KOREA", "KIM TOURS FACTORY, NO TRUMP MEETING",
         "KCNA shows school-equipment factory tour after Trump left Asia"),
        (cricket_icon, "SPORT · CRICKET · NZ", "RAHUL 136 PUTS INDIA ON TOP",
         "First Indian opener with tons in every SENA land; Gill falls two short"),
    ]
    for i, (icon, tag, head, deck) in enumerate(wide):
        cx = M + i * (cw2 + g)
        icon(d, cx + 2, ry2 + 40, 84)
        story(d, cx + 176, ry2, cw2 - 176, tag, head, deck, 30, 3, 17, H - 40)
        if i:
            d.line((cx - g // 2, ry2, cx - g // 2, H - 44), fill=(180, 172, 158), width=1)

    ff = font(SANS, 15)
    foot = "Events reported on Saturday 21 November 2026"
    d.line((M, H - 34, W - M, H - 34), fill=INK, width=1)
    d.text(((W - text_w(d, foot, ff)) // 2, H - 28), foot, font=ff, fill=GREY)

    img.save("entry.png", optimize=True)


if __name__ == "__main__":
    main()
