#!/usr/bin/env python3
"""
Build 100 Quote Slides & Render 3-Hour Full HD MP4 Video Draft
LIDO AI Meditation Music Factory
"""

import os
import sys
import json
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def get_system_font(font_size=36):
    font_paths = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc"
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, font_size)
            except Exception:
                pass
    return ImageFont.load_default()

def create_base_canvas(img_path, canvas_w=1920, canvas_h=1080):
    original_img = Image.open(img_path).convert("RGBA")
    
    bg_img = original_img.copy()
    bg_w, bg_h = bg_img.size
    bg_aspect = bg_w / bg_h
    canvas_aspect = canvas_w / canvas_h
    
    if bg_aspect > canvas_aspect:
        new_h = canvas_h
        new_w = int(canvas_h * bg_aspect)
    else:
        new_w = canvas_w
        new_h = int(canvas_w / bg_aspect)
        
    bg_img = bg_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    left = (new_w - canvas_w) // 2
    top = (new_h - canvas_h) // 2
    bg_img = bg_img.crop((left, top, left + canvas_w, top + canvas_h))
    
    bg_blurred = bg_img.filter(ImageFilter.GaussianBlur(radius=35))
    
    fg_img = original_img.copy()
    fg_h = canvas_h
    fg_w = int(canvas_h * (original_img.width / original_img.height))
    fg_img = fg_img.resize((fg_w, fg_h), Image.Resampling.LANCZOS)
    
    fg_x = (canvas_w - fg_w) // 2
    base = bg_blurred.copy()
    base.paste(fg_img, (fg_x, 0), fg_img)
    return base

def render_slide(base_canvas, quote_text, index, total, output_path):
    canvas = base_canvas.copy().convert("RGBA")
    draw = ImageDraw.Draw(canvas)
    
    font = get_system_font(38)
    small_font = get_system_font(24)
    header_font = get_system_font(28)
    
    card_w, card_h = 1700, 220
    card_x = (1920 - card_w) // 2
    card_y = 1080 - card_h - 50
    
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rounded_rectangle(
        [(card_x, card_y), (card_x + card_w, card_y + card_h)],
        radius=20,
        fill=(15, 25, 20, 200),
        outline=(212, 175, 55, 180),
        width=2
    )
    
    canvas = Image.alpha_composite(canvas, overlay)
    draw = ImageDraw.Draw(canvas)
    
    header_text = f"🪷 LIDO MEDITATION — HƯ KHÔNG HUYỀN GIÁC ({index}/{total})"
    draw.text((card_x + 30, card_y + 20), header_text, font=header_font, fill=(212, 175, 55, 255))
    
    words = quote_text.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        test_str = " ".join(current_line)
        bbox = font.getbbox(test_str)
        if (bbox[2] - bbox[0]) > (card_w - 60):
            current_line.pop()
            lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
        
    line_y = card_y + 65
    for line in lines[:3]:
        draw.text((card_x + 30, line_y), line, font=font, fill=(255, 255, 255, 255))
        line_y += 45
        
    footer_text = "528Hz • 432Hz • 963Hz Solfeggio Meditation Music"
    draw.text((card_x + card_w - 520, card_y + card_h - 35), footer_text, font=small_font, fill=(180, 200, 190, 220))
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    canvas.convert("RGB").save(output_path, "PNG")

def main():
    quotes_file = "data/quotes_100.json"
    # Construct input image & audio paths dynamically without hardcoded user paths
    target_dir = os.path.expanduser("~/Documents/KenhYTB/hukhonghuyengiac_ny")
    img_path = os.path.join(target_dir, "hukhonghuyengiac.png")
    audio_path = os.path.join(target_dir, "HuKhongHuyenGiac_Master_320kbps.mp3")
    slides_dir = "data/slides"
    
    if not os.path.exists(quotes_file):
        print(f"Error: {quotes_file} not found. Run generate_100_quotes_video.py first.")
        sys.exit(1)
        
    with open(quotes_file, "r", encoding="utf-8") as f:
        quotes = json.load(f)
        
    print(f"Loaded {len(quotes)} quotes.")
    print("Creating 1920x1080 Full HD base canvas...")
    base_canvas = create_base_canvas(img_path)
    
    print("Rendering 100 quote slide images...")
    os.makedirs(slides_dir, exist_ok=True)
    for i, quote in enumerate(quotes, start=1):
        slide_path = os.path.join(slides_dir, f"slide_{i:03d}.png")
        render_slide(base_canvas, quote, i, len(quotes), slide_path)
        if i % 20 == 0 or i == len(quotes):
            print(f"  Rendered {i}/{len(quotes)} slides.")
            
    concat_list_path = "data/slides_concat.txt"
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for i in range(1, len(quotes) + 1):
            slide_abs = os.path.abspath(os.path.join(slides_dir, f"slide_{i:03d}.png"))
            f.write(f"file '{slide_abs}'\n")
            f.write("duration 108\n")
        last_abs = os.path.abspath(os.path.join(slides_dir, f"slide_{len(quotes):03d}.png"))
        f.write(f"file '{last_abs}'\n")
        
    print(f"Generated FFmpeg slide concat file: {concat_list_path}")
    print("Setup completed successfully. Ready for MP4 rendering!")

if __name__ == "__main__":
    main()
