
import io
from datetime import datetime
from zoneinfo import ZoneInfo
import segno
from PIL import Image
import streamlit as st

APP_VERSION = "v2.0"
APP_BUILD_TIME = datetime.now(ZoneInfo("Europe/Rome")).strftime("%d/%m/%Y %H:%M")

st.set_page_config(page_title="Generatore QR con Segno", layout="wide")

# Version label
st.markdown(
    f"""<div style='position:absolute; top:12px; right:16px; font-size:13px; color:#6b7280;'>
    <strong>{APP_VERSION}</strong> – {APP_BUILD_TIME}
    </div>""", unsafe_allow_html=True
)

st.title("🌀 Generatore di QR Code (Segno)")
st.caption("Crea QR code vettoriali (SVG) o raster (PNG) con o senza logo.")

def generate_qr_segno(data, fill_color, back_color, scale, border, logo_file=None, fmt="PNG"):
    qr = segno.make(data, error="h")
    buf = io.BytesIO()

    if fmt == "SVG":
        qr.save(buf, kind="svg", scale=scale, border=border, dark=fill_color, light=back_color)
        return buf.getvalue(), "image/svg+xml"

    # Per PNG, generiamo l'immagine e aggiungiamo il logo se presente
    qr.save(buf, kind="png", scale=scale, border=border, dark=fill_color, light=back_color)
    buf.seek(0)
    img = Image.open(buf).convert("RGBA")

    if logo_file is not None:
        logo = Image.open(logo_file).convert("RGBA")
        # Ridimensiona logo (circa 20-25% del QR)
        qr_w, qr_h = img.size
        logo_size = int(min(qr_w, qr_h) * 0.25)
        logo.thumbnail((logo_size, logo_size))
        pos = ((qr_w - logo.width) // 2, (qr_h - logo.height) // 2)
        # Incolla logo sopra QR
        img.alpha_composite(logo, dest=pos)

    out_buf = io.BytesIO()
    img.save(out_buf, format="PNG")
    return out_buf.getvalue(), "image/png"

# ---- UI ----
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

    st.subheader("④ Logo (solo per PNG)")
    logo_file = st.file_uploader("Carica logo (PNG/JPG)", type=["png", "jpg", "jpeg"])

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
                fmt=fmt
            )

            if fmt == "PNG":
                st.image(result, caption="Anteprima QR Code", use_container_width=True)
            else:
                st.image("data:image/svg+xml;base64," + result.decode("utf-8").encode("base64").decode(), caption="Anteprima SVG")

            file_name = f"qrcode_{fmt.lower()}.{fmt.lower()}"
            st.download_button(f"💾 Scarica {fmt}", data=result, file_name=file_name, mime=mime)
    else:
        st.info("👈 Inserisci i dati e premi 'Genera QR Code'.")

# ---- Style ----
st.markdown(
    """<style>
    .stButton>button { background-color:#3CBFAE; color:white; font-weight:600; border-radius:10px; padding:10px 20px; }
    .stButton>button:hover { background-color:#2CA18A; transition:.2s; }
    </style>""", unsafe_allow_html=True
)
