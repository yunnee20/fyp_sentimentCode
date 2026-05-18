from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os
import platform
import subprocess

DPI = 300
WIDTH_IN = 1.97
HEIGHT_IN = 3.94

width = int(WIDTH_IN * DPI)
height = int(HEIGHT_IN * DPI)

scale = width / 215

def S(v):
    return int(v * scale)


def draw_dashed_line(draw, x1, y, x2, dash=6, gap=6):
    x = x1
    while x < x2:
        draw.line((x, y, min(x + S(dash), x2), y), fill=0, width=S(1))
        x += S(dash + gap)

    pattern = [
        1, 2, 1, 3, 2, 1, 4, 1,
        2, 3, 1, 1, 3, 2, 4, 1,
        1, 3, 2, 1, 4, 2, 1, 3,
        1, 2, 2, 4, 1, 3, 1, 2,
        4, 1, 1, 2, 3, 1, 2, 1
    ]

    current_x = x

    while current_x < x + w:
        for i, bar_w in enumerate(pattern):
            bar_w = S(bar_w)

            if i % 2 == 0:
                draw.rectangle(
                    (current_x, y, current_x + bar_w, y + h),
                    fill=0
                )

            current_x += bar_w

            if current_x >= x + w:
                break

def generate_receipt(data):
    img = Image.new("L", (width, height), 255)
    draw = ImageDraw.Draw(img)

    # side borders
    border_w = S(3)

    draw.rectangle(
        (0, 0, border_w, height),
        fill=0
    )

    draw.rectangle(
        (width - border_w, 0, width, height),
        fill=0
    )

    padding = S(20)

    font_title = ImageFont.truetype("mat/jbm_extrabold.ttf", S(16))
    font_sub = ImageFont.truetype("mat/jbm_bold.ttf", S(12))
    font_body = ImageFont.truetype("mat/jbm_regular.ttf", S(10))

    y = S(10)

    # top thick line
    draw.line((padding, y, width - padding, y), fill=0, width=S(3))
    y += S(10)

    # title block
    draw.rectangle((padding, y, width - padding, y + S(92)), fill=0)

    draw.text((S(43), y + S(17)), "WHEN AI CLAIMS", font=font_title, fill=255)
    draw.text((S(43), y + S(37)), "TO KNOW US TOO", font=font_title, fill=255)
    draw.text((S(76), y + S(57)), "CLEARLY", font=font_title, fill=255)

    y += S(102)

    # title bottom line
    draw.line((padding, y, width - padding, y), fill=0, width=S(3))
    y += S(12)

    # score
    draw.text(
        (padding, y),
        f"SCORE: {data['score']:.0f}% SUBOPTIMAL",
        font=font_sub,
        fill=0
    )

    y += S(22)
    draw.line((padding, y, width - padding, y), fill=0, width=S(3))
    y += S(10)

    lineheight = S(15)

    draw.text((padding, y), f"Valence: {data['valence']:.0f}", font=font_body, fill=0)
    y += lineheight
    draw.text((padding, y), f"Thinking: {data['thinking']:.3f}", font=font_body, fill=0)
    y += lineheight
    draw.text((padding, y), f"Arousal: {data['arousal']:.2f}", font=font_body, fill=0)
    y += lineheight
    draw.text((padding, y), f"Anxious: {data['anxious']:.3f}", font=font_body, fill=0)

    y += S(22)
    draw_dashed_line(draw, padding, y, width - padding)
    y += S(10)

    draw.text((padding, y), f"Face Score: {data['face']:.1f} %", font=font_body, fill=0)
    y += lineheight
    draw.text((padding, y), f"Voice Score: {data['voice']:.0f} %", font=font_body, fill=0)
    y += lineheight
    draw.text((padding, y), f"Text Score: {data['text']:.0f} %", font=font_body, fill=0)

    y += S(25)
    draw.line((padding, y, width - padding, y), fill=0, width=S(4))
    y += S(12)

    draw.text((padding, y), "Practice Required", font=font_sub, fill=0)

    y += S(20)
    draw_dashed_line(draw, padding, y, width - padding)
    y += S(12)

    # timestamp / ID
    timestamp = datetime.now().strftime("%Y %m %d %H%M%S")
    draw.text((S(30), y-10), f"{timestamp} 1201", font=font_sub, fill=0)
    draw.text((S(25), y+30), "Thank You for participating", font=font_body, fill=0)
    y += S(30)
    draw_dashed_line(draw, padding, y, width - padding)

    y += S(10)

    draw.text((S(20), y+35), "by Yunnee Tey", font=font_body, fill=0)
    # draw.text((S(40), y+50), "portfolio", font=font_body, fill=100)

    barcode_img = Image.open("mat/qr.png").convert("L")
    barcode_img = barcode_img.resize((S(50), S(50)))
    img.paste(barcode_img, (width - 150- S(20), y-10))

    return img


def save_and_print_receipt(data):
    os.makedirs("receipt", exist_ok=True)

    img = generate_receipt(data)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"receipt_{timestamp}.pdf"

    img_rgb = img.convert("RGB")
    img_rgb.save(filename, resolution=DPI)

    system = platform.system()

    if system == "Windows":
        os.startfile(filename, "print")

    else:
        print("Unsupported operating system")

    print(f"Printed: {filename}")


