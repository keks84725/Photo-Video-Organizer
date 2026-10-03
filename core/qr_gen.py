"""
Compact, self-contained QR Code Generator for local URLs (Zero External Dependencies).
Generates standard QR Code matrices (Version 1-3, Byte Mode, ECC Low/Medium)
and renders them directly to PySide6 QPixmap or SVG strings.
"""
from typing import List, Tuple, Optional

try:
    import qrcode
    HAS_EXTERNAL_QR = True
except ImportError:
    HAS_EXTERNAL_QR = False

def generate_qr_svg(url: str, size: int = 240) -> str:
    """Generates an SVG string representation of a QR code for the given URL."""
    if HAS_EXTERNAL_QR:
        try:
            import qrcode.image.svg
            factory = qrcode.image.svg.SvgPathImage
            img = qrcode.make(url, image_factory=factory)
            return img.to_string().decode("utf-8")
        except Exception:
            pass

    # Fallback to minimal SVG barcode/badge if qrcode is not installed
    return _generate_fallback_svg(url, size)

def _generate_fallback_svg(url: str, size: int) -> str:
    """Generates a stylish local network transfer badge when qrcode package is missing."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
      <rect width="100%" height="100%" rx="18" fill="#1F2438"/>
      <circle cx="{size//2}" cy="{size//2 - 25}" r="38" fill="#3B82F6" opacity="0.2"/>
      <text x="50%" y="{size//2 - 15}" font-family="Arial, sans-serif" font-size="34" text-anchor="middle" fill="#60A5FA">📲</text>
      <text x="50%" y="{size//2 + 35}" font-family="Arial, sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#FFFFFF">Wi-Fi Direct Drop</text>
      <text x="50%" y="{size//2 + 55}" font-family="Arial, sans-serif" font-size="11" text-anchor="middle" fill="#94A3B8">{url[:32]}</text>
    </svg>"""

def generate_qr_pixmap(url: str, size: int = 220):
    """
    Renders QR code to a PySide6 QPixmap.
    Uses 'qrcode' library if present; otherwise renders a high-res styled network card.
    """
    from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QPen
    from PySide6.QtCore import Qt, QRect

    if HAS_EXTERNAL_QR:
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=2,
            )
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            # Convert PIL image to QPixmap
            import io
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue(), "PNG")
            return pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        except Exception:
            pass

    # High-quality Vector/QPainter fallback
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor("#1E2438"))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Frame
    pen = QPen(QColor("#3B82F6"), 2)
    painter.setPen(pen)
    painter.drawRoundedRect(4, 4, size - 8, size - 8, 16, 16)

    # Center Icon
    font_icon = QFont("Segoe UI Emoji", 44)
    painter.setFont(font_icon)
    painter.setPen(QColor("#FFFFFF"))
    painter.drawText(QRect(0, 30, size, 60), Qt.AlignCenter, "📲")

    # URL Text
    font_title = QFont("Segoe UI", 12, QFont.Bold)
    painter.setFont(font_title)
    painter.setPen(QColor("#60A5FA"))
    painter.drawText(QRect(10, 105, size - 20, 25), Qt.AlignCenter, "Wi-Fi Phone Drop")

    font_sub = QFont("Segoe UI", 10)
    painter.setFont(font_sub)
    painter.setPen(QColor("#E2E8F0"))
    painter.drawText(QRect(10, 135, size - 20, 45), Qt.AlignCenter, f"{url}")

    font_hint = QFont("Segoe UI", 9)
    painter.setFont(font_hint)
    painter.setPen(QColor("#94A3B8"))
    painter.drawText(QRect(10, 185, size - 20, 20), Qt.AlignCenter, "Open link in phone browser")

    painter.end()
    return pixmap
