import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
from datetime import datetime

# --- ZONA DE CONTROL PRIVADA (INSERCIÓN) ---
if "anuncio_vip" not in st.session_state:
    st.session_state.anuncio_vip = ""

# Configuración de página con estilo premium oscuro/neón para enganchar al público joven
st.set_page_config(page_title="¡Qué Hay Pa' Hacer! - Agenda Viva", page_icon="⚡", layout="centered")

# --- DISEÑO DE INTERFAZ PREMIUM (CSS INYECTADO) ---
st.markdown("""
    <style>
    /* Estilos globales */
    .main { background-color: #0f172a; }
    h1, h2, h3 { font-family: 'Inter', sans-serif; }
    
    .app-title {
        font-size: 42px;
        font-weight: 900;
        background: linear-gradient(90deg, #ec4899, #8b5cf6, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2px;
    }
    .app-subtitle {
        font-size: 16px;
        color: #94a3b8;
        text-align: center;
        margin-bottom: 25px;
    }
    .badge-gratis {
        background-color: #10b981;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 8px;
    }
    .badge-categoria {
        background-color: #3b82f6;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 8px;
    }
    .card-evento {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    .card-title {
        font-size: 20px;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 6px;
    }
    .card-meta {
        font-size: 13px;
        color: #38bdf8;
        margin-bottom: 10px;
    }
    .card-desc {
        font-size: 14px;
        color: #cbd5e1;
        line-height: 1.5;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- PANEL DE ADMINISTRACIÓN (SOLO PARA TI EN SIDEBAR) ---
st.sidebar.markdown("### 🔐 Alex: Gestión Privada")
clave = st.sidebar.text_input("Clave:", type="password")
if clave == "TuClave123": # Cambia esto por tu clave
    st.session_state.anuncio_vip = st.sidebar.text_area("Evento para Publicar:", value=st.session_state.anuncio_vip)

st.markdown('<h1 class="app-title">⚡ ¡Qué Hay Pa\' Hacer!</h1>', unsafe_allow_html=True)

# --- ZONA DE ANUNCIO (VISIBLE ARRIBA) ---
if st.session_state.anuncio_vip:
    st.markdown(f'<div style="background:#3b82f6; color:white; padding:15px; border-radius:16px; text-align:center; font-weight:bold; margin-bottom:20px;">🌟 PATROCINADO: {st.session_state.anuncio_vip}</div>', unsafe_allow_html=True)

st.markdown('<p class="app-subtitle">La única app en Colombia con eventos 100% reales extraídos de la red en tiempo real.</p>', unsafe_allow_html=True)

# --- SISTEMA INTELIGENTE DE EXTRACCIÓN (TU CÓDIGO ORIGINAL SIN CAMBIOS) ---
@st.cache_data(ttl=3600)
def escanear_agenda_real(ciudad, categoria):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/122.0.0.0",
        "Accept-Language": "es-ES,es;q=0.9"
    }
    terminos = {
        "gratis": f"conciertos gratis feria entrada libre hoy {ciudad} 2026",
        "rumba": f"conciertos discotecas eventos rumba esta semana {ciudad}",
        "cc": f"eventos exposiciones ferias centros comerciales {ciudad}",
        "cine": f"cartelera estrenos funciones cine colombia {ciudad}",
        "deportes": f"ciclovia carreras torneos eventos deportivos {ciudad}"
    }
    query = terminos.get(categoria, f"eventos agenda cultural {ciudad}")
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&hl=es&gl=co"
    eventos_encontrados = []
    try:
        r = requests.get(url, headers=headers, timeout=7)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            elementos = soup.find_all('div', class_='MjjYud')
            for el in elementos:
                h3 = el.find('h3')
                snippet = el.find('div', class_='VwiC3b')
                link_tag = el.find('a')
                if h3 and snippet and link_tag:
                    titulo = h3.get_text()
                    descripcion = snippet.get_text()
                    link = link_tag['href']
                    if len(titulo) > 15 and "https://" in link and not any(x in titulo.lower() for x in ["google", "maps", "traductor"]):
                        for separador in [" | ", " - ", " – "]:
                            if separador in titulo:
                                titulo = titulo.split(separador)[0]
                        eventos_encontrados.append({"titulo": titulo.strip(), "descripcion": descripcion.strip(), "link": link})
                if len(eventos_encontrados) >= 4:
                    break
    except Exception as e:
        pass
    if not eventos_encontrados:
        # Aquí mantienes tu lógica de contingencia original
        return [{"titulo": "Revisa tu conexión", "descripcion": "No se encontraron eventos, intenta refrescar.", "link": "#"}]
    return eventos_encontrados

# --- ESTRUCTURA ORIGINAL (SIN CAMBIOS) ---
with st.container(border=True):
    st.markdown("### 📍 Configura Tu Parche")
    ciudad_input = st.text_input("¿En qué ciudad o municipio estás?", value="Medellin")
    ciudad_limpia = ciudad_input.strip().title()

tab_gratis, tab_rumba, tab_cc, tab_cine, tab_deportes = st.tabs([
    "🔥 TODO GRATIS", "🎸 Rumba y Conciertos", "🏢 Centros Comerciales", "🎬 Cine y Estrenos", "🏃 Deportes y Parques"
])

def renderizar_pestaña(tab_objeto, clave_cat, texto_header, badge_type, icono):
    with tab_objeto:
        st.markdown(f"### {icono} {texto_header} en {ciudad_limpia}")
        with st.spinner("Escaneando transmisiones de red..."):
            lista_eventos = escanear_agenda_real(ciudad_limpia.lower(), clave_cat)
            for ev in lista_eventos:
                st.markdown(f"""
                <div class="card-evento">
                    <span class="{badge_type}">{clave_cat.upper()} CONFIRMADO</span>
                    <div class="card-title">{ev['titulo']}</div>
                    <div class="card-meta">📍 Ubicación en {ciudad_limpia}</div>
                    <div class="card-desc">{ev['descripcion']}</div>
                </div>
                """, unsafe_allow_html=True)
                st.link_button("🌐 Ver Detalles y Horarios", ev['link'], use_container_width=True)

renderizar_pestaña(tab_gratis, "gratis", "Planes Con Entrada Libre", "badge-gratis", "🔥")
renderizar_pestaña(tab_rumba, "rumba", "Conciertos, Bares y Vida Nocturna", "badge-categoria", "🎸")
renderizar_pestaña(tab_cc, "cc", "Muestras y Ferias en Centros Comerciales", "badge-categoria", "🏢")
renderizar_pestaña(tab_cine, "cine", "Películas y Carteleras de Estrenos", "badge-categoria", "🎬")
renderizar_pestaña(tab_deportes, "deportes", "Ciclovías y Actividades de Fin de Semana", "badge-categoria", "🏃")

st.markdown("---")
st.caption("⚡ Portal Comercial v8.0 | Motor de Extracción Híbrido.")
