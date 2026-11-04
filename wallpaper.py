"""Заставка-календарь года для экрана блокировки iPhone

Рисует 12 месяцев точками: прошедшие дни светлые, сегодня оранжевый,
будущие тёмные. Внизу сколько дней осталось до конца года и процент

Запуск:
    python wallpaper.py                      # сегодня по Сан-Паулу -> wallpaper.png
    python wallpaper.py --date 2026-11-01    # любая дата
    python wallpaper.py --model iphone_16_pro --out my.png
"""

import argparse
import calendar
import datetime as dt
import os
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(HERE, "fonts", "Inter-Medium.otf")

# Разрешения экранов, px
MODELS = {
    "iphone_16_pro_max": (1320, 2868),
    "iphone_16_pro": (1206, 2622),
    "iphone_16_plus": (1290, 2796),
    "iphone_16": (1179, 2556),
    "iphone_15_pro_max": (1290, 2796),
    "iphone_15_pro": (1179, 2556),
    "iphone_15": (1179, 2556),
    "iphone_14": (1170, 2532),
    "iphone_13": (1170, 2532),
}

MONTHS_RU = ["Янв", "Фев", "Март", "Апр", "Май", "Июнь",
             "Июль", "Авг", "Сен", "Окт", "Нояб", "Дек"]

# Цвета сняты с прежней заставки
BG = (0, 0, 0)
PAST = (220, 220, 220)
FUTURE = (39, 39, 39)
TODAY = (233, 128, 67)
LABEL = (175, 175, 175)
FOOTER_MAIN = (233, 128, 67)
FOOTER_SUB = (121, 121, 121)

# Раскладка в пикселях для 1320x2868, для других экранов масштабируется
BASE_W, BASE_H = 1320, 2868
DOT = 21            # диаметр точки
STEP_X = 37         # шаг точек по горизонтали
STEP_Y = 37.6       # шаг недель по вертикали
BLOCK_X = 336       # шаг между колонками месяцев
BLOCK_Y = 355       # шаг между рядами месяцев
FIRST_ROW_Y = 963   # центр первой строки точек января
LABEL_DX = -21      # подпись месяца левее центра первой точки
LABEL_DY = -47      # базовая линия подписи выше центра первой строки
LABEL_SIZE = 33
FOOTER_BASELINE = 2571
FOOTER_SIZE = 37
FOOTER_GAP = 61

SS = 3  # сглаживание: рисуем в 3 раза крупнее и уменьшаем


def days_ru(n: int) -> str:
    return f"{n} дн. осталось"


def render(today: dt.date, model: str = "iphone_16_pro_max") -> Image.Image:
    W, H = MODELS.get(model, MODELS["iphone_16_pro_max"])
    sx, sy = W / BASE_W, H / BASE_H
    k = SS

    img = Image.new("RGB", (W * k, H * k), BG)
    d = ImageDraw.Draw(img)
    label_font = ImageFont.truetype(FONT_PATH, round(LABEL_SIZE * sx * k))
    footer_font = ImageFont.truetype(FONT_PATH, round(FOOTER_SIZE * sx * k))

    year = today.year
    grid_w = 2 * BLOCK_X + 6 * STEP_X
    x0 = (BASE_W - grid_w) / 2  # центр первой точки января, сетка по центру
    r = DOT / 2

    for m in range(1, 13):
        col, row = (m - 1) % 3, (m - 1) // 3
        bx = x0 + col * BLOCK_X
        by = FIRST_ROW_Y + row * BLOCK_Y

        d.text(((bx + LABEL_DX) * sx * k, (by + LABEL_DY) * sy * k),
               MONTHS_RU[m - 1], font=label_font, fill=LABEL, anchor="ls")

        first_wd, n_days = calendar.monthrange(year, m)  # 0 = понедельник
        for day in range(1, n_days + 1):
            idx = first_wd + day - 1
            cx = bx + (idx % 7) * STEP_X
            cy = by + (idx // 7) * STEP_Y
            date = dt.date(year, m, day)
            color = PAST if date < today else TODAY if date == today else FUTURE
            box = [(cx - r) * sx * k, (cy - r) * sy * k,
                   (cx + r) * sx * k, (cy + r) * sy * k]
            d.ellipse(box, fill=color)

    days_in_year = 366 if calendar.isleap(year) else 365
    left = days_in_year - today.timetuple().tm_yday
    main_txt = days_ru(left)
    sub_txt = f"{round(left / days_in_year * 100)}%"

    w_main = d.textlength(main_txt, font=footer_font)
    w_sub = d.textlength(sub_txt, font=footer_font)
    gap = FOOTER_GAP * sx * k
    start = (W * k - (w_main + gap + w_sub)) / 2
    base = FOOTER_BASELINE * sy * k
    d.text((start, base), main_txt, font=footer_font, fill=FOOTER_MAIN, anchor="ls")
    d.text((start + w_main + gap, base), sub_txt, font=footer_font, fill=FOOTER_SUB, anchor="ls")

    return img.resize((W, H), Image.LANCZOS)


def today_in(tz: str) -> dt.date:
    return dt.datetime.now(ZoneInfo(tz)).date()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--date", help="ГГГГ-ММ-ДД, по умолчанию сегодня")
    p.add_argument("--tz", default=os.getenv("WALLPAPER_TZ", "America/Sao_Paulo"))
    p.add_argument("--model", default=os.getenv("WALLPAPER_MODEL", "iphone_16_pro_max"))
    p.add_argument("--out", default="wallpaper.png")
    a = p.parse_args()

    day = dt.date.fromisoformat(a.date) if a.date else today_in(a.tz)
    render(day, a.model).save(a.out, optimize=True)
    print(f"{a.out}: {day} ({a.model})")


if __name__ == "__main__":
    main()
