from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os
import platform
import subprocess

DPI = 300
WIDTH_IN = 1.97
HEIGHT_IN = 3.94

width = int(WIDTH_IN * DPI)      # 591
height = int(HEIGHT_IN * DPI)    # 1182

scale = width / 215  # scale from your original design

def S(v):
    return int(v * scale)

def generate_receipt(data):
    img = Image.new("L", (width, height), 255)
    draw = ImageDraw.Draw(img)

    padding = S(20)
    container = S(181)

    font_title = ImageFont.truetype("mat/jbm_extrabold.ttf", S(16))
    font_sub = ImageFont.truetype("mat/jbm_bold.ttf", S(12))
    font_body = ImageFont.truetype("mat/jbm_regular.ttf", S(10))

    y = S(20)

    draw.rectangle((padding, y, width-padding, y+S(96)), fill=0)

    draw.text((S(35), y+S(15)), "WHEN AI CLAIMS", font=font_title, fill=255)
    draw.text((S(35), y+S(35)), "TO KNOW US TOO", font=font_title, fill=255)
    draw.text((S(70), y+S(55)), "CLEARLY", font=font_title, fill=255)

    y += S(105)

    draw.line((padding, y, container+S(10), y), fill=0, width=S(2))
    y += S(10)

    draw.text((S(20), y), f"SCORE: {data['score']}%  SUBOPTIMAL", font=font_sub, fill=0)

    y += S(30)
    draw.line((padding, y, container+S(10), y), fill=0, width=S(2))
    y += S(10)

    lineheight = S(18)

    draw.text((S(20), y), f"Valence: {data['valence']}", font=font_body, fill=0)
    y += lineheight
    draw.text((S(20), y), f"Thinking: {data['thinking']}", font=font_body, fill=0)
    y += lineheight
    draw.text((S(20), y), f"Arousal: {data['arousal']}", font=font_body, fill=0)
    y += lineheight
    draw.text((S(20), y), f"Anxious: {data['anxious']}", font=font_body, fill=0)

    y += S(25)
    draw.line((padding, y, container+S(10), y), fill=0)

    y += S(10)

    draw.text((S(20), y), f"Face Score: {data['face']}%", font=font_body, fill=0)
    y += lineheight
    draw.text((S(20), y), f"Voice Score: {data['voice']}%", font=font_body, fill=0)
    y += lineheight
    draw.text((S(20), y), f"Text Score: {data['text']}%", font=font_body, fill=0)

    y += S(25)
    draw.line((padding, y, container+S(10), y), fill=0, width=S(3))

    y += S(10)
    draw.text((S(20), y), "Practice Required", font=font_sub, fill=0)

    y += S(25)
    draw.line((padding, y, container+S(10), y), fill=0)

    y += S(10)
    draw.text((S(30), y), "thank you for visiting...", font=font_body, fill=100)

    y += S(20)

    barcode_img = Image.open("mat/barcode.png").convert("L")
    barcode_img = barcode_img.resize((S(150), S(50)))
    img.paste(barcode_img, (S(30), y))

    y += S(55)

    timestamp = datetime.now().strftime("%Y %m %d %H%M%S")
    draw.text((S(35), y), timestamp, font=font_body, fill=0)

    return img


def save_and_print_receipt(data):
    img = generate_receipt(data)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"receipt_{timestamp}.pdf"

    img_rgb = img.convert("RGB")
    img_rgb.save(filename, resolution=300)

    system = platform.system()

    if system == "Windows":
        os.startfile(filename, "print")

    elif system == "Darwin":  # macOS
        subprocess.run(["lp", filename])

    elif system == "Linux":
        subprocess.run(["lp", filename])

    else:
        print("Unsupported operating system")

    print(f"Printed: {filename}")
