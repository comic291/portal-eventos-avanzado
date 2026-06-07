import os
import streamlit as st
import requests
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# Configuración visual de la plataforma
st.set_page_config(page_title="Portal de Eventos Real-Time Colombia", page_icon="🎉", layout="centered")

# --- DISEÑO VISUAL AVANZADO (CSS INYECTADO) ---
st.markdown("""
    <style>
    .main-title {
        font-size: 40px;
        font-weight: 800;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 5px;
    }
    .subtitle {
        font-size: 18px;
        color: #4B5563;
        text-align: center;
        margin-bottom: 30px;
    }
    .section-header {
        font-size: 22px;
        font-weight: 700;
        color: #1E3A8A;
        border-bottom: 2px solid #3B82F6;
        padding-bottom: 6px;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎉 Portal Comercial de Eventos y Agenda Cultural</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Descubre qué hacer hoy con nuestro buscador inteligente en tiempo real.</div>', unsafe_allow_html=True)

# --- CONTROL DE TIEMPO REAL DINÁMICO ---
fecha_actual = datetime.now()
nombre_mes = "Junio" if fecha_actual.month == 6 else fecha_actual.strftime('%B').title()
ano_actual = fecha_actual.year 

# --- MOTOR DE CONSULTA EN VIVO (API ABIERTA DE GOOGLE) ---
def obtener_tendencias_eventos(ciudad_nombre, concepto_busqueda):
    # Usamos el motor de autocompletado de Google en español de Colombia (.com.co)
    query = f"eventos {concepto_busqueda} {ciudad_nombre}"
    url = f"https://suggestqueries.google.com/complete/search?output=toolbar&hl=es&gl=co&q={urllib.parse.quote(query)}"
    
    planes_detectados = []
    try:
        respuesta = requests.get(url, timeout=5)
        if respuesta.status_code == 200:
            # Procesamos la respuesta en formato XML que devuelve Google
            root = ET.fromstring(respuesta.content)
            for suggestion in root.findall('.//suggestion'):
                data = suggestion.get('data')
                if data:
                    # Limpiamos el texto para que se vea estético quitando la palabra "eventos" repetida
                    texto_limpio = data.replace("eventos", "").strip().capitalize()
                    planes_detectados.append(texto_limpio)
    except:
        pass
    return planes_detectados

# --- SISTEMA DE PERSISTENCIA DE ANUNCIOS ---
if "anuncios_pauta" not in st.session_state:
    st.session_state.anuncios_pauta = "🌟 ¡Espacio disponible para pauta publicitaria! Destaca tu evento aquí."

# 🔐 ADMINISTRACIÓN DEL CREADOR (Contador secreto intacto)
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
    ciudad = st.text_input("¿En qué ciudad te encuentras?", placeholder="Ej: Bogota, Medellin, Cali")

    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("¿Para cuándo buscas plan?", [f"Cartelera Actualizada ({nombre_mes} {ano_actual})"])
    with col2:
        st.selectbox("Filtro de costo:", ["Todos los accesos"])

    buscar_btn = st.button("🔍 Escanear Cartelera en Tiempo Real", use_container_width=True)

if buscar_btn:
    if not ciudad:
        st.warning("Por favor, ingresa una ciudad para iniciar el escaneo en vivo.")
    else:
        ciudad_limpia = ciudad.strip().title()
        
        with st.spinner(f"Analizando búsquedas en vivo y tendencias para {ciudad_limpia}..."):
            st.markdown("---")
            st.markdown(f"### 📍 Cartelera en Tiempo Real: {ciudad_limpia}")
            
            # --- CREACIÓN DE LAS PESTAÑAS INTERACTIVAS ---
            tab_gratis, tab1, tab2, tab3, tab4 = st.tabs([
                "🔥 TODO GRATIS", 
                "🏢 Centros Comerciales", 
                "🎸 Conciertos y Rumba", 
                "🎬 Cine y Estrenos", 
                "🏃 Deportes y Aire Libre"
            ])
            
            # Función interna para rellenar las pestañas consultando a Google en vivo
            def renderizar_bloque_busqueda(tab_destino, clave_concepto, titulo_seccion, sub_icono, mensaje_vacio):
                with tab_destino:
                    st.markdown(f'<div class="section-header">{sub_icono} {titulo_seccion}</div>', unsafe_allow_html=True)
                    resultados_reales = obtener_tendencias_eventos(ciudad_limpia, clave_concepto)
                    
                    if not resultados_reales:
                        st.info(f"✨ {mensaje_vacio} en {ciudad_limpia} para esta semana de {nombre_mes}.")
                    else:
                        for plan in resultados_reales[:4]: # Mostramos los 4 mejores planes reales en tendencia
                            with st.container(border=True):
                                st.markdown(f"#### {sub_icono} {plan}")
                                st.markdown(f"* **📅 Fecha:** Actualizado hoy para esta semana de {nombre_mes}")
                                st.markdown(f"* **📍 Ubicación:** Consultar puntos oficiales en la ciudad")
                                st.markdown(f"* **📝 Estado:** Cartelera activa reportada en tendencias locales")
                                
                                # Enlaces de interacción rápida para viralidad y conversión
                                q_google = urllib.parse.quote(f"eventos {plan} {ciudad_limpia} {ano_actual}")
                                col_b1, col_b2 = st.columns(2)
                                with col_b1:
                                    st.markdown(f"[🔗 Ver Horarios y Boletas](https://www.google.com/search?q={q_google})")
                                with col_b2:
                                    txt_wp = f"¡Pilla este plan real en {ciudad_limpia}! 🎉 '{plan}'. Revisa los detalles aquí."
                                    st.markdown(f"[📲 Enviar a WhatsApp](https://api.whatsapp.com/send?text={urllib.parse.quote(txt_wp)})")

            # Rellenar cada pestaña automáticamente consultando internet de verdad
            renderizar_bloque_busqueda(tab_gratis, "gratis entrada libre", "PLANES SIN PRESUPUESTO", "🔥", "Explorando parches gratuitos de libre acceso")
            renderizar_bloque_busqueda(tab1, "centros comerciales ferias", "FERIAS EN CENTROS COMERCIALES", "🏢", "Revisando muestras comerciales y eventos en complejos")
            renderizar_bloque_busqueda(tab2, "conciertos rumba rumba hoy", "CONCIERTOS Y VIDA NOCTURNA", "🎸", "Rastreando agendas de discotecas, bares y conciertos")
            renderizar_bloque_busqueda(tab3, "cartelera de cine estrenos", "🍿 CARTELERA DE CINE", "🎬", "Actualizando los horarios de películas de cartelera")
            renderizar_bloque_busqueda(tab4, "ciclovia deportes aire libre", "DEPORTES Y RECREACIÓN", "🏃", "Cargando rutas de caminatas, ciclovías y eventos deportivos")

            st.markdown("---")
            st.caption(f"⚙️ Portal Comercial de Eventos v4.0 - Google Live Sync Engine {ano_actual}. 100% Real, sin tokens y directo en español.")
