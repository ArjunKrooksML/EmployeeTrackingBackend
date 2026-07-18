import io, asyncio
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import services.storage as storage

LOGO_PATH = Path(__file__).resolve().parent.parent / "utils" / "svaas.png"

MM_TO_PX = 300 / 25.4
CARD_W = round(54 * MM_TO_PX)
CARD_H = round(85 * MM_TO_PX)

# sampled directly from utils/svaas.png so the card always matches the logo exactly
BRAND_BLUE = (66, 115, 185)
BRAND_MAROON = (132, 20, 28)

_template_cache = None


def _diagonal_gradient(w: int, h: int, c1: tuple, c2: tuple, saturate_at: float = 0.42, angle_deg: float = 18) -> Image.Image:
    diag = int((w ** 2 + h ** 2) ** 0.5) + 40
    col = Image.new("RGB", (1, diag))
    for y in range(diag):
        t = min(1.0, (y / (diag - 1)) / saturate_at)
        col.putpixel((0, y), (
            round(c1[0] + (c2[0] - c1[0]) * t),
            round(c1[1] + (c2[1] - c1[1]) * t),
            round(c1[2] + (c2[2] - c1[2]) * t),
        ))
    grad = col.resize((diag, diag))
    grad = grad.rotate(angle_deg, resample=Image.BICUBIC)
    gw, gh = grad.size
    x0, y0 = (gw - w) // 2, (gh - h) // 2
    return grad.crop((x0, y0, x0 + w, y0 + h))


def _get_template() -> Image.Image:
    global _template_cache
    if _template_cache is None:
        _template_cache = _diagonal_gradient(CARD_W, CARD_H, BRAND_BLUE, BRAND_MAROON)
    return _template_cache


def _font(size: int):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _circle_crop(img: Image.Image, size: int) -> Image.Image:
    img = ImageOps.exif_transpose(img.convert("RGB"))
    img = ImageOps.fit(img, (size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    out = Image.new("RGBA", (size, size))
    out.paste(img, (0, 0), mask)
    return out


def _initials_avatar(name: str, size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((0, 0, size, size), fill=BRAND_BLUE)
    letter = (name or "?").strip()[:1].upper()
    f = _font(size // 2)
    bbox = d.textbbox((0, 0), letter, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((size - tw) / 2 - bbox[0], (size - th) / 2 - bbox[1]), letter, font=f, fill="white")
    return img


def _centered(draw: ImageDraw.ImageDraw, text: str, font, y: int, fill="white") -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text(((CARD_W - w) / 2 - bbox[0], y), text, font=font, fill=fill)
    return y + (bbox[3] - bbox[1]) + 16


def _build_sync(emp) -> bytes:
    base = _get_template().copy().convert("RGBA")

    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo = ImageOps.contain(logo, (130, 130))
    lx = (CARD_W - logo.width) // 2
    ly = 40
    base.alpha_composite(logo, (lx, ly))

    photo_size = 260
    photo_img = None
    if emp.profile_pic_path:
        try:
            raw = storage.download(emp.profile_pic_path)
            photo_img = Image.open(io.BytesIO(raw))
        except Exception:
            photo_img = None
    circle = _circle_crop(photo_img, photo_size) if photo_img else _initials_avatar(emp.employee_name, photo_size)

    px = (CARD_W - photo_size) // 2
    py = ly + logo.height + 40
    ring = photo_size + 16
    ImageDraw.Draw(base).ellipse((px - 8, py - 8, px - 8 + ring, py - 8 + ring), fill="white")
    base.alpha_composite(circle, (px, py))

    panel_top = py + photo_size + 40
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle((0, panel_top, CARD_W, CARD_H + 50), radius=40, fill=BRAND_MAROON + (255,))

    text_y = panel_top + 36
    text_y = _centered(draw, emp.employee_name, _font(40), text_y)
    text_y = _centered(draw, (emp.role or "employee").upper(), _font(24), text_y, fill=(230, 220, 220))
    text_y += 18
    text_y = _centered(draw, emp.email, _font(22), text_y)
    if emp.year_joined:
        text_y = _centered(draw, f"Joined {emp.year_joined}", _font(22), text_y)
    text_y = _centered(draw, f"Employee ID: {emp.employee_id}", _font(22), text_y)

    footer_font = _font(18)
    footer = "SVAAS Inframax Solutions OPC Pvt Ltd"
    fbbox = draw.textbbox((0, 0), footer, font=footer_font)
    fw = fbbox[2] - fbbox[0]
    draw.text(((CARD_W - fw) / 2, CARD_H - 44), footer, font=footer_font, fill="white")

    out = io.BytesIO()
    base.convert("RGB").save(out, format="PNG")
    return out.getvalue()


async def build_card(emp) -> bytes:
    return await asyncio.to_thread(_build_sync, emp)
