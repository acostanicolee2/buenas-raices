import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import math

st.set_page_config(page_title="Buenas Raíces - Reparto", layout="wide", page_icon="🌱")

# ESTILO
st.markdown("""
<style>
h1 {color: #2E7D32!important;}
.stButton>button {background-color: #2E7D32; color: white; border-radius: 8px; width: 100%;}
</style>
""", unsafe_allow_html=True)

# LOGO Y TITULO
col1, col2 = st.columns([1,4])
with col1:
    try:
        st.image("logo.png", width=110)
    except:
        st.write("🌱")
with col2:
    st.title("Buenas Raíces")
    st.subheader("PRODUCTOS ORGÁNICOS - Sistema de Reparto")

if 'pedidos' not in st.session_state:
    st.session_state.pedidos = []

# GEOCODIFICADOR
geolocator = Nominatim(user_agent="buenas_raices_v3")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def ordenar_ruta(pedidos_df):
    if pedidos_df.empty or len(pedidos_df) <= 1:
        return pedidos_df
    # Empieza en el primer pedido y busca el más cercano
    sin_visitar = pedidos_df.to_dict('records')
    ruta = [sin_visitar.pop(0)]
    while sin_visitar:
        ultimo = ruta[-1]
        mas_cercano = min(sin_visitar, key=lambda x: calcular_distancia(ultimo['lat'], ultimo['lon'], x['lat'], x['lon']))
        ruta.append(mas_cercano)
        sin_visitar.remove(mas_cercano)
    return pd.DataFrame(ruta)

# FORMULARIO
st.markdown("### 1. Cargar nuevo pedido orgánico")
with st.form("form_pedido"):
    cliente = st.text_input("Cliente*")
    direccion = st.text_input("Dirección completa* Ej: Av. Rivadavia 5000, Flores, CABA")
    c1, c2 = st.columns(2)
    with c1:
        zona = st.selectbox("Zona", ["CABA - Norte", "CABA - Sur", "GBA Oeste", "GBA Norte", "GBA Sur"])
    with c2:
        repartidor = st.selectbox("Repartidor", ["Repartidor 1 - Norte", "Repartidor 2 - Oeste", "Repartidor 3 - Sur"])
    nota = st.text_input("Nota (Ej: Bolsón vegano, sin TACC)")
    submit = st.form_submit_button("🌱 Agregar Pedido")

if submit:
    if not cliente or not direccion:
        st.error("Faltan datos")
    else:
        location = geocode(direccion + ", Buenos Aires, Argentina")
        if location:
            nuevo = {"Cliente": cliente, "Direccion": direccion, "Zona": zona, "Repartidor": repartidor, "Nota": nota, "lat": location.latitude, "lon": location.longitude}
            st.session_state.pedidos.append(nuevo)
            st.success(f"Agregado: {cliente} - {location.latitude:.4f}, {location.longitude:.4f}")
            st.rerun()
        else:
            st.error("No pude encontrar esa dirección. Probá más completa: Calle, altura, barrio, CABA")

# MOSTRAR DATOS
if st.session_state.pedidos:
    df = pd.DataFrame(st.session_state.pedidos)
    st.markdown("### 2. Pedidos de hoy")
    st.dataframe(df[["Cliente","Direccion","Zona","Repartidor"]], use_container_width=True)

    for rep in df["Repartidor"].unique():
        df_rep = df[df["Repartidor"] == rep]
        df_ordenada = ordenar_ruta(df_rep)

        st.markdown(f"#### 🚚 Ruta óptima para: {rep} ({len(df_ordenada)} paradas)")

        # Mapa
        m = folium.Map(location=[df_ordenada.iloc[0]['lat'], df_ordenada.iloc[0]['lon']], zoom_start=12)
        coords_ruta = []
        for i, row in df_ordenada.iterrows():
            coords_ruta.append([row['lat'], row['lon']])
            folium.Marker([row['lat'], row['lon']], popup=f"{i+1}. {row['Cliente']}<br>{row['Direccion']}", icon=folium.Icon(color="green", icon="leaf")).add_to(m)

        # DIBUJA LA RUTA MÁS CORTA
        if len(coords_ruta) > 1:
            folium.PolyLine(coords_ruta, color="#2E7D32", weight=4, opacity=0.8).add_to(m)

        st_folium(m, width=700, height=400)

        # Botón para WhatsApp
        texto_whatsapp = f"Ruta {rep} - Buenas Raíces:\n"
        for i, row in df_ordenada.iterrows():
            texto_whatsapp += f"{i+1}. {row['Cliente']} - {row['Direccion']} - {row['Nota']}\n"
        texto_whatsapp += "\nMapa: https://www.google.com/maps/dir/" + "/".join([f"{lat},{lon}" for lat, lon in coords_ruta])
        st.code(texto_whatsapp, language="text")
        st.caption("Copiá ese texto y mandaselo por WhatsApp al repartidor. Al tocar el link de Google Maps le abre toda la ruta.")

    if st.button("🔴 Terminar día y borrar todo"):
        st.session_state.pedidos = []
        st.rerun()