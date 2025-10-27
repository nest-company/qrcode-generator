
import io
import qrcode
from PIL import Image
import streamlit as st

st.set_page_config(page_title="Generatore di QR Code con Logo", layout="wide")

def generate_qr_with_logo(qr_url, logo_img=None):
    """Genera un QR code con logo centrale opzionale."""
    qr = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    if logo_img:
        qr_width, qr_height = img.size
        logo_size = min(qr_width, qr_height) // 4
        logo_img.thumbnail((logo_size, logo_size))

        # Centra il logo
        pos = ((qr_width - logo_img.size[0]) // 2, (qr_height - logo_img.size[1]) // 2)
        img.paste(logo_img, pos, logo_img if logo_img.mode == "RGBA" else None)

    return img

# ---- Interfaccia Streamlit ----
st.title("🌀 Generatore di QR Code con Logo")
st.write("Crea un QR code personalizzato con il tuo logo centrale.")

# Colonne per layout
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("① Inserisci i dati")
    qr_url = st.text_input("🔗 URL o testo da codificare:", placeholder="https://tuosito.com")

    st.subheader("② Carica un logo (opzionale)")
    logo_file = st.file_uploader("Carica un file immagine", type=["png", "jpg", "jpeg"])

    st.subheader("③ Genera il QR Code")
    generate_btn = st.button("🚀 Genera QR Code")

with col2:
    st.subheader("Anteprima QR Code")
    if generate_btn:
        if not qr_url:
            st.warning("⚠️ Inserisci un URL valido!")
        else:
            logo = Image.open(logo_file).convert("RGBA") if logo_file else None
            qr_img = generate_qr_with_logo(qr_url, logo)

            st.image(qr_img, caption="QR Code generato", use_container_width=True)

            # Pulsante per download
            buf = io.BytesIO()
            qr_img.save(buf, format="PNG")
            st.download_button(
                label="💾 Scarica QR Code",
                data=buf.getvalue(),
                file_name="qrcode.png",
                mime="image/png"
            )
    else:
        st.info("👈 Inserisci i dati e premi 'Genera QR Code' per iniziare.")

# ---- Stile personalizzato ----
st.markdown(
    """
    <style>
    .stButton>button {
        background-color: #3CBFAE;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 10px 25px;
    }
    .stButton>button:hover {
        background-color: #2CA18A;
        transition: 0.3s;
    }
    </style>
    """, unsafe_allow_html=True
)
