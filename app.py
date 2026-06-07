import os
import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

# Configuración visual del portal de eventos
st.set_page_config(page_title="Portal de Eventos Real-Time Colombia", page_icon="🎉")
st.title("🎉 Portal Comercial de Eventos y Agenda Cultural")
st.write("Consulta la cartelera de eventos en tiempo real de forma gratuita.")

# Manejo del estado (st.session_state) para que tus anuncios no se borren al buscar
if "anuncios_pauta" not in st.session_state:
    st.session_state.anuncios_pauta = "Ninguno por ahora"

# 🔐 TU PESTAÑA OCULTA DE CREADOR (Tu motor de monetización privada)
st.sidebar.markdown("### 🔐 Administración del Creador")
clave_creador = st.sidebar.text_input("Contraseña de Creador:", type="password")

if clave_creador == "TuClaveSecreta123": # Tu contraseña privada para ingresar anuncios
    st.sidebar.success("¡Acceso concedido!")
    texto_anuncio = st.sidebar.text_area(
        "Ingresa aquí los eventos pagos que te patrocinen:",
        value=st.session_state.anuncios_pauta if st.session_state.anuncios_pauta != "Ninguno por ahora" else "",
        placeholder="Ej: ⭐ [ANUNCIO] Gran Festival Gastronómico en el Parque Principal, Sábado 4PM, Entrada Libre."
    )
    if texto_anuncio:
        st.session_state.anuncios_pauta = texto_anuncio

# INTERFAZ PÚBLICA DEL CIUDADANO (Buscador Gratis)
st.subheader("🔍 Buscar Planes y Eventos para Salir")
ciudad = st.text_input("¿En qué ciudad te encuentras?", placeholder="Ej: Bogota, Medellin, Cali")

# Selección de rango de tiempo para el rastreador
rango_fecha = st.selectbox(
    "¿Para cuándo buscas plan?", 
    ["Este fin de semana", "Próximos 30 días (1 mes)", "Próximos 6 meses"]
)

tipo_acceso = st.selectbox("Filtro de costo:", ["AMBOS", "GRATIS", "DE PAGA"])

# FUNCIÓN INTERNA DE RASTREO Y LIMPIEZA AUTOMÁTICA
def rastrear_categoria(termino_busqueda, ciudad_nombre, filtro_tiempo):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    query = urllib.parse.quote(f"{termino_busqueda} en {ciudad_nombre} {filtro_tiempo}")
    url = f"https://html.duckduckgo.com/html/?q={query}"
    
    resultados_limpios = []
    try:
        response = requests.get(url, headers=headers, timeout=7)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            bloques = soup.find_all('div', class_='result__body')
            
            for b in bloques:
                enlace_tag = b.find('a', class_='result__url')
                snippet_tag = b.find('a', class_='result__snippet')
                
                if enlace_tag and snippet_tag:
                    titulo = enlace_tag.text.strip()
                    snippet = snippet_tag.text.strip()
                    
                    # Limpieza profunda de títulos basura de internet
                    nombre = titulo.split("|")[0].split("-")[0].replace("www.", "").replace(".com", "").replace(".co", "").strip()
                    nombre = re.sub(r'(Eventbrite|Boletas|Tickets|Compra|Descubre|Encuentra|Agenda)', '', nombre, flags=re.IGNORECASE).strip().title()
                    
                    # Intentar extraer un lugar físico real basado en palabras clave del texto descriptivo
                    lugar = f"Ubicación en {ciudad_nombre}"
                    palabras_lugar = ["Teatro", "Movistar Arena", "Estadio", "Coliseo", "Mall", "Centro Comercial", "Parque", "Auditorio", "Club", "Hall", "Plaza"]
                    for p in palabras_lugar:
                        match = re.search(r'(' + p + r'\s+[A-Za-z0-9áéíóúÁÉÍÓÚñÑ\s]+)', snippet, re.IGNORECASE)
                        if match:
                            lugar = match.group(1).split(".")[0].split(",")[0].strip().title()
                            break
                    
                    if len(nombre) > 10 and not any(r['nombre'] == nombre for r in resultados_limpios):
                        resultados_limpios.append({"nombre": nombre, "lugar": lugar})
    except Exception:
        pass
    return resultados_limpios

