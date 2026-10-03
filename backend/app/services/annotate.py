from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

COLORS = {
    "open_manhole": (220, 38, 38), "pothole": (234, 88, 12),
    "garbage_dump": (234, 179, 8), "damaged_lights": (37, 99, 235)
}

def annotate(image: Image.Image, detections: list[dict]) -> bytes:
    output = image.convert("RGB").copy()
    draw = ImageDraw.Draw(output)
    width, height = output.size
    font = ImageFont.load_default()
    for d in detections:
        x1, y1, x2, y2 = d["bbox"]
        box = (x1 * width, y1 * height, x2 * width, y2 * height)
        color = COLORS.get(d["category"], (22, 163, 74))
        draw.rectangle(box, outline=color, width=max(3, width // 250))
        label = f'{d["category"]} {d["confidence"]:.2f}'
        left, top, right, bottom = draw.textbbox((box[0], box[1]), label, font=font)
        draw.rectangle((left, top, right + 5, bottom + 3), fill=color)
        draw.text((left + 2, top + 1), label, fill="white", font=font)
    buffer = BytesIO()
    output.save(buffer, format="JPEG", quality=88)
    return buffer.getvalue()
