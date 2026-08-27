import streamlit as st
import pandas as pd
from urllib.parse import quote_plus
from geopy.geocoders import Nominatim

st.set_page_config(page_title="Buenas Raíces", page_icon="🌱", layout="wide")
st.markdown("""<style>.stApp { background-color: #121212; color: #EAEAEA; } h1, h2, h3 { color: #EAEAEA!important; }</style>""", unsafe_allow_html=True)

# --- TITULO NUEVO QUE ME PEDISTE ---
st.title("Buenas Raíces 🌱 - Reparto")

geolocator = Nominatim(user_agent="buenas_raices_app_v2")
if 'pedidos' not in st.session_state: st.session_state.pedidos = []
if 'dir_elegida' not in st.session_state: st.session_state.dir_elegida = ""

def repartidor_por_zona(zona_texto):
    z = zona_texto.upper()
    if any(x in z for x in ["SUR", "AVELLANEDA", "WILDE", "LANUS", "LOMAS", "BANFIELD", "TEMPERLEY", "ADROGUE", "BURZACO", "QUILMES", "BERAZATEGUI", "VARELA", "MONTE GRANDE", "GUILLON", "EZEIZA", "CANNING"]):
        return "Repartidor 2 - SUR"
    elif any(x in z for x in ["CABA", "NORTE", "VICENTE", "OLIVOS", "SAN ISIDRO", "TIGRE", "PILAR", "ESCOBAR"]):
        return "Repartidor 3 - CABA y NORTE"
    else:
        return "Repartidor 1 - OESTE"

# --- BUSCADOR ---
st.markdown("### 1. Buscar Dirección")
busqueda = st.text_input("Escribí la dirección", placeholder="Ej: El Chacabuco 4000, Ciudad Evita")
if st.button("🔍 Buscar opciones"):
    if busqueda:
        with st.spinner("Buscando..."):
            results = geolocator.geocode(busqueda + ", Buenos Aires, Argentina", exactly_one=False, limit=5, country_codes='ar')
            if results: st.session_state.resultados_busqueda = results
            else: st.warning("No encontré. Probá: Calle 1234, Localidad")

if 'resultados_busqueda' in st.session_state:
    opciones = [r.address for r in st.session_state.resultados_busqueda]
    seleccion = st.selectbox("Elegí la correcta:", opciones)
    if st.button("✅ Usar esta dirección"):
        st.session_state.dir_elegida = seleccion
        st.success(f"Seleccionada: {seleccion}")

st.markdown("---")
st.markdown("### 2. Cargar Pedido")

# --- TODAS LAS ZONAS QUE ME PEDISTE ---
todas_las_zonas = [
    "CABA - Microcentro / San Telmo / La Boca",
    "CABA - Norte (Palermo, Belgrano, Nuñez)",
    "CABA - Oeste (Caballito, Flores, Floresta, Liniers)",
    "CABA - Sur (Barracas, Parque Patricios, Boedo)",
    "--- ZONA SUR COMPLETA ---",
    "Avellaneda / Dock Sud / Sarandí / Wilde",
    "Lanús Este / Lanús Oeste / Gerli / Valentín Alsina",
    "Lomas de Zamora / Banfield / Temperley / Llavallol",
    "Turdera / Adrogué / Burzaco / Longchamps / Glew",
    "Quilmes / Bernal / Ezpeleta / Don Bosco",
    "Berazategui / Ranelagh / Florencio Varela / Bosques",
    "Monte Grande / Luis Guillón / El Jagüel / Esteban Echeverría",
    "Ezeiza / Tristán Suárez / Canning / Spegazzini / La Unión",
    "Guernica / Presidente Perón / San Vicente / Alejandro Korn",
    "--- ZONA OESTE ---",
    "San Justo / Ramos Mejía / Lomas del Mirador / La Tablada",
    "Ciudad Evita / Isidro Casanova / Villa Luzuriaga",
    "González Catán / Virrey del Pino / Rafael Castillo",
    "Gregorio de Laferrere",
    "Morón / Haedo / Castelar / El Palomar",
    "Hurlingham / William Morris / Ituzaingó / Villa Udaondo",
    "Merlo / Parque San Martín / Libertad / Pontevedra",
    "Moreno / Paso del Rey / La Reja / Francisco Álvarez",
    "--- ZONA NORTE ---",
    "Vicente López / Olivos / La Lucila / Florida / Munro",
    "San Isidro / Martínez / Acassuso / Beccar / Boulogne",
    "San Fernando / Victoria / Virreyes / Tigre / Don Torcuato",
    "El Talar / Pacheco / Benavídez / Garín / Maschwitz",
    "Pilar / Del Viso / Tortuguitas / Manuel Alberti",
    "Escobar / Matheu / Belén de Escobar",
    "Otra Zona"
]

with st.form("pedido_form"):
    cliente = st.text_input("Cliente*")
    direccion_final = st.text_input("Dirección final*", value=st.session_state.dir_elegida)
    col1, col2 = st.columns(2)
    with col1:
        zona = st.selectbox("Zona de Reparto", todas_las_zonas)
        repartidor_sugerido = repartidor_por_zona(zona)
        st.info(f"👉 Va para: **{repartidor_sugerido}**")
        repartidor = st.selectbox("Repartidor", ["Repartidor 1 - OESTE", "Repartidor 2 - SUR", "Repartidor 3 - CABA y NORTE"], index=["Repartidor 1 - OESTE", "Repartidor 2 - SUR", "Repartidor 3 - CABA y NORTE"].index(repartidor_sugerido))
    with col2:
        monto = st.number_input("Monto ($)", min_value=0, step=500)
        nota = st.text_area("Nota")
    enviado = st.form_submit_button("✅ Agregar Pedido")
    if enviado and cliente and direccion_final:
        st.session_state.pedidos.append({"Cliente": cliente, "Dirección": direccion_final, "Zona": zona, "Monto": monto, "Repartidor": repartidor, "Nota": nota})
        st.success(f"Agregado a {repartidor}!")
        st.session_state.dir_elegida = ""

# --- LISTA CON BOTON PARA BORRAR UNO SOLO ---
if st.session_state.pedidos:
    st.markdown("---")
    st.markdown(f"### 📦 Pedidos cargados ({len(st.session_state.pedidos)})")

    df = pd.DataFrame(st.session_state.pedidos)
    st.dataframe(df, use_container_width=True)
    st.success(f"💰 Total: ${df['Monto'].sum():,.0f}")

    st.markdown("**Borrar un pedido puntual:**")
    for i in range(len(st.session_state.pedidos)-1, -1, -1):
        pedido = st.session_state.pedidos[i]
        col_a, col_b = st.columns([4, 1])
        with col_a:
            st.write(f"**{i+1}.** {pedido['Cliente']} - {pedido['Dirección']} ({pedido['Zona']})")
        with col_b:
            if st.button(f"🗑️ Borrar", key=f"del_{i}"):
                st.session_state.pedidos.pop(i)
                st.rerun()

    st.markdown("---")
    # Links por repartidor
    for rep in df["Repartidor"].unique():
        df_rep = df[df["Repartidor"] == rep]
        link = "https://www.google.com/maps/dir/" + "/".join([quote_plus(d) for d in df_rep["Dirección"].tolist()])
        st.link_button(f"🗺️ Recorrido {rep} ({len(df_rep)} paradas)", link)