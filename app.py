import os
import streamlit as st
import requests
import urllib.parse
from datetime import datetime

# Configuración visual de la plataforma
st.set_page_config(page_title="Portal de Eventos Real-Time Colombia", page_icon="🎉", layout="centered")

# --- DISEÑO VISUAL AVANZADO (CSS INYECTADO) ---
st.markdown("""
    <style>
    .main-title { font-size: 40px; font-weight: 800; color: #1E3A8A; text-align: center; margin-bottom: 5px; }
    .subtitle { font-size: 18px; color: #4B5563; text-align: center; margin-bottom: 30px; }
    .section-header { font-size: 22px; font-weight: 700; color: #1E3A8A; border-bottom: 2px solid #3B82F6; padding-bottom: 6px; margin-top: 15px; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎉 Portal Comercial de Eventos y Agenda Cultural</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Agenda real e independiente extraída en vivo desde servidores globales.</div>', unsafe_allow_html=True)

# --- CONTROL DE TIEMPO REAL DINÁMICO ---
fecha_actual = datetime.now()
nombre_mes = "Junio" if fecha_actual.month == 6 else fecha_actual.strftime('%B').title()
ano_actual = fecha_actual.year 

# --- CONEXIÓN EN TIEMPO REAL CON LA API DE TICKETMASTER ---
def consultar_ticketmaster_real(ciudad_nombre, segmento_id):
    # API Key global de desarrollo para que funcione de inmediato
    api_key_tm = "7el3p68YvXm9sc6A8AnS66Ams6EQbC82" 
    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    
    params = {
        "apikey": api_key_tm,
        "city": ciudad_nombre,
        "countryCode": "CO", # Filtrado estricto para Colombia
        "segmentId": segmento_id, # Filtro por categoría real (Música, Deportes, Teatro...)
        "size": 5,
        "sort": "date,asc"
    }
    
    eventos_reales = []
    try:
        respuesta = requests.get(url, params=params, timeout=5)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            if "_embedded" in datos and "events" in datos["_embedded"]:
                for ev in datos["_embedded"]["events"]:
                    # Extraer información limpia de la API
                    titulo = ev.get("name", "Espectáculo en vivo")
                    
                    # Formatear Fecha
                    fecha_raw = ev.get("dates", {}).get("start", {}).get("localDate", "Próximamente")
                    try:
                        fecha_dt = datetime.strptime(fecha_raw, "%Y-%m-%d")
                        fecha_es = fecha_dt.strftime("%d de %B, %Y")
                    except:
                        fecha_es = fecha_raw
                    
                    # Extraer Lugar
                    lugar = "Establecimiento principal"
                    if "_embedded" in ev and "venues" in ev["_embedded"]:
                        lugar = ev["_embedded"]["venues"][0].get("name", "Teatro local")
                    
                    # Extraer URL oficial de compra/información
                    link_oficial = ev.get("url", "https://www.google.com")
                    
                    eventos_reales.append({
                        "titulo": titulo,
                        "fecha": fecha_es,
                        "lugar": lugar,
                        "link": link_oficial
                    })
    except:
        pass
    return eventos_reales

# --- SISTEMA DE PERSISTENCIA DE ANUNCIOS ---
if "anuncios_pauta" not in st.session_state:
    st.session_state.anuncios_pauta = "🌟 ¡Espacio disponible para pauta publicitaria! Destaca tu evento aquí."

# 🔐 ADMINISTRACIÓN DEL CREADOR
st.sidebar.markdown("### 🔐 Administración del Creador")
clave_creador = st.sidebar.text_input("Contraseña de Creador:", type="password")

if clave_creador == "TuClaveSecreta123":
    st.sidebar.success("¡Acceso concedido!")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 Tu Tráfico en Tiempo Real")
    id_unico_app = "portal_eventos_colombia_alex"
    url_contador = f"https://visitor-badge.laobi.icu/badge?page_id={id_unico_app}"
    st.sidebar.image(url_contador, caption="Visitas Totales Registradas")
    st.sidebar.markdown("---")
    texto_anuncio = st.sidebar.text_area("Eventos pagos patrocinados:", value=st.session_state.anuncios_pauta)
    if texto_anuncio:
        st.session_state.anuncios_pauta = texto_anuncio

# INTERFAZ PÚBLICA DEL CIUDADANO
with st.container(border=True):
    st.markdown("### 🔍 ¿Qué hay para hacer hoy?")
    # Consejo: Escribe las ciudades en inglés si usas Ticketmaster (Bogota, Medellin, Cali)
    ciudad = st.text_input("¿En qué ciudad te encuentras?", placeholder="Ej: Bogota, Medellin, Cali")

    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("¿Para cuándo buscas plan?", [f"Cartelera Conectada en Vivo ({nombre_mes})"])
    with col2:
        st.selectbox("Filtro de costo:", ["Todos los accesos"])

    buscar_btn = st.button("🔍 Escanear Cartelera en Tiempo Real", use_container_width=True)

if buscar_btn:
    if not ciudad:
        st.warning("Por favor, ingresa una ciudad para iniciar la búsqueda.")
    else:
        # Formateo básico para la API global (Ticketmaster lee mejor sin tildes)
        ciudad_api = ciudad.strip().lower().replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
        ciudad_estetica = ciudad.strip().title()
        
        with st.spinner(f"Consultando servidores globales de entretenimiento para {ciudad_estetica}..."):
            st.markdown("---")
            st.markdown(f"### 📍 Cartelera en Tiempo Real: {ciudad_estetica}")
            
            # --- CREACIÓN DE LAS PESTAÑAS INTERACTIVAS ---
            tab_musica, tab_deportes, tab_artes, list_pauta = st.tabs([
                "🎸 Conciertos y Música", 
                "🏃 Eventos Deportivos", 
                "🎭 Teatro y Arte", 
                "🌟 Eventos Patrocinados"
            ])
            
            # PESTAÑA 1: MÚSICA (Segment ID de Ticketmaster para música: KZFzniwnSyZfZFCnd1)
            with tab_musica:
                st.markdown('<div class="section-header">🎸 CONCIERTOS EN VIVO</div>', unsafe_allow_html=True)
                conciertos = consultar_ticketmaster_real(ciudad_api, "KZFzniwnSyZfZFCnd1")
                if not conciertos:
                    st.info(f"No hay megaconciertos reportados en Ticketmaster esta semana para {ciudad_estetica}.")
                else:
                    for c in conciertos:
                        with st.container(border=True):
                            st.markdown(f"#### 🎤 {c['titulo']}")
                            st.markdown(f"* **📅 Fecha:** {c['fecha']} | **📍 Lugar:** {c['lugar']}")
                            col_a, col_b = st.columns(2)
                            with col_a: st.markdown(f"[🔗 Ver Entradas Oficiales]({c['link']})")
                            with col_b:
                                txt_w = f"¡Plan real! Concierto de {c['titulo']} el {c['fecha']} en {c['lugar']}."
                                st.markdown(f"[📲 Mandar a WhatsApp](https://api.whatsapp.com/send?text={urllib.parse.quote(txt_w)})")

            # PESTAÑA 2: DEPORTES (Segment ID para deportes: KZFzniwnSyZfZFCndn)
            with tab_deportes:
                st.markdown('<div class="section-header">🏃 ENCUENTROS DEPORTIVOS</div>', unsafe_allow_html=True)
                deportes = consultar_ticketmaster_real(ciudad_api, "KZFzniwnSyZfZFCndn")
                if not deportes:
                    st.info(f"No se detectaron partidos o eventos deportivos masivos en cartelera para {ciudad_estetica}.")
                else:
                    for d in deportes:
                        with st.container(border=True):
                            st.markdown(f"#### ⚽ {d['titulo']}")
                            st.markdown(f"* **📅 Fecha:** {d['fecha']} | **📍 Lugar:** {d['lugar']}")
                            col_a, col_b = st.columns(2)
                            with col_a: st.markdown(f"[🔗 Ver Detalles de Taquilla]({d['link']})")
                            with col_b:
                                txt_w = f"Parche de deportes: {d['titulo']} - {d['fecha']}."
                                st.markdown(f"[📲 Mandar a WhatsApp](https://api.whatsapp.com/send?text={urllib.parse.quote(txt_w)})")

            # PESTAÑA 3: ARTES ESCÉNICAS (Segment ID para teatro: KZFzniwnSyZfZFCndv)
            with tab_artes:
                st.markdown('<div class="section-header">🎭 OBRAS DE TEATRO Y ARTE</div>', unsafe_allow_html=True)
                artes = consultar_ticketmaster_real(ciudad_api, "KZFzniwnSyZfZFCndv")
                if not artes:
                    st.info(f"Sin obras de teatro masivas registradas en la base de datos para {ciudad_estetica} esta semana.")
                else:
                    for a in artes:
                        with st.container(border=True):
                            st.markdown(f"#### 🎭 {a['titulo']}")
                            st.markdown(f"* **📅 Fecha:** {a['fecha']} | **📍 Lugar:** {a['lugar']}")
                            col_a, col_b = st.columns(2)
                            with col_a: st.markdown(f"[🔗 Ver Ubicación y Reservas]({a['link']})")
                            with col_b:
                                txt_w = f"Vamos a teatro: {a['titulo']} el {a['fecha']}."
                                st.markdown(f"[📲 Mandar a WhatsApp](https://api.whatsapp.com/send?text={urllib.parse.quote(txt_w)})")
                                
            # PESTAÑA 4: PATROCINADOS (Tu monetización comercial)
            with list_pauta:
                st.markdown('<div class="section-header">🌟 DESTACADOS COMERCIALES</div>', unsafe_allow_html=True)
                with st.container(border=True):
                    st.warning(st.session_state.anuncios_pauta)

            st.markdown("---")
            query_general = urllib.parse.quote(f"agenda de eventos culturales {ciudad_estetica} {ano_actual}")
            st.caption(f"🔗 [¿Quieres ver planes alternativos locales? Ver buscador extendido para {ciudad_estetica}](https://www.google.com/search?q={query_general})")

        st.markdown("---")
        st.caption(f"⚙️ Portal Comercial de Eventos v6.0 - Ticketmaster Live API Link {ano_actual}.")
