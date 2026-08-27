import streamlit as st
import pandas as pd
from urllib.parse import quote_plus
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

st.set_page_config(page_title="Buenas Raíces", page_icon="🌱", layout="wide")
st.markdown("""<style>.stApp { background-color: #121212; color: #EAEAEA; } h1, h2, h3 { color: #EAEAEA !important; }</style>""", unsafe_allow_html=True)
st.title("Buenas Raíces 🌱 - Con Buscador de Direcciones")

geolocator = Nominatim(user_agent="buenas_raices_app")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

if 'pedidos' not in st.session_state: st.session_state.pedidos = []
if 'dir_elegida' not in st.session_state: st.session_state.dir_elegida = ""

st.markdown("### 1. Buscar Dirección (como en Google Maps)")
busqueda = st.text_input("Escribí la dirección para buscar opciones", placeholder="Ej: El Chacabuco 4000, Ciudad Evita")

if st.button("🔍 Buscar opciones de dirección"):
    if busqueda:
        with st.spinner("Buscando..."):
            # Buscamos solo en Argentina, cerca de Buenos Aires
            results = geolocator.geocode(busqueda + ", Buenos Aires, Argentina", exactly_one=False, limit=5, addressdetails=True, country_codes='ar')
            if results:
                st.session_state.resultados_busqueda = results
            else:
                st.warning("No encontré esa dirección. Probá más completa: Ej. Ruta 21 5000, Ciudad Evita, La Matanza")

if 'resultados_busqueda' in st.session_state:
    opciones = [r.address for r in st.session_state.resultados_busqueda]
    seleccion = st.selectbox("Elegí la opción correcta:", opciones)
    if st.button("✅ Usar esta dirección"):
        st.session_state.dir_elegida = seleccion
        st.success(f"Dirección seleccionada: {seleccion}")

st.markdown("---")
st.markdown("### 2. Cargar Pedido")
with st.form("pedido_form"):
    cliente = st.text_input("Cliente*")
    # Si ya eligió una dirección del buscador, aparece acá
    direccion_final = st.text_input("Dirección completa final*", value=st.session_state.dir_elegida)
    col1, col2 = st.columns(2)
    with col1:
        zona = st.selectbox("Zona de Reparto", [
            "--- CABA ---",
            "CABA - Microcentro / San Telmo",
            "CABA - Norte (Palermo, Belgrano, Nuñez)",
            "CABA - Sur (Barracas, La Boca, Parque Patricios)",
            "CABA - Oeste (Caballito, Flores, Floresta)",
            "--- ZONA SUR ---",
            "Avellaneda / Wilde / Sarandí",
            "Lanús / Gerli / Remedios de Escalada",
            "Lomas de Zamora / Banfield / Temperley",
            "Adrogué / Burzaco / Longchamps",
            "Quilmes / Bernal / Ezpeleta",
            "Berazategui / Florencio Varela",
            "Monte Grande / Ezeiza / Canning",
            "--- ZONA OESTE (TU ZONA FUERTE) ---",
            "Ciudad Evita / San Justo / Ramos Mejía",
            "González Catán / Laferrere / Rafael Castillo",
            "Isidro Casanova / Gregorio de Laferrere",
            "Morón / Haedo / Castelar",
            "Hurlingham / Ituzaingó / Merlo",
            "Moreno / La Reja / Francisco Álvarez",
            "--- ZONA NORTE ---",
            "Vicente López / Olivos / Florida",
            "San Isidro / Martínez / Acassuso",
            "San Fernando / Victoria / Tigre",
            "Pilar / Del Viso / Tortuguitas",
            "Escobar / Garín / Maschwitz",
            "--- OTRA ---",
            "Otra Zona"
        ])
        monto = st.number_input("Monto ($)", min_value=0, step=500)
    with col2:
        repartidor = st.selectbox("Repartidor", ["Repartidor 1", "Repartidor 2", "Repartidor 3"])
        nota = st.text_area("Nota")
    enviado = st.form_submit_button("✅ Agregar Pedido")
    if enviado and cliente and direccion_final:
        st.session_state.pedidos.append({"Cliente": cliente, "Dirección": direccion_final, "Zona": zona, "Monto": monto})
        st.success("Agregado!")
        st.session_state.dir_elegida = ""
        st.session_state.resultados_busqueda = []

if st.session_state.pedidos:
    df = pd.DataFrame(st.session_state.pedidos)
    st.dataframe(df, use_container_width=True)
    st.success(f"📦 Total Pedidos: {len(df)} | 💰 Total: ${df['Monto'].sum():,.0f}")
    base_url = "https://www.google.com/maps/dir/"
    direcciones_url = "/".join([quote_plus(d) for d in df["Dirección"].tolist()])
    link_maps = base_url + direcciones_url
    st.link_button("🗺️ ABRIR RECORRIDO EN GOOGLE MAPS", link_maps)