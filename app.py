import streamlit as st
import pandas as pd
from urllib.parse import quote_plus

st.set_page_config(page_title="Buenas Raices", page_icon="🌱", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #121212; color: #EAEAEA; }
    h1, h2, h3, label { color: #EAEAEA !important; }
    div[data-testid="stForm"] { background-color: #1E1E1E; border-radius: 15px; padding: 20px; border: 1px solid #2E7D32; }
</style>
""", unsafe_allow_html=True)

st.title("Buenas Raíces 🌱")
st.subheader("PRODUCTOS ORGÁNICOS - Sistema de Reparto")

if 'pedidos' not in st.session_state:
    st.session_state.pedidos = []

with st.form("pedido_form"):
    cliente = st.text_input("Cliente*")
    direccion = st.text_input("Dirección completa*")
    col1, col2 = st.columns(2)
    with col1:
        zona = st.selectbox("Zona", ["CABA - Norte", "CABA - Sur", "Zona Oeste", "Zona Norte"])
        monto = st.number_input("Monto ($)", min_value=0, step=500)
    with col2:
        repartidor = st.selectbox("Repartidor", ["Repartidor 1", "Repartidor 2", "Repartidor 3"])
        nota = st.text_area("Nota")
    enviado = st.form_submit_button("✅ Agregar Pedido")
    if enviado and cliente and direccion:
        st.session_state.pedidos.append({"Cliente": cliente, "Dirección": direccion, "Zona": zona, "Repartidor": repartidor, "Monto": monto, "Nota": nota})
        st.success("Agregado!")

if st.session_state.pedidos:
    df = pd.DataFrame(st.session_state.pedidos)
    st.dataframe(df, use_container_width=True)
    total = df["Monto"].sum()
    st.success(f"📦 Total Pedidos: {len(df)} | 💰 Total a Cobrar: ${total:,.0f}")

    st.markdown("### 🗺️ Recorrido para Maps")
    base_url = "https://www.google.com/maps/dir/"
    direcciones_url = "/".join([quote_plus(d) for d in df["Dirección"].tolist()])
    link_maps = base_url + direcciones_url
    st.link_button("ABRIR RECORRIDO EN GOOGLE MAPS", link_maps)
    st.code(link_maps)

    if st.button("Borrar todo"):
        st.session_state.pedidos = []
        st.rerun()
