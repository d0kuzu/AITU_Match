from datetime import datetime
from io import BytesIO
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont
from aiogram.types import BufferedInputFile

from database.models import User


def wrap_text(text: str, day: int, max_width: int, draw: ImageDraw, font: FreeTypeFont) -> list[str]:
    words = text.split()
    lines = [f"День {day}"]
    current_line = ""

    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        test_width = draw.textlength(test_line, font=font)
        if test_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    return lines


def generate_counter_image(text: str, day: int):
    img = Image.open("images/background.PNG").convert("RGB")
    w, h = img.size
    band_h = h // 3
    band_y0 = (h - band_h) // 2

    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("fonts/Montserrat-Regular.ttf", size=80)

    lines = wrap_text(text, day, int(w * 0.9), draw, font)

    line_heights = [draw.textbbox((0, 0), line, font=font)[3] for line in lines]
    total_h = sum(line_heights)
    y = band_y0 + (band_h - total_h) // 2

    mask = Image.new("L", (w, h), 0)
    mdraw = ImageDraw.Draw(mask)
    for line, line_h in zip(lines, line_heights):
        line_width = draw.textlength(line, font=font)
        x = (w - line_width) // 2
        mdraw.text((x, y), line, font=font, fill=255)
        y += line_h

    grad = Image.new("RGB", (w, h))
    gdraw = ImageDraw.Draw(grad)
    sc = (160, 225, 220)
    ec = (30, 70, 120)
    for yy in range(h):
        ratio = yy / (h - 1)
        r = int(sc[0] * (1 - ratio) + ec[0] * ratio)
        g = int(sc[1] * (1 - ratio) + ec[1] * ratio)
        b = int(sc[2] * (1 - ratio) + ec[2] * ratio)
        gdraw.line([(0, yy), (w, yy)], fill=(r, g, b))

    result = Image.composite(grad, img, mask)
    buf = BytesIO()
    result.save(buf, format="PNG")
    buf.seek(0)
    return BufferedInputFile(file=buf.read(), filename="image.png")