
import io
from typing import Optional, Tuple

import qrcode
from PIL import Image, ImageDraw
import streamlit as st

st.set_page_config(page_title="Generatore di QR Code con Logo", layout="wide")

# -------------------- Core --------------------
def add_center_clear_zone(base_img: Image.Image, box: Tuple[int, int, int, int], *, radius: int = 14, circular: bool = False) -> None:
    """Disegna una zona bianca di rispetto (quiet area) nel QR, sotto il logo.
    Modifica l'immagine in-place.
    - box = (x0, y0, x1, y1)
    - radius = raggio angoli se rettangolo
    - circular = True per un cerchio inscritto nel box
    """
    draw = ImageDraw.Draw(base_img)
    if circular:
        draw.ellipse(box, fill="white")
    else:
        # rounded_rectangle disponibile su Pillow 9+
        try:
            draw.rounded_rectangle(box, radius=radius, fill="white")
        except AttributeError:
            draw.rectangle(box, fill="white")

def generate_qr_with_logo(
    qr_data: str,
    logo_img: Optional[Image.Image] = None,
    *,
    version: Optional[int] = None,
    box_size: int = 10,
    border: int = 4,
    logo_scale: float = 0.25,
    padding_ratio: float = 0.18,
    rounded_radius: int = 14,
    circular_clear: bool = False,
    fill_color: str = "black",
    back_color: str = "white",
) -> Image.Image:
    """Genera QR con logo e zona centrale di rispetto.
    - logo_scale: frazione rispetto al lato minimo del QR (0.1-0.4 è realistico)
    - padding_ratio: padding bianco attorno al logo come frazione del lato logo
    """
    qr = qrcode.QRCode(
        version=version,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGBA")

    if logo_img is None:
        return img.convert("RGB")

    qr_w, qr_h = img.size

    # Prepara logo
    logo = logo_img.convert("RGBA")
    target = int(min(qr_w, qr_h) * logo_scale)
    logo.thumbnail((target, target), Image.LANCZOS)
    lw, lh = logo.size

    # Box della quiet area (con padding)
    pad = int(max(lw, lh) * padding_ratio)
    x0 = (qr_w - lw) // 2 - pad
    y0 = (qr_h - lh) // 2 - pad
    x1 = (qr_w + lw) // 2 + pad
    y1 = (qr_h + lh) // 2 + pad

    # Clamp ai bordi
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(qr_w, x1), min(qr_h, y1)

    # Disegna quiet area
    add_center_clear_zone(img, (x0, y0, x1, y1), radius=rounded_radius, circular=circular_clear)

    # Compositing del logo sopra
    pos = ((qr_w - lw) // 2, (qr_h - lh) // 2)
    img.alpha_composite(logo, dest=pos)

    return img.convert("RGB")

# -------------------- UI --------------------
st.title("🌀 Generatore di QR Code con Logo (con zona di rispetto)")
st.caption("Assicura la leggibilità creando un'area bianca sotto al logo.")

left, right = st.columns([1, 1])

with left:
    st.subheader("① Dati")
    qr_text = st.text_input("🔗 URL o testo:", placeholder="https://tuosito.com")

    st.subheader("② Logo (opzionale)")
    logo_file = st.file_uploader("Carica logo (PNG/JPG)", type=["png", "jpg", "jpeg"])

    st.subheader("③ Parametri QR")
    colA, colB = st.columns(2)
    with colA:
        box_size = st.slider("Dimensione modulo (box_size)", 6, 16, 10)
        border = st.slider("Bordo esterno (quiet zone)", 2, 8, 4)
        version = st.selectbox("Versione (None = auto)", [None] + list(range(1, 20)), index=0)
    with colB:
        logo_scale = st.slider("Scala logo vs QR", 0.10, 0.40, 0.25, step=0.01)
        padding_ratio = st.slider("Padding attorno al logo", 0.05, 0.40, 0.18, step=0.01)
        rounded_radius = st.slider("Raggio angoli clear area", 0, 30, 14)
    circular_clear = st.checkbox("Zona di rispetto circolare", value=False)

    st.subheader("🎨 Colori")
    colC, colD = st.columns(2)
    with colC:
        fill_color = st.color_picker("Colore moduli", "#000000")
    with colD:
        back_color = st.color_picker("Colore sfondo", "#FFFFFF")

    generate = st.button("🚀 Genera QR Code")

with right:
    st.subheader("Anteprima")
    if generate:
        if not qr_text:
            st.warning("⚠️ Inserisci prima URL o testo.")
        else:
            logo = None
            if logo_file:
                try:
                    logo = Image.open(logo_file)
                except Exception as e:
                    st.error(f"Logo non valido: {e}")
            img = generate_qr_with_logo(
                qr_text,
                logo,
                version=version,
                box_size=box_size,
                border=border,
                logo_scale=logo_scale,
                padding_ratio=padding_ratio,
                rounded_radius=rounded_radius,
                circular_clear=circular_clear,
                fill_color=fill_color,
                back_color=back_color,
            )
            st.image(img, caption="QR Code generato", use_container_width=True)

            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.download_button("💾 Scarica PNG", buf.getvalue(), file_name="qrcode.png", mime="image/png")
    else:
        st.info("👈 Inserisci i dati e premi 'Genera QR Code'.")

# -------------------- Style --------------------
st.markdown(
    """
    <style>
    .stButton>button { background-color:#3CBFAE; color:white; font-weight:600; border-radius:10px; padding:10px 20px; }
    .stButton>button:hover { background-color:#2CA18A; transition:.2s; }
    </style>
    """,
    unsafe_allow_html=True,
)
