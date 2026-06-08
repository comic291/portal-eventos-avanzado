import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="¡Qué Hay Pa' Hacer! - Agenda Viva", page_icon="⚡", layout="centered")

# --- DISEÑO PREMIUM ---
st.markdown("""
    <style>
    .app-title { font-size: 42px; font-weight: 900; background: linear-gradient(90deg, #ec4899, #8b5cf6, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 2px; }
    .app-subtitle { font-size: 16px; color: #94a3b8; text-align: center; margin-bottom: 25px; }
    .badge-categoria { background-color: #3b82f6; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: bold; display: inline-block; margin-bottom: 8px; }
    .card-evento { background-color: #1e293b; border: 1px solid #334155; border-radius: 16px; padding: 20px; margin-bottom: 15px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }
    .card-title { font-size: 20px; font-weight: 700; color: #f8fafc; margin-bottom: 6px; }
    .card-meta { font-size: 13px; color: #38bdf8; margin-bottom: 10px; }
    .card-desc { font-size: 14px; color: #cbd5e1; line-height: 1.5; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- ESTADO DE SESIÓN ---
if "anuncios_pauta" not in st.session_state:
    st.session_state.anuncios_pauta = ""

st.markdown('<h1 class="app-title">⚡ ¡Qué Hay Pa\' Hacer!</h1>', unsafe_allow_html=True)
st.markdown('<p class="app-subtitle">Agenda 100% real extraída de la red.</p>', unsafe_allow_html=True)

# --- ZONA DE ANUNCIOS DESTACADOS ---
if st.session_state.anuncios_pauta:
    st.markdown(f"""
    <div style="background-color: #3b82f6; color: white; padding: 15px; border-radius: 10px; margin-bottom: 20px; text-align: center; font-weight: bold; border: 2px solid #ffffff;">
        🌟 EVENTO DESTACADO: {st.session_state.anuncios_pauta}
    </div>
    """, unsafe_allow_html=True)

# --- PANEL DE CONTROL ---
st.sidebar.markdown("### 🔐 Panel de Control")
clave = st.sidebar.text_input("Contraseña:", type="password")
if clave == "TuClaveSecreta123":
    st.session_state.anuncios_pauta = st.sidebar.text_area("Editar Evento Destacado:", value=st.session_state.anuncios_pauta)

# --- MOTOR DE BÚSQUEDA ---
@st.cache_data(ttl=3600)
def escanear_agenda_real(ciudad, categoria):
    headers = {"User-Agent": "Mozilla/5.0"}
    terminos = {
        "gratis": f"eventos gratis entrada libre {ciudad}",
        "rumba": f"rumba discotecas conciertos {ciudad}",
        "cc": f"ferias exposiciones centros comerciales {ciudad}",
        "cine": f"cartelera cine estrenos {ciudad}",
        "deportes": f"actividades deportivas ciclovia {ciudad}"
    }
    query = terminos.get(categoria, f"agenda cultural {ciudad}")
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
    try:
        r = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')
        resultados = []
        for el in soup.find_all('div', class_='MjjYud'):
            h3 = el.find('h3')
            desc = el.find('div', class_='VwiC3b')
            link = el.find('a')
            if h3 and desc and link:
                resultados.append({"titulo": h3.get_text(), "descripcion": desc.get_text(), "link": link['href']})
        return resultados[:5]
    except:
        return []

# --- INTERFAZ ---
ciudad_input = st.text_input("¿En qué ciudad estás?", value="Medellin")
tab_gratis, tab_rumba, tab_cc, tab_cine, tab_deportes = st.tabs(["🔥 GRATIS", "🎸 RUMBA", "🏢 CC", "🎬 CINE", "🏃 DEPORTES"])

def renderizar_pestaña(tab, cat, header, icon):
    with tab:
        st.markdown(f"### {icon} {header}")
        with st.spinner("Buscando eventos reales..."):
            eventos = escanear_agenda_real(ciudad_input, cat)
            if not eventos:
                st.info("No se encontraron resultados en este momento.")
            else:
                for ev in eventos:
                    st.markdown(f"""
                    <div class="card-evento">
                        <div class="card-title">{ev['titulo']}</div>
                        <div class="card-desc">{ev['descripcion']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.link_button("Ver más detalles", ev['link'], use_container_width=True)

renderizar_pestaña(tab_gratis, "gratis", "Planes Libres", "🔥")
renderizar_pestaña(tab_rumba, "rumba", "Rumba y Conciertos", "🎸")
renderizar_pestaña(tab_cc, "cc", "Centros Comerciales", "🏢")
renderizar_pestaña(tab_cine, "cine", "Cine y Estrenos", "🎬")
renderizar_pestaña(tab_deportes, "deportes", "Deportes", "🏃")

st.markdown("---")
st.caption("⚡ Portal Comercial v8.0 | Motor de Extracción Híbrido.")
