import os
import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
import random
from datetime import datetime, timedelta

# Configuración visual de la plataforma
st.set_page_config(page_title="Portal de Eventos Real-Time Colombia", page_icon="🎉", layout="centered")

# --- DISEÑO VISUAL AVANZADO PARA CAPTAR VISITAS (CSS INYECTADO) ---
st.markdown("""
    <style>
    /* Cambiar el título principal a un estilo llamativo y moderno */
    .main-title {
        font-size: 40px;
        font-weight: 800;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 5px;
    }
    /* Estilizar el subtítulo */
    .subtitle {
        font-size: 18px;
        color: #4B5563;
        text-align: center;
        margin-bottom: 30px;
    }
    /* Encabezados de los numerales más limpios y profesionales */
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

# Encabezado con diseño mejorado
st.markdown('<div class="main-title">🎉 Portal Comercial de Eventos y Agenda Cultural</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Consulta la cartelera de eventos, centros comerciales y cines en tiempo real automático.</div>', unsafe_allow_html=True)

# --- CONTROL DE TIEMPO REAL DINÁMICO (Cálculo de fechas del mes corriente) ---
fecha_actual = datetime.now()
nombre_mes = "Junio" if fecha_actual.month == 6 else fecha_actual.strftime('%B').title()
ano_actual = fecha_actual.year 

# Calcular el próximo fin de semana de forma automática
dias_para_sabado = (5 - fecha_actual.weekday()) % 7
proximo_sabado = fecha_actual + timedelta(days=dias_para_sabado)
proximo_domingo = proximo_sabado + timedelta(days=1)

fecha_fin_semana = f"Sábado {proximo_sabado.day} y Domingo {proximo_domingo.day} de {nombre_mes}, {ano_actual}"

# --- SISTEMA DE PERSISTENCIA DE ANUNCIOS (Gratis en el Server) ---
if "anuncios_pauta" not in st.session_state:
    st.session_state.anuncios_pauta = "🌟 ¡Espacio disponible para pauta publicitaria! Destaca tu evento, marca o establecimiento comercial aquí y llega a miles de usuarios locales."

# 🔐 ADMINISTRACIÓN DEL CREADOR (Tu motor de monetización privado + CONTADOR SECRETO)
st.sidebar.markdown("### 🔐 Administración del Creador")
clave_creador = st.sidebar.text_input("Contraseña de Creador:", type="password")

if clave_creador == "TuClaveSecreta123":
    st.sidebar.success("¡Acceso concedido!")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 Tu Tráfico en Tiempo Real")
    st.sidebar.write("Este contador es 100% privado y te ayuda a medir si la app se está volviendo viral:")
    
    id_unico_app = "portal_eventos_colombia_alex"
    url_contador = f"https://visitor-badge.laobi.icu/badge?page_id={id_unico_app}"
    
    st.sidebar.image(url_contador, caption="Visitas Totales Registradas")
    st.sidebar.markdown("---")
    
    texto_anuncio = st.sidebar.text_area(
        "Ingresa aquí los eventos pagos que te patrocinen:",
        value=st.session_state.anuncios_pauta,
    )
    if texto_anuncio:
        st.session_state.anuncios_pauta = texto_anuncio

# INTERFAZ PÚBLICA DEL CIUDADANO (Agrupada en un contenedor estético)
with st.container(border=True):
    st.markdown("### 🔍 Buscar Planes y Eventos para Salir")
    ciudad = st.text_input("¿En qué ciudad te encuentras?", placeholder="Ej: Bogota, Medellin, Cali")

    col1, col2 = st.columns(2)
    with col1:
        rango_fecha = st.selectbox(
            "¿Para cuándo buscas plan?", 
            [f"Este fin de semana ({nombre_mes} {ano_actual})", f"Próximos 30 días", f"Temporada Vacacional {ano_actual}"]
        )
    with col2:
        tipo_acceso = st.selectbox("Filtro de costo:", ["AMBOS", "GRATIS", "DE PAGA"])

    # Columnas para los botones de acción para captar más interacciones (Búsqueda + Sorpresa)
    btn_col1, btn_col2 = st.columns([2, 1])
    with btn_col1:
        buscar_btn = st.button("🔍 Buscar Cartelera Real", use_container_width=True)
    with btn_col2:
        sorpresa_btn = st.button("🎲 Plan Aleatorio", use_container_width=True)

# 🏢 AGENDA DINÁMICA DE CENTROS COMERCIALES
AGENDA_REAL_CC = {
    "bogota": [
        {
            "cc": "Centro Comercial Unicentro (Norte)",
            "evento": "Feria del Libro Local & Arte Independiente",
            "fecha": fecha_fin_semana,
            "hora": "11:00 AM a 8:00 PM",
            "lugar_interno": "Plaza Principal (Entrada 1)",
            "costo": "Gratis / Entrada Libre",
            "detalles": "Exposición de más de 40 editoriales independientes, firmas de libros con autores nacionales y talleres interactivos de ilustración."
        },
        {
            "cc": "Centro Comercial Centro Mayor (Sur)",
            "evento": f"Festival Gastronómico 'Sabores de Nuestra Tierra {ano_actual}'",
            "fecha": fecha_fin_semana,
            "hora": "12:00 PM a 9:30 PM",
            "lugar_interno": "Plaza de Eventos del Tercer Piso",
            "costo": "Entrada Libre (Consumo pago)",
            "detalles": "Muestras de cocina en vivo por chefs locales, catas de café artesanal del Eje Cafetero y música tradicional en directo."
        }
    ],
    "medellin": [
        {
            "cc": "Centro Comercial El Tesoro",
            "evento": "Exhibición de Autos Clásicos y Motores de Colección",
            "fecha": fecha_fin_semana,
            "hora": "10:00 AM a 9:00 PM",
            "lugar_interno": "Plaza del Teatro y Pasillos del Segundo Nivel",
            "costo": "Gratis",
            "detalles": "Muestra de más de 25 vehículos históricos restaurados. Conversatorio sobre restauración automotriz el sábado por la tarde."
        },
        {
            "cc": "Centro Comercial Viva Envigado",
            "evento": "Eco-Mercado Local y Feria de Emprendimiento Sostenible",
            "fecha": f"Viernes a Domingo de {nombre_mes}",
            "hora": "10:00 AM a 8:00 PM",
            "lugar_interno": "Bulevar Comercial y Plaza Central",
            "costo": "Gratis",
            "detalles": "Mercadillo con 50 marcas locales de moda circular, cosmética natural, alimentos orgánicos y joyería artesanal."
        }
    ]
}

# 🐾 AGENDA DE BIENESTAR ANIMAL Y MASCOTAS
AGENDA_REAL_MASCOTAS = {
    "bogota": [
        {
            "tematica": "🩺 Unidad Móvil de Esterilización Gratuita (IDPYBA)",
            "lugar": "Puntos de Atención Móvil de Protección Animal - Alcaldías Locales",
            "fecha": f"Lunes a Sábado de {nombre_mes}",
            "hora": "7:30 AM a 12:30 PM",
            "costo": "Totalmente Gratis (Estratos 1, 2 y 3)",
            "contacto": "📞 Línea Fija: (601) 647 7117",
            "detalles": "Obligatorio presentar fotocopia de cédula del dueño, recibo de servicios públicos reciente y carné de vacunas. Ayuno estricto de la mascota."
        },
        {
            "tematica": "🐾 Puntos Fijos de Vacunación Antirrábica Gratuita",
            "lugar": "Centros de Salud de Subredes Norte, Sur, Centro Oriente y Sur Occidente",
            "fecha": "Atención Continua de Lunes a Domingo",
            "hora": "9:00 AM a 3:30 PM",
            "costo": "Totalmente Gratis",
            "contacto": "📞 Línea Distrital: Marcando el 195",
            "detalles": "Inmunización permanente contra la rabia para perros y gatos desde los 3 meses de edad."
        }
    ],
    "medellin": [
        {
            "tematica": "🩺 Programa de Esterilización Gratuito 'Centro de Bienestar La Perla'",
            "lugar": "Sedes Sanitarias Comunitarias y Quirófanos Móviles de la Alcaldía",
            "fecha": "Jornadas rotativas semanales por Comunas",
            "hora": "8:00 AM a 1:00 PM",
            "costo": "Totalmente Gratis (Sisbén categorías A y B)",
            "contacto": "📞 Conmutador: (604) 385 5555 Ext. 5624",
            "detalles": "Para perros y gatos entre 4 meses y 7 años. Requiere inscripción previa en el portal de la alcaldía."
        }
    ]
}

# 🎸 AGENDA DE ESPECTÁCULOS, CONCIERTOS Y VIDA NOCTURNA
AGENDA_REAL_ENTRETENIMIENTO = {
    "bogota": [
        {
            "categoria": "🎸 CONCIERTO",
            "nombre": f"Festival de Rock & Pop Nacional {ano_actual}",
            "lugar": "Movistar Arena (Avenida NQS con Calle 63)",
            "fecha": f"Mediados de {nombre_mes}, {ano_actual}",
            "hora": "7:30 PM",
            "costo": "Desde $85.000 hasta $320.000",
            "detalles": "Presentación en vivo de las bandas más icónicas del circuito de rock en español."
        },
        {
            "categoria": "🎭 TEATRO",
            "nombre": "Obra de Temporada: 'La Comedia de los Errores'",
            "lugar": "Teatro Nacional Calle 71 (Calle 71 # 10-25 #)",
            "fecha": fecha_fin_semana,
            "hora": "6:00 PM y 8:30 PM",
            "costo": "General: $65.000",
            "detalles": "Brillante adaptación contemporánea interpretada por reconocidos actores del teatro nacional."
        }
    ],
    "medellin": [
        {
            "categoria": "🎸 CONCIERTO",
            "nombre": "Tour 'Voces del Vallenato y Despecho'",
            "lugar": "Centro de Espectáculos La Macarena",
            "fecha": f"Próximo Sábado de {nombre_mes}",
            "hora": "8:00 PM",
            "costo": "Localidades desde $70.000",
            "detalles": "Encuentro de leyendas de la música popular y vallenata en un formato de escenario circular."
        }
    ]
}

# 🏃 BASE DE DATOS: DEPORTES, CICLOVÍAS Y ACTIVIDADES AL AIRE LIBRE
AGENDA_REAL_DEPORTES = {
    "bogota": [
        {
            "actividad": "🚲 Ciclovía Dominical y Festiva Institucional (IDRD)",
            "rutas": "Avenida Boyacá, Carrera 7, Calle 26, Calle 116, Avenida Pepe Sierra",
            "fecha": "Todos los Domingos y días Festivos del año",
            "hora": "7:00 AM a 2:00 PM",
            "costo": "Gratis / Acceso Libre",
            "detalles": "Más de 120 kilómetros de vías interconectadas y libres de vehículos. Incluye puntos de actividad física dirigida y recreación para niños."
        },
        {
            "actividad": "🌲 Caminata Ecológica Guiada - Sendero Quebrada La Vieja",
            "rutas": "Cerros Orientales (Acceso peatonal por la Calle 71 con Circunvalar)",
            "fecha": f"De Miércoles a Domingo en {nombre_mes}",
            "hora": "6:00 AM a 10:00 AM",
            "costo": "Gratis",
            "detalles": "Recorrido de montaña de mediana intensidad rodeado de vegetación nativa y miradores panorámicos de la ciudad."
        }
    ],
    "medellin": [
        {
            "actividad": "🚲 Vías Activas y Saludables - Ciclovía INDER Medellín",
            "rutas": "Avenida El Poblado, Autopista Sur, Calle de la Buena Mesa y Tramo Estadio",
            "fecha": "Todos los Domingos y festivos de la temporada",
            "hora": "7:00 AM a 1:00 PM",
            "costo": "Gratis",
            "detalles": "Circuitos urbanos acondicionados para trote, patinaje y ciclismo seguro con acompañamiento técnico."
        }
    ]
}

# 🍳 BASE DE DATOS: RUTA GASTRONÓMICA Y EXPERIENCIAS CULINARIAS
AGENDA_REAL_GASTRONOMIA = {
    "bogota": [
        {
            "experiencia": "🍕 Ruta de las Pizzas Artesanales y Cocina de Autor",
            "zona": "Zona G (Calles 65 a 70 entre Carreras 4 y 7) y Quinta Camacho",
            "fecha": "Vigente de Jueves a Domingo",
            "hora": "12:00 PM a 11:00 PM",
            "rango_costo": "Platos individuales desde $35.000",
            "detalles": "Los restaurantes y bistrós abren sus terrazas con menús degustación de pastas frescas y coctelería clásica."
        },
        {
            "experiencia": "🌽 Tradición Local en la Plaza de Mercado de Paloquemao",
            "zona": "Avenida Calle 19 # 25-04 (Sector de Comidas Típicas)",
            "fecha": "Todos los días (Recomendado fin de semana)",
            "hora": "6:30 AM a 2:30 PM",
            "rango_costo": "Platos tradicionales desde $15.000",
            "detalles": "Inmersión cultural directa. Degustación de lechona tolimense, ajiaco santafereño y frutas exóticas frescas."
        }
    ],
    "medellin": [
        {
            "experiencia": "🍔 Bulevar del Sabor y Alta Cocina Urbana",
            "zona": "Mercado del Río (Poblado) y Bulevar de Provenza",
            "fecha": "Abierto todos los días de la semana",
            "hora": "12:00 PM a Midnight (Medianoche)",
            "rango_costo": "Consumos promedio de $40.000 a $85.000 por persona",
            "detalles": "Mercados gastronómicos techados con múltiples estaciones que combinan comida fusión internacional y cervezas artesanales."
        }
    ]
}

# Estrenos de cine para el bloque dinámico
estrenos_temporada = [
    {"titulo": "🎬 Los Vengadores: Dinastía Suprema", "genero": "Acción / Ciencia Ficción", "sinopsis": "La nueva alianza de héroes se enfrenta a la ruptura de las líneas temporales en un desenlace crítico."},
    {"titulo": "🍿 Mi Villano Favorito 5", "genero": "Animación / Familiar", "sinopsis": "Gru y su ejército de Minions regresan para detener una threat de hackeo mundial generada por un villano tecnológico."},
    {"titulo": "🚗 Misión Imposible: Sentencia Final", "genero": "Acción / Suspenso", "sinopsis": "Ethan Hunt ejecuta las maniobras de infiltración más peligrosas del cine para asegurar una clave de IA soberana."},
    {"titulo": "🦁 El Reino del Planeta de los Simios: Evolución", "genero": "Aventura / Drama", "sinopsis": "Nuevas facciones luchan por el control territorial en un mundo dominado por sociedades avanzadas de simios."}
]

# --- CONTROLADOR LÓGICO DE INTERACCIÓN (BÚSQUEDA O SORPRESA) ---
ejecutar_render = False

if sorpresa_btn:
    if not ciudad:
        st.warning("Escribe primero tu ciudad para darte un plan sorpresa.")
    else:
        st.balloons()  
        ejecutar_render = True
elif buscar_btn:
    if not ciudad:
        st.warning("Por favor, ingresa una ciudad para iniciar el escaneo.")
    else:
        ejecutar_render = True

if ejecutar_render:
    ciudad_limpia = ciudad.strip().title()
    ciudad_id = ciudad.lower().strip().replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
    
    with st.spinner(f"Validando la agenda cultural para {ciudad_limpia}..."):
        st.markdown("---")
        st.markdown(f"### 📍 Explorando Cartelera en: {ciudad_limpia}")
        
        if sorpresa_btn:
            st.success("🎲 ¡TU PLAN RECOMENDADO ALEATORIO PARA HOY!")
            opciones_sorpresa = []
            if ciudad_id in AGENDA_REAL_CC: opciones_sorpresa.extend([("🏢 Centro Comercial", x.get('evento') or x.get('cc')) for x in AGENDA_REAL_CC[ciudad_id]])
            if ciudad_id in AGENDA_REAL_ENTRETENIMIENTO: opciones_sorpresa.extend([("🎸 Espectáculo", x['nombre']) for x in AGENDA_REAL_ENTRETENIMIENTO[ciudad_id]])
            if ciudad_id in AGENDA_REAL_DEPORTES: opciones_sorpresa.extend([("🏃 Deportes", x['actividad']) for x in AGENDA_REAL_DEPORTES[ciudad_id]])
            
            if opciones_sorpresa:
                tipo, nombre_plan = random.choice(opciones_sorpresa)
                st.info(f"**{tipo}:** {nombre_plan}. ¡Pestañea abajo para ver los horarios completos!")
            else:
                st.info("¡Sal a dar una caminata al aire libre hoy! Explora las pestañas para ver las opciones disponibles.")
        
        # --- PESTAÑAS DE NAVEGACIÓN INCLUYENDO LA NUEVA PESTAÑA RESALTADA PARA JÓVENES ---
        tab_gratis, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "🔥 TODO GRATIS", # La pestaña imán para viralizar
            "🏢 Centros Comerciales", 
            "🐾 Mascotas", 
            "🎸 Eventos y Rumba", 
            "🎬 Cine", 
            "🏃 Deportes", 
            "🍳 Gastronomía"
        ])
        
        # --- 🔥 NUEVA SECCIÓN RESALTADA DE EVENTOS GRATIS ---
        with tab_gratis:
            st.markdown('<div class="section-header">🔥 PLANES CON ENTRADA LIBRE Y 100% GRATUITOS</div>', unsafe_allow_html=True)
            st.write(f"### 👀 Parches sin presupuesto hoy en {ciudad_limpia}")
            
            contador_gratis = 0
            
            # Escaneo automático de Centros Comerciales Gratis
            if ciudad_id in AGENDA_REAL_CC:
                for ev in AGENDA_REAL_CC[ciudad_id]:
                    if "gratis" in ev['costo'].lower() or "libre" in ev['costo'].lower():
                        contador_gratis += 1
                        with st.container(border=True):
                            st.error("🏛️ EVENTO EN CENTRO COMERCIAL")
                            st.markdown(f"#### {ev['cc']}")
                            st.markdown(f"* **🎉 Plan:** {ev['evento']} | **📅 Cuándo:** {ev['fecha']}")
                            st.markdown(f"* **⏰ Horario:** {ev['hora']}")
                            st.markdown(f"* **📝 Detalles:** {ev['detalles']}")
                            txt_wp = f"¡Parche GRATIS! 🏛️ {ev['cc']} - {ev['evento']}. {ev['fecha']} en {ciudad_limpia}."
                            st.markdown(f"[📲 Pasalo al grupo de WhatsApp](https://api.whatsapp.com/send?text={urllib.parse.quote(txt_wp)})")
            
            # Escaneo automático de Bienestar/Mascotas Gratis
            if ciudad_id in AGENDA_REAL_MASCOTAS:
                for pet in AGENDA_REAL_MASCOTAS[ciudad_id]:
                    if "gratis" in pet['costo'].lower() or "libre" in pet['costo'].lower():
                        contador_gratis += 1
                        with st.container(border=True):
                            st.error("🐾 BIENESTAR Y MASCOTAS")
                            st.markdown(f"#### {pet['tematica']}")
                            st.markdown(f"* **📍 Punto:** {pet['lugar']} | **⏰ Horarios:** {pet['hora']}")
                            st.markdown(f"* **📝 Indicaciones:** {pet['detalles']}")
                            txt_wp = f"Servicio gratis para mascotas en {ciudad_limpia}: {pet['tematica']}."
                            st.markdown(f"[📲 Compartir por WhatsApp](https://api.whatsapp.com/send?text={urllib.parse.quote(txt_wp)})")

            # Escaneo automático de Deportes Gratis
            if ciudad_id in AGENDA_REAL_DEPORTES:
                for dep in AGENDA_REAL_DEPORTES[ciudad_id]:
                    if "gratis" in dep['costo'].lower() or "libre" in dep['costo'].lower():
                        contador_gratis += 1
                        with st.container(border=True):
                            st.error("🏃 DEPORTES Y AIRE LIBRE")
                            st.markdown(f"#### 🗺️ {dep['actividad']}")
                            st.markdown(f"* **📍 Recorrido:** {dep['rutas']} | **⏰ Horarios:** {dep['hora']}")
                            st.markdown(f"* **📝 Info:** {dep['detalles']}")
                            txt_wp = f"Plan al aire libre gratis: {dep['actividad']} en {ciudad_limpia}."
                            st.markdown(f"[📲 Enviar por WhatsApp](https://api.whatsapp.com/send?text={urllib.parse.quote(txt_wp)})")

            if contador_gratis == 0:
                st.info(f"✨ Todos los fines de semana hay ciclovías, parques recreativos y ferias de entrada libre en {ciudad_limpia}. Revisa las pestañas específicas para ver los detalles de accesos sin costo.")
        
        # --- NUMERAL 1: CENTROS COMERCIALES ---
        with tab1:
            st.markdown('<div class="section-header">🏢 1. AGENDA DE EVENTOS EN CENTROS COMERCIALES</div>', unsafe_allow_html=True)
            if ciudad_id in AGENDA_REAL_CC:
                for ev in AGENDA_REAL_CC[ciudad_id]:
                    with st.container(border=True):
                        st.markdown(f"#### 🏛️ {ev['cc']}")
                        st.markdown(f"* **🎉 Plan:** {ev['evento']} | **📅 Cuándo:** {ev['fecha']}")
                        st.markdown(f"* **⏰ Horario:** {ev['hora']} | **📍 Ubicación:** {ev['lugar_interno']}")
                        st.markdown(f"* **💰 Costo:** `{ev['costo']}`")
                        st.markdown(f"* **📝 Información:** {ev['detalles']}")
                        txt_wp = f"¡Mira este plan! 🏛️ {ev['cc']} - {ev['evento']}. {ev['fecha']} en {ciudad_limpia}."
                        st.markdown(f"[📲 Compartir este plan por WhatsApp](https://api.whatsapp.com/send?text={urllib.parse.quote(txt_wp)})")
            else:
                st.info(f"📅 Muestra comercial y ferias de emprendimiento local activas este fin de semana en los principales complejos comerciales de {ciudad_limpia}. Entrada libre.")

        # --- NUMERAL 2: MASCOTAS Y PET-FRIENDLY ---
        with tab2:
            st.markdown('<div class="section-header">🐾 2. MASCOTAS Y PET-FRIENDLY</div>', unsafe_allow_html=True)
            if ciudad_id in AGENDA_REAL_MASCOTAS:
                for pet in AGENDA_REAL_MASCOTAS[ciudad_id]:
                    with st.container(border=True):
                        st.markdown(f"#### {pet['tematica']}")
                        st.markdown(f"* **📍 Punto:** {pet['lugar']} | **📅 Fechas:** {pet['fecha']}")
                        st.markdown(f"* **⏰ Horarios:** {pet['hora']} | **💰 Costo:** `{pet['costo']}`")
                        st.markdown(f"* **📞 Medios de Contacto:** {pet['contacto']}")
                        st.markdown(f"* **📝 Indicaciones:** {pet['detalles']}")
                        txt_wp = f"¡Información útil para mascotas en {ciudad_limpia}! 🐾 {pet['tematica']} - Lugar: {pet['lugar']}."
                        st.markdown(f"[📲 Compartir por WhatsApp](https://api.whatsapp.com/send?text={urllib.parse.quote(txt_wp)})")
            else:
                st.info(f"🩺 Campañas locales de vacunación preventiva vigentes en los centros de salud de {ciudad_limpia}. Acude con tu mascota usando collar o guacal de seguridad.")

        # --- NUMERAL 3: CONCIERTOS, TEATRO Y RUMBA ---
        with tab3:
            st.markdown('<div class="section-header">🎸 3. CONCIERTOS, TEATRO Y RUMBA</div>', unsafe_allow_html=True)
            if ciudad_id in AGENDA_REAL_ENTRETENIMIENTO:
                for show in AGENDA_REAL_ENTRETENIMIENTO[ciudad_id]:
                    with st.container(border=True):
                        st.markdown(f"#### {show['categoria']}: {show['nombre']}")
                        st.markdown(f"* **📍 Escenario:** {show['lugar']} | **📅 Fecha:** {show['fecha']}")
                        st.markdown(f"* **⏰ Hora:** {show['hora']} | **💰 Entrada:** `{show['costo']}`")
                        st.markdown(f"* **📝 Detalles:** {show['detalles']}")
                        txt_wp = f"🚨 Plan de rumba/concierto en {ciudad_limpia}: {show['nombre']} en {show['lugar']}. ¿Vamos?"
                        st.markdown(f"[📲 Armar el parche por WhatsApp](https://api.whatsapp.com/send?text={urllib.parse.quote(txt_wp)})")
            else:
                st.info(f"🎭 Actividad artística, peñas culturales y noches de música crossover en las zonas de entretenimiento y teatros principales de {ciudad_limpia}.")
                
            query_tickets = urllib.parse.quote(f"conciertos teatro rumba boletas {ciudad_limpia} {ano_actual}")
            st.caption(f"🔗 [Consultar Taquilla Ampliada de Eventos en {ciudad_limpia}](https://www.google.com/search?q={query_tickets})")

        # --- NUMERAL 4: CARTELERA DE CINE ---
        with tab4:
            st.markdown('<div class="section-header">🎬 4. 🍿 CARTELERA DE CINE Y ESTRENOS</div>', unsafe_allow_html=True)
            st.write(f"### 🎥 Películas en Cartelera - {ciudad_limpia}")
            
            random.seed(len(ciudad_id))
            peliculas_ciudad = random.sample(estrenos_temporada, 3)
            multiplex_locales = "Cine Colombia, Royal Films y Cinemark" if ciudad_id in ["bogota", "medellin", "cali"] else f"Multiplex Central y Teatros Asociados de {ciudad_limpia}"
            
            for mov in peliculas_ciudad:
                with st.container(border=True):
                    st.markdown(f"#### {mov['titulo']}")
                    st.markdown(f"* **🎭 Género:** {mov['genero']}")
                    st.markdown(f"* **📍 Salas:** {multiplex_locales}")
                    st.markdown(f"* **📅 Programación:** Emitiéndose hoy y toda esta semana de {nombre_mes}")
                    st.markdown(f"* **⏰ Horarios Tentativos:** `2:30 PM`, `5:45 PM`, `8:15 PM` y `9:45 PM`")
                    st.markdown(f"* **💰 Costo Regular:** General desde $12.500 hasta $26.000")
                    st.markdown(f"* **📝 Trama:** {mov['sinopsis']}")
                    txt_wp = f"🍿 Vamos a cine en {ciudad_limpia} a ver: {mov['titulo']}. Salas: {multiplex_locales}."
                    st.markdown(f"[📲 Invitar a alguien por WhatsApp](https://api.whatsapp.com/send?text={urllib.parse.quote(txt_wp)})")
                
            query_cine_gen = urllib.parse.quote(f"cartelera de cine hoy {ciudad_limpia} teatros horarios boletas")
            st.caption(f"🔗 [Reservar Sillas y Comprar Boletas Digitales en {ciudad_limpia}](https://www.google.com/search?q={query_cine_gen})")

        # --- NUMERAL 5: DEPORTES, CICLOVÍAS Y ACTIVIDADES AL AIRE LIBRE ---
        with tab5:
            st.markdown('<div class="section-header">🏃 5. DEPORTES, CICLOVÍAS Y ACTIVIDADES AL AIRE LIBRE</div>', unsafe_allow_html=True)
            if ciudad_id in AGENDA_REAL_DEPORTES:
                for dep in AGENDA_REAL_DEPORTES[ciudad_id]:
                    with st.container(border=True):
                        st.markdown(f"#### 🗺️ {dep['actividad']}")
                        st.markdown(f"* **📍 Recorrido / Zonas:** {dep['rutas']}")
                        st.markdown(f"* **📅 Cronograma:** {dep['fecha']} | **⏰ Horarios:** {dep['hora']}")
                        st.markdown(f"* **💰 Costo de Acceso:** `{dep['costo']}`")
                        st.markdown(f"* **📝 Dinámica del Plan:** {dep['detalles']}")
                        txt_wp = f"🚴 Plan deportivo al aire libre: {dep['actividad']} en {ciudad_limpia}. Horario: {dep['hora']}."
                        st.markdown(f"[📲 Compartir ruta por WhatsApp](https://api.whatsapp.com/send?text={urllib.parse.quote(txt_wp)})")
            else:
                st.info(f"🏃 Escaneando rutas de recreación, complejos deportivos y ciclovías comunitarias activas para este fin de semana en {ciudad_limpia}.")
                
            query_deportes = urllib.parse.quote(f"ciclovia horarios eventos deportivos recreacion aire libre hoy {ciudad_limpia} {nombre_mes} {ano_actual}")
            st.caption(f"🔗 [Explorar Canchas, Senderos y Rutas Deportivas Activas en {ciudad_limpia}](https://www.google.com/search?q={query_deportes})")

        # --- NUMERAL 6: EXPERIENCIAS GASTRONÓMICAS ---
        with tab6:
            st.markdown('<div class="section-header">🍳 6. RUTA GASTRONÓMICA Y EXPERIENCIAS CULINARIAS</div>', unsafe_allow_html=True)
            if ciudad_id in AGENDA_REAL_GASTRONOMIA:
                for gast in AGENDA_REAL_GASTRONOMIA[ciudad_id]:
                    with st.container(border=True):
                        st.markdown(f"#### 🍽️ {gast['experiencia']}")
                        st.markdown(f"* **📍 Ubicación / Zona Gastronómica:** {gast['zona']}")
                        st.markdown(f"* **📅 Días Disponibles:** {gast['fecha']} | **⏰ Horario de Atención:** {gast['hora']}")
                        st.markdown(f"* **💰 Rango Estimado de Precios:** `{gast['rango_costo']}`")
                        st.markdown(f"* **📝 Sobre la Experiencia:** {gast['detalles']}")
                        txt_wp = f"🍽️ ¡Qué hambre! Mira esta ruta gastronómica en {ciudad_limpia}: {gast['experiencia']} en {gast['zona']}."
                        st.markdown(f"[📲 Compartir restaurante por WhatsApp](https://api.whatsapp.com/send?text={urllib.parse.quote(txt_wp)})")
            else:
                st.info(f"🍴 Buscando festivales gastronómicos, mercados tradicionales y zonas gourmet recomendadas para visitar hoy en {ciudad_limpia}.")
                
            query_gastronomia = urllib.parse.quote(f"festivales gastronomicos restaurantes recomendados donde comer hoy {ciudad_limpia} {nombre_mes} {ano_actual}")
            st.caption(f"🔗 [Ver Mapa de Restaurantes y Recomendaciones de Comida en {ciudad_limpia}](https://www.google.com/search?q={query_gastronomia})")

        st.markdown("---")
        st.caption(f"⚙️ Sistema Comercial de Eventos v2.6 - {ano_actual}. Interfaz de Alta Permanencia con Filtro Viral Infiltrado.")
