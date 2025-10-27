
import io
import base64
from datetime import datetime
from zoneinfo import ZoneInfo
import segno
from PIL import Image, ImageDraw
import streamlit as st

# -------------------- Version Info --------------------
APP_VERSION = "v3.0"
APP_BUILD_TIME = datetime.now(ZoneInfo("Europe/Rome")).strftime("%d/%m/%Y %H:%M")

st.set_page_config(page_title="Generatore QR con Segno", layout="wide")

# Badge versione in alto a destra
st.markdown(
    f"""
    <div style='position:absolute; top:12px; right:16px; font-size:13px; color:#6b7280;'>
        <strong>{APP_VERSION}</strong> – {APP_BUILD_TIME}
    </div>
    """, unsafe_allow_html=True
)

st.title("🌀 Generatore di QR Code (Segno)")
st.caption("Crea QR code vettoriali (SVG) o raster (PNG) con logo e zona di rispetto regolabile.")

# -------------------- Funzione per generare QR --------------------
def add_center_clear_zone(img: Image.Image, box: tuple[int, int, int, int], radius: int = 14):
    draw = ImageDraw.Draw(img)
    try:
        draw.rounded_rectangle(box, radius=radius, fill="white")
    except AttributeError:
        draw.rectangle(box, fill="white")

def generate_qr_segno(data, fill_color, back_color, scale, border, logo_file=None, padding_ratio=0.18, radius=14, fmt="PNG"):
    qr = segno.make(data, error="h")

    # ---- SVG ----
    if fmt == "SVG":
        buf = io.BytesIO()
        qr.save(buf, kind="svg", scale=scale, border=border, dark=fill_color, light=back_color)
        return buf.getvalue(), "image/svg+xml"

    # ---- PNG ----
    buf = io.BytesIO()
    qr.save(buf, kind="png", scale=scale, border=border, dark=fill_color, light=back_color)
    buf.seek(0)
    img = Image.open(buf).convert("RGBA")

    if logo_file:
        logo = Image.open(logo_file).convert("RGBA")
        qr_w, qr_h = img.size
        logo_size = int(min(qr_w, qr_h) * 0.25)
        logo.thumbnail((logo_size, logo_size))

        lw, lh = logo.size
        pos = ((qr_w - lw)//2, (qr_h - lh)//2)

        pad = int(max(lw, lh) * padding_ratio)
        x0, y0 = pos[0]-pad, pos[1]-pad
        x1, y1 = pos[0]+lw+pad, pos[1]+lh+pad
        add_center_clear_zone(img, (x0, y0, x1, y1), radius=radius)

        img.alpha_composite(logo, dest=pos)

    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue(), "image/png"

# -------------------- Interfaccia --------------------
left, right = st.columns([1, 1])

with left:
    st.subheader("① Dati")
    data = st.text_input("🔗 URL o testo da codificare:", placeholder="https://tuosito.com")

    st.subheader("② Colori")
    fill_color = st.color_picker("Colore moduli", "#000000")
    back_color = st.color_picker("Colore sfondo", "#FFFFFF")

    st.subheader("③ Parametri QR")
    scale = st.slider("Scala (dimensione complessiva)", 3, 20, 8)
    border = st.slider("Bordo esterno (quiet zone)", 1, 8, 4)

    st.subheader("④ Logo e zona di rispetto (solo PNG)")
    logo_file = st.file_uploader("Carica logo (PNG/JPG)", type=["png", "jpg", "jpeg"])
    padding_ratio = st.slider("Padding attorno al logo", 0.05, 0.4, 0.18, step=0.01)
    radius = st.slider("Raggio angoli zona bianca", 0, 30, 14)

    st.subheader("⑤ Formato output")
    fmt = st.selectbox("Formato download", ["PNG", "SVG"])

    generate = st.button("🚀 Genera QR Code")

with right:
    st.subheader("Anteprima e Download")
    if generate:
        if not data:
            st.warning("⚠️ Inserisci prima un testo o URL.")
        else:
            result, mime = generate_qr_segno(
                data=data,
                fill_color=fill_color,
                back_color=back_color,
                scale=scale,
                border=border,
                logo_file=logo_file if fmt == "PNG" else None,
                padding_ratio=padding_ratio,
                radius=radius,
                fmt=fmt
            )

            if fmt == "PNG":
                st.image(result, caption="Anteprima QR Code", use_container_width=True)
            else:
                svg_b64 = base64.b64encode(result).decode("utf-8")
                st.markdown(f"<img src='data:image/svg+xml;base64,{svg_b64}' width='300'>", unsafe_allow_html=True)

            file_name = f"qrcode_{fmt.lower()}.{fmt.lower()}"
            st.download_button(f"💾 Scarica {fmt}", data=result, file_name=file_name, mime=mime)
    else:
        st.info("👈 Inserisci i dati e premi 'Genera QR Code'.")

# -------------------- Stile --------------------
st.markdown(
    """
    <style>
    .stButton>button { background-color:#3CBFAE; color:white; font-weight:600; border-radius:10px; padding:10px 20px; }
    .stButton>button:hover { background-color:#2CA18A; transition:.2s; }
    </style>
    """, unsafe_allow_html=True
)
