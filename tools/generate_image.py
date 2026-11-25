#!/usr/bin/env python3
"""Build the front page for Wednesday, 25 November 2026.

Reads the AI-generated lead photograph (two tankers burning in the
Strait of Hormuz) from tools/, crops it to the lead slot, and draws the
rest of the page -- masthead, date band, headlines and story panels --
with Pillow and the system Liberation fonts. Every story on the page
was reported on 25 November 2026; nothing from another day is used.

Run from the repo root:  python3 tools/generate_image.py
Writes entry.png (1024 x 1024, under 1 MiB) next to this repo's root.
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LEAD_PHOTO = os.path.join(
    HERE, "media-generation-hormuz-tankers-0-fc58223d-8ec3-4250-84bd-6ac07cac3664.jpg"
)
OUT = os.path.join(ROOT, "entry.png")

PAGE_W, PAGE_H = 1024, 1024
EDGE = 32
BLACK = (18, 18, 18)
CRIMSON = (172, 32, 32)
NAVY = (20, 68, 118)
PAPER = (253, 251, 245)
MIDGREY = (96, 96, 96)
LINECOL = (158, 158, 158)

SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def load(path, size):
    return ImageFont.truetype(path, size)


def split_lines(canvas, text, face, width):
    """Greedy wrap of text into lines no wider than width pixels."""
    out, current = [], ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if canvas.textlength(trial, font=face) <= width:
            current = trial
        else:
            if current:
                out.append(current)
            current = word
    if current:
        out.append(current)
    return out


def write_lines(canvas, lines, face, x, y, colour=BLACK):
    step = int(face.size * 1.22)
    for line in lines:
        canvas.text((x, y), line, font=face, fill=colour)
        y += step
    return y


def story_box(canvas, x, y, w, h, tag, title, body, title_size=22, body_size=15):
    """One bordered panel: red tag, serif headline, sans body text."""
    title_face = load(SERIF_BOLD, title_size)
    body_face = load(SANS, body_size)
    title_lines = split_lines(canvas, title, title_face, w - 26)
    body_lines = split_lines(canvas, body, body_face, w - 26)
    needed = (12 + 21 + len(title_lines) * int(title_size * 1.22)
              + 5 + len(body_lines) * int(body_size * 1.22) + 10)
    if needed > h:
        raise SystemExit(
            f"panel {tag!r} needs {needed}px but has {h}px: "
            f"{len(title_lines)} title + {len(body_lines)} body lines")
    canvas.rectangle([x, y, x + w, y + h], outline=LINECOL, width=1)
    px = x + 13
    top = y + 11
    canvas.text((px, top), tag, font=load(SANS_BOLD, 12), fill=CRIMSON)
    top += 21
    top = write_lines(canvas, title_lines, title_face, px, top)
    write_lines(canvas, body_lines, body_face, px, top + 5)


def main():
    page = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    d = ImageDraw.Draw(page)

    # Top rule and small caps line.
    d.line([(EDGE, 20), (PAGE_W - EDGE, 20)], fill=BLACK, width=2)
    d.text((EDGE, 27), "THE WORLD IN ONE PAGE",
           font=load(SANS_BOLD, 13), fill=MIDGREY)
    tail = "No. 328  •  ONE PAGE, ONE DAY"
    d.text((PAGE_W - EDGE - d.textlength(tail, font=load(SANS, 13)), 27),
           tail, font=load(SANS, 13), fill=MIDGREY)

    # Masthead.
    name = "THE WORLD TODAY"
    name_face = load(SERIF_BOLD, 70)
    d.text(((PAGE_W - d.textlength(name, font=name_face)) / 2, 50),
           name, font=name_face, fill=BLACK)
    d.line([(EDGE, 134), (PAGE_W - EDGE, 134)], fill=BLACK, width=3)

    # Date band.
    d.rectangle([EDGE, 144, PAGE_W - EDGE, 188], fill=BLACK)
    date = "WEDNESDAY, 25 NOVEMBER 2026"
    date_face = load(SANS_BOLD, 29)
    d.text(((PAGE_W - d.textlength(date, font=date_face)) / 2, 152),
           date, font=date_face, fill=(255, 255, 255))
    d.line([(EDGE, 200), (PAGE_W - EDGE, 200)], fill=BLACK, width=2)

    # ---- Lead story, left column, with the generated photograph ----
    lx, ly, lw = EDGE, 214, 596
    d.text((lx, ly), "LEAD STORY", font=load(SANS_BOLD, 14), fill=CRIMSON)
    y = ly + 24
    y = write_lines(d, split_lines(d, "Two tankers hit mines and burn in the Strait of Hormuz",
                                    load(SERIF_BOLD, 33), lw),
                    load(SERIF_BOLD, 33), lx, y)
    y += 6
    y = write_lines(d, split_lines(d,
        "Two oil tankers struck naval mines, exploded and caught fire "
        "in the Strait of Hormuz, Iran's Revolutionary Guards Navy said. "
        "It warned ships to coordinate passage through the strait.",
        load(SANS, 16), lw), load(SANS, 16), lx, y)
    y += 8
    photo = Image.open(LEAD_PHOTO).convert("RGB")
    pw, ph = lw, 132
    # Centre-crop the wide photograph to the slot's aspect ratio.
    scale = max(pw / photo.width, ph / photo.height)
    resized = photo.resize((int(photo.width * scale) + 1,
                            int(photo.height * scale) + 1))
    left = (resized.width - pw) // 2
    top = (resized.height - ph) // 2
    page.paste(resized.crop((left, top, left + pw, top + ph)), (lx, y))
    d.rectangle([lx, y, lx + pw, y + ph], outline=LINECOL, width=1)
    y += ph + 6
    d.text((lx, y), "Burning tankers in the Strait of Hormuz. (Illustration)",
           font=load(SANS, 12), fill=MIDGREY)
    lead_bottom = y + 18

    # ---- Right of the lead: the Houthi refinery claim ----
    rx = lx + lw + 16
    rw = PAGE_W - EDGE - rx
    story_box(d, rx, ly, rw, lead_bottom - ly,
              "YEMEN  •  SAUDI ARABIA",
              "Houthis say they hit Saudi refinery at Ras Tanura",
              "Yemen's Houthis said they attacked Saudi Arabia's Ras "
              "Tanura oil refinery, in an announcement on Wednesday. "
              "Ras Tanura is one of the world's largest oil refineries.",
              title_size=24, body_size=15)

    # ---- Middle row: refineries, markets, Pacific pact ----
    row_y, row_h = lead_bottom + 12, 176
    col_w = (PAGE_W - 2 * EDGE - 2 * 14) // 3
    x0 = EDGE
    story_box(d, x0, row_y, col_w, row_h, "UKRAINE  •  RUSSIA",
              "Drones set two Rosneft refineries ablaze",
              "Ukrainian drones hit the Syzran and Kuibyshev refineries "
              "in Russia's Samara region overnight; both were ablaze "
              "and one person was killed.")
    story_box(d, x0 + col_w + 14, row_y, col_w, row_h, "MARKETS",
              "Asian shares tumble as AI sell-off spreads",
              "South Korea's KOSPI fell 6.16%, Japan's Nikkei 2.78% and "
              "Taiwan's Taiex 4.8%. The Dow closed above 50,000 for the "
              "first time on Tuesday.")
    story_box(d, x0 + 2 * (col_w + 14), row_y, col_w, row_h,
              "AUSTRALIA  •  PACIFIC",
              "Australia signs security pact with Solomons",
              "Australia and Solomon Islands signed a security treaty in "
              "Canberra that precludes a foreign military base in the "
              "Solomon Islands.")

    # ---- Bottom row: space, Sudan, Colombia ----
    row2_y, row2_h = row_y + row_h + 12, 160
    story_box(d, x0, row2_y, col_w, row2_h, "SPACE  •  CHINA",
              "Shenzhou-24 docks with Tiangong",
              "China's Shenzhou-24 docked with the Tiangong space "
              "station, carrying Pakistan's first astronaut.")
    story_box(d, x0 + col_w + 14, row2_y, col_w, row2_h, "SUDAN",
              "RSF drone strikes kill 19 civilians",
              "Drone strikes by the Rapid Support Forces killed 19 "
              "civilians, reports said on Wednesday.")
    story_box(d, x0 + 2 * (col_w + 14), row2_y, col_w, row2_h, "COLOMBIA",
              "All hostages freed in Cartagena siege",
              "Security forces freed every hostage in a supermarket "
              "siege in Cartagena; one captor was killed.")

    # ---- "Also today" strip ----
    ay = row2_y + row2_h + 12
    strip_h = 56
    d.rectangle([EDGE, ay, PAGE_W - EDGE, ay + strip_h], fill=BLACK)
    strip_face = load(SANS_BOLD, 15)
    strip_lines = split_lines(
        d, "ALSO TODAY:  Pope Leo XIV on the COP31 failure  •  Israel kills "
        "Hamas colonel Mohammad Abuelouf in Gaza  •  Senegal restored as "
        "Africa Cup of Nations champions  •  Eurozone inflation rises to 4.0%.",
        strip_face, PAGE_W - 2 * EDGE - 28)
    if len(strip_lines) > 2:
        raise SystemExit(f"also-today strip needs {len(strip_lines)} lines")
    write_lines(d, strip_lines, strip_face, EDGE + 14, ay + 10,
                colour=(255, 255, 255))

    # Footer.
    foot = "Sources: Reuters  •  AP  •  BBC  •  Seoul Economic Daily"
    foot_face = load(SANS, 13)
    d.text(((PAGE_W - d.textlength(foot, font=foot_face)) / 2, ay + strip_h + 10),
           foot, font=foot_face, fill=MIDGREY)

    page.save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT} ({os.path.getsize(OUT)} bytes)")


if __name__ == "__main__":
    main()