# BOTÓN DE EJECUCIÓN
if st.button("Buscar Cartelera Real"):
    if not ciudad:
        st.warning("Por favor, ingresa la ciudad para realizar la búsqueda.")
    else:
        ciudad_limpia = ciudad.strip().title()
        ciudad_normalizada = ciudad.lower().strip().replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
        
        # Ajuste de palabras clave según la temporalidad seleccionada
        if "1 mes" in rango_fecha:
            tiempo_busqueda = "este mes cartelera programacion 2026"
        elif "6 meses" in rango_fecha:
            tiempo_busqueda = "proximos meses eventos agenda 2026"
        else:
            tiempo_busqueda = "este fin de semana agenda"

        with st.spinner(f"Rastreando la red en vivo en {ciudad_limpia}..."):
            st.markdown("---")
            st.markdown(f"### 📍 Cartelera Cultural Encontrada para: {ciudad_limpia} ({rango_fecha})")
            
            # 1. INYECCIÓN PRIORITARIA DE TU ANUNCIO PAGO (Monetización)
            if st.session_state.anuncios_pauta != "Ninguno por ahora" and st.session_state.anuncios_pauta.strip() != "":
                st.markdown("### ⭐ ANUNCIOS DESTACADOS - RECOMENDADOS")
                st.info(st.session_state.anuncios_pauta)
                st.markdown("---")
            
            # --- SECCIÓN 1: CENTROS COMERCIALES (100% AUTOMÁTICO) ---
            st.markdown("### 🏢 1. PLANES EN CENTROS COMERCIALES")
            cc_encontrados = rastrear_categoria("eventos actividades feria centro comercial", ciudad_limpia, tiempo_busqueda)
            
            conteo_cc = 0
            for cc in cc_encontrados:
                st.write(f"• **Actividad:** {cc['nombre']}")
                st.write(f"  * **Lugar:** {cc['lugar']} ({ciudad_limpia})")
                st.caption(f"🔗 [Ver Horarios y Detalles de este Centro Comercial](https://www.google.com/search?q={urllib.parse.quote(cc['nombre'] + ' ' + ciudad_limpia)})")
                st.markdown(" ")
                conteo_cc += 1
                if conteo_cc >= 3: break
                
            if conteo_cc == 0:
                st.info(f"No se detectaron ferias comerciales masivas registradas en la red para esta fecha en {ciudad_limpia}.")

            # --- SECCIÓN 2: MASCOTAS Y PET-FRIENDLY (100% AUTOMÁTICO) ---
            st.markdown("### 🐾 2. MASCOTAS Y PET-FRIENDLY")
            mascotas_encontrados = rastrear_categoria("evento canino adopcion mascotas pet friendly", ciudad_limpia, tiempo_busqueda)
            
            conteo_pet = 0
            for pet in mascotas_encontrados:
                st.write(f"• **Plan Mascota:** {pet['nombre']}")
                st.write(f"  * **Lugar:** {pet['lugar']}")
                st.caption(f"🔗 [Consultar requisitos de asistencia con tu mascota](https://www.google.com/search?q={urllib.parse.quote(pet['nombre'] + ' ' + ciudad_limpia)})")
                st.markdown(" ")
                conteo_pet += 1
                if conteo_pet >= 3: break
                
            if conteo_pet == 0:
                st.write(f"• **Plan Recomendado:** Caminata y Recreación en los Parques Principales de {ciudad_limpia}.")
                st.caption(f"🐾 Zonas verdes habilitadas para ingreso libre con correa de forma permanente.")

            # --- SECCIÓN 3: CONCIERTOS, TEATRO Y RUMBA (100% AUTOMÁTICO) ---
            st.markdown("### 🎸 3. CONCIERTOS, TEATRO Y RUMBA")
            shows_encontrados = rastrear_categoria("site:eventbrite.com.co OR site:tuboleta.com OR site:eticket.co conciertos teatro festival", ciudad_limpia, tiempo_busqueda)
            
            conteo_show = 0
            for show in shows_encontrados:
                # Aplicar los filtros de costo seleccionados por el usuario
                if tipo_acceso == "GRATIS" and "gratis" not in show['nombre'].lower():
                    continue
                if tipo_acceso == "DE PAGA" and "gratis" in show['nombre'].lower():
                    continue
                    
                st.write(f"• **Espectáculo:** {show['nombre']}")
                st.write(f"  * **Lugar:** {show['lugar']}")
                st.caption(f"🔗 [Comprar Boletas y Verificar Fechas Oficiales](https://www.google.com/search?q={urllib.parse.quote(show['nombre'] + ' ' + show['lugar'])})")
                st.markdown(" ")
                conteo_show += 1
                if conteo_show >= 3: break
                
            if conteo_show == 0:
                st.info(f"No encontramos eventos específicos de boletería con el filtro '{tipo_acceso}' en este momento.")
            
            # SECCIÓN 4: CULTURA Y ARTE
            st.markdown("### 🎨 4. CULTURA, ARTE Y CIUDAD")
            st.write(f"• **Ruta de Museos y Casas de la Cultura Regional** | Lugar: Centros históricos de {ciudad_limpia} | Costo: Acceso público permanente.")
            
            st.markdown("---")
            st.caption(f"⚙️ Sistema Cazador de Eventos Autónomo. Datos indexados y filtrados de forma independiente.")
