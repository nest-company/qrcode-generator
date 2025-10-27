
import io
import math
import qrcode
from PIL import Image, ImageDraw
import streamlit as st

st.set_page_config(page_title="Generatore di QR Code con Logo", layout="wide")

def add_center_clear_zone(base_img: Image.Image, box: tuple, radius: int = 12, circular: bool = False) -> None:
    """Disegna una zona bianca di rispetto (quiet zone) al centro del QR, dietro al logo.
    Modifica l'immagine in place.
    - box: (x0, y0, x1, y1)
    - radius: raggi degli angoli se rettangolare
    - circular: se True disegna un cerchio invece del rettangolo con angoli arrotondati
    """
    draw = ImageDraw.Draw(base_img)
    if circular:
        # Cerchio inscritto nel box
        draw.ellipse(box, fill="white")
    else:
        x0, y0, x1, y1 = box
        # Rettangolo arrotondato (rounded rectangle) - Pillow 9+ supporta rounded_rectangle
        try:
            draw.rounded_rectangle(box, radius=radius, fill="white")
        except AttributeError:
            # Fallback: rettangolo normale
            draw.rectangle(box, fill="white")

def generate_qr_with_logo(qr_data: str, logo_img: Image.Image | None = None, *, 
                          version: int | None = None, box_size: int = 10, border: int = 4,
                          logo_scale: float = 0.25, padding_ratio: float = 0.18,
                          rounded_radius: int = 14, circular_clear: bool = False) -> Image.Image:
    """Genera QR con logo e zona centrale di rispetto opzionale.
    - logo_scale: frazione della dimensione min(qr_width, qr_height) (0 < s < 1)
    - padding_ratio: padding bianco attorno al logo come frazione della dimensione del logo
    """
    qr = qrcode.QRCode(
        version=version,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

    if logo_img is None:
        return img.convert("RGB")

    # Prepara il logo
    qr_w, qr_h = img.size
    target = int(min(qr_w, qr_h) * logo_scale)
    # mantieni proporzioni
    logo_img = logo_img.convert("RGBA")
    logo_img.thumbnail((target, target), Image.LANCZOS)
    lw, lh = logo_img.size

    # Calcola il box della zona di rispetto con padding
    pad = int(max(lw, lh) * padding_ratio)
    x0 = (qr_w - lw) // 2 - pad
    y0 = (qr_h - lh) // 2 - pad
    x1 = (qr_w + lw) // 2 + pad
    y1 = (qr_h + lh) // 2 + pad
    # Clampa ai bordi
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(qr_w, x1), min(qr_h, y1)

    # Disegna la zona bianca sotto il logo (quiet zone)
    add_center_clear_zone(img, (x0, y0, x1, y1), radius=rounded_radius, circular=circular_clear)

    # Incolla il logo centrato sopra la zona bianca
    pos = ((qr_w - lw) // 2, (qr_h - lh) // 2)
    img.alpha_composite(logo_img, dest=pos)
    return img.convert("RGB")

# ---- UI ----
st.title("🌀 Generatore di QR Code con Logo (con zona di rispetto)")

left, right = st.columns([1, 1])

with left:
    st.subheader("① Dati")
    qr_text = st.text_input("🔗 URL o testo:", placeholder="https://tuosito.com")

    st.subheader("② Logo")
    logo_file = st.file_uploader("Carica logo (PNG/JPG)", type=["png", "jpg", "jpeg"])

    st.subheader("③ Impostazioni QR")
    colA, colB = st.columns(2)
    with colA:
        box_size = st.slider("Dimensione modulo (box_size)", 6, 16, 10)
        border = st.slider("Bordo esterno (quiet zone)", 2, 8, 4)
    with colB:
        version = st.selectbox("Versione (None = auto)", [None] + list(range(1, 20)), index=0)
        logo_scale = st.slider("Scala logo vs QR", 0.10, 0.40, 0.25, step=0.01)

    st.subheader("④ Zona di rispetto sotto il logo")
    padding_ratio = st.slider("Padding attorno al logo", 0.05, 0.40, 0.18, step=0.01)
    rounded_radius = st.slider("Raggio angoli (se rettangolo)", 0, 30, 14)
    circular_clear = st.checkbox("Usa zona di rispetto circolare", value=False)

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
                qr_text, logo, version=version, box_size=box_size, border=border,
                logo_scale=logo_scale, padding_ratio=padding_ratio,
                rounded_radius=rounded_radius, circular_clear=circular_clear
            )
            st.image(img, caption="QR Code generato", use_container_width=True)

            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.download_button("💾 Scarica PNG", buf.getvalue(), file_name="qrcode.png", mime="image/png")
    else:
        st.info("👈 Inserisci i dati e premi "Genera QR Code".")

# ---- Stile ----
st.markdown(
    """
    <style>
    .stButton>button { background-color:#3CBFAE; color:white; font-weight:600; border-radius:10px; padding:10px 20px; }
    .stButton>button:hover { background-color:#2CA18A; transition:.2s; }
    </style>
    """, unsafe_allow_html=True
)
