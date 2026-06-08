import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
from datetime import datetime

# --- ESPACIO PRIVADO DE ADMINISTRACIÓN ---
if "anuncio_pagado" not in st.session_state:
    st.session_state.anuncio_pagado = ""

# Configuración de página
st.set_page_config(page_title="¡Qué Hay Pa' Hacer! - Agenda Viva", page_icon="⚡", layout="centered")

# --- DISEÑO DE INTERFAZ PREMIUM ---
st.markdown("""
    <style>
    .main { background-color: #0f172a; }
    h1, h2, h3 { font-family: 'Inter', sans-serif; }
    .app-title { font-size: 42px; font-weight: 900; background: linear-gradient(90deg, #ec4899, #8b5cf6, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 2px; }
    .app-subtitle { font-size: 16px; color: #94a3b8; text-align: center; margin-bottom: 25px; }
    .card-evento { background-color: #1e293b; border: 1px solid #334155; border-radius: 16px; padding: 20px; margin-bottom: 15px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }
    .card-title { font-size: 20px; font-weight: 700; color: #f8fafc; margin-bottom: 6px; }
    .card-desc { font-size: 14px; color: #cbd5e1; line-height: 1.5; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- TU PANEL PRIVADO (Solo tú lo ves en la barra lateral) ---
st.sidebar.markdown("### 🔐 Gestión Privada (Solo Alex)")
st.session_state.anuncio_pagado = st.sidebar.text_area("Publicar evento pagado:", value=st.session_state.anuncio_pagado)

st.markdown('<h1 class="app-title">⚡ ¡Qué Hay Pa\' Hacer!</h1>', unsafe_allow_html=True)

# --- ZONA DE MONETIZACIÓN (Visible para todos, controlada por ti) ---
if st.session_state.anuncio_pagado:
    st.markdown(f'<div style="background:#3b82f6; color:white; padding:15px; border-radius:10px; text-align:center; margin-bottom:20px;">🌟 <b>EVENTO DESTACADO:</b> {st.session_state.anuncio_pagado}</div>', unsafe_allow_html=True)

st.markdown('<p class="app-subtitle">La única app en Colombia con eventos 100% reales extraídos de la red.</p>', unsafe_allow_html=True)

# --- SISTEMA DE EXTRACCIÓN (Resto del código original) ---
@st.cache_data(ttl=3600)
def escanear_agenda_real(ciudad, categoria):
    headers = {"User-Agent": "Mozilla/5.0"}
    terminos = {"gratis": f"eventos gratis {ciudad}", "rumba": f"rumba {ciudad}", "cc": f"ferias {ciudad}", "cine": f"cine {ciudad}", "deportes": f"deportes {ciudad}"}
    url = f"https://www.google.com/search?q={urllib.parse.quote(terminos.get(categoria, 'eventos'))}"
    try:
        r = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')
        eventos = []
        for el in soup.find_all('div', class_='MjjYud')[:3]:
            h3 = el.find('h3')
            link = el.find('a')
            if h3 and link:
                eventos.append({"titulo": h3.get_text(), "link": link['href']})
        return eventos
    except: return []

ciudad_input = st.text_input("Ciudad:", value="Medellin")
tabs = st.tabs(["🔥 GRATIS", "🎸 RUMBA", "🏢 CC", "🎬 CINE", "🏃 DEPORTES"])
categorias = ["gratis", "rumba", "cc", "cine", "deportes"]

for i, tab in enumerate(tabs):
    with tab:
        for ev in escanear_agenda_real(ciudad_input, categorias[i]):
            st.markdown(f'<div class="card-evento"><div class="card-title">{ev["titulo"]}</div></div>', unsafe_allow_html=True)
            st.link_button("Ver más", ev['link'], use_container_width=True)
