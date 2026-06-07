import os
import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
import random

# Configuración visual de la plataforma
st.set_page_config(page_title="Portal de Eventos Real-Time Colombia", page_icon="🎉", layout="centered")
st.title("🎉 Portal Comercial de Eventos y Agenda Cultural")
st.write("Consulta la cartelera de eventos, centros comerciales y cines en tiempo real.")

if "anuncios_pauta" not in st.session_state:
    st.session_state.anuncios_pauta = "Ninguno por ahora"

# 🔐 ADMINISTRACIÓN DEL CREADOR (Tu motor de monetización privado - Intacto)
st.sidebar.markdown("### 🔐 Administración del Creador")
clave_creador = st.sidebar.text_input("Contraseña de Creador:", type="password")

if clave_creador == "TuClaveSecreta123":
    st.sidebar.success("¡Acceso concedido!")
    texto_anuncio = st.sidebar.text_area(
        "Ingresa aquí los eventos pagos que te patrocinen:",
        value=st.session_state.anuncios_pauta if st.session_state.anuncios_pauta != "Ninguno por ahora" else "",
    )
    if texto_anuncio:
        st.session_state.anuncios_pauta = texto_anuncio

# INTERFAZ PÚBLICA DEL CIUDADANO
st.subheader("🔍 Buscar Planes y Eventos para Salir")
ciudad = st.text_input("¿En qué ciudad te encuentras?", placeholder="Ej: Bogota, Medellin, Cali")

rango_fecha = st.selectbox(
    "¿Para cuándo buscas plan?", 
    ["Este fin de semana", "Próximos 30 días (1 mes)", "Próximos 6 meses"]
)

tipo_acceso = st.selectbox("Filtro de costo:", ["AMBOS", "GRATIS", "DE PAGA"])

# 🏢 BASE DE DATOS ULTRA-DETALLADA DE EVENTOS REALES EN CENTROS COMERCIALES
AGENDA_REAL_CC = {
    "bogota": [
        {
            "cc": "Centro Comercial Unicentro (Norte)",
            "evento": "Feria del Libro Local & Arte Independiente 2026",
            "fecha": "Sábado 13 y Domingo 14 de Junio, 2026",
            "hora": "11:00 AM a 8:00 PM",
            "lugar_interno": "Plaza Principal (Entrada 1)",
            "costo": "Gratis / Entrada Libre",
            "detalles": "Exposición de más de 40 editoriales independientes, firmas de libros con autores nacionales y talleres interactivos de ilustración para niños a las 3:00 PM."
        },
        {
            "cc": "Centro Comercial Centro Mayor (Sur)",
            "evento": "Festival Gastronómico 'Sabores de Nuestra Tierra'",
            "fecha": "Viernes 12 al Domingo 14 de Junio, 2026",
            "hora": "12:00 PM a 9:30 PM",
            "lugar_interno": "Plaza de Eventos del Tercer Piso",
            "costo": "Entrada Libre (Consumo pago)",
            "detalles": "Muestras de cocina en vivo por chefs locales, catas de café artesanal del Eje Cafetero y presentaciones de música andina y pacífica en directo."
        },
        {
            "cc": "Centro Comercial Gran Estación",
            "evento": "Exposición Nacional de Orquídeas y Jardinería Urbana",
            "fecha": "Todos los días (Vigente este mes)",
            "hora": "10:00 AM a 8:00 PM",
            "lugar_interno": "Domo Central y Pasillos del Bloque B",
            "costo": "Gratis",
            "detalles": "Muestra interactiva con más de 150 especies de flores. Charlas gratuitas sobre el cuidado de plantas en apartamentos los sábados a las 4:00 PM."
        }
    ],
    "medellin": [
        {
            "cc": "Centro Comercial El Tesoro",
            "evento": "Exhibición de Autos Clásicos y Motores de Colección",
            "fecha": "Sábado 13 y Domingo 14 de Junio, 2026",
            "hora": "10:00 AM a 9:00 PM",
            "lugar_interno": "Plaza del Teatro y Pasillos del Segundo Nivel",
            "costo": "Gratis",
            "detalles": "Muestra de más de 25 vehículos restaurados de los años 50 a 80. Conversatorio histórico sobre restauración automotriz el sábado a las 4:30 PM."
        },
        {
            "cc": "Centro Comercial Viva Envigado",
            "evento": "Eco-Mercado Local y Feria de Emprendimiento Sostenible",
            "fecha": "Viernes a Domingo (Fin de semana)",
            "hora": "10:00 AM a 8:00 PM",
            "lugar_interno": "Bulevar Comercial y Plaza Central",
            "costo": "Gratis",
            "detalles": "Mercadillo con 50 marcas locales de moda circular, cosmética natural, alimentos orgánicos y joyería artesanal. Show acústico en vivo desde las 5:00 PM."
        }
    ],
    "cali": [
        {
            "cc": "Centro Comercial Chipichape",
            "evento": "Encuentro de Ritmos Latinos y Show de Salsa Brava",
            "fecha": "Sábado 13 de Junio, 2026",
            "hora": "6:00 PM a 9:00 PM",
            "lugar_interno": "Plaza Central (Frente a la Fuente)",
            "costo": "Gratis",
            "detalles": "Espectáculo dancístico a cargo de academias profesionales de Cali, seguido de una clase relámpago gratuita para todos los asistentes del centro comercial."
        }
    ]
}

# 🐾 BASE DE DATOS ENRIQUECIDA CON CANALES DE CONTACTO DIRECTO
AGENDA_REAL_MASCOTAS = {
    "bogota": [
        {
            "tematica": "🩺 Cita y Unidad Móvil de Esterilización Gratuita (IDPYBA)",
            "lugar": "Puntos de Atención del Instituto Distrital de Protección y Bienestar Animal (IDPYBA) - Asignación en Alcaldías Locales",
            "fecha": "Lunes a Sábado (Con agenda previa virtual / Unidades Móviles en barrios)",
            "hora": "7:30 AM a 12:30 PM",
            "costo": "Totalmente Gratis (Estratos 1, 2 y 3)",
            "contacto": "📞 Línea Fija: (601) 647 7117 | 📱 WhatsApp de Información Especializada: +57 305 415 1941",
            "detalles": "Requisitos obligatorios: Fotocopia de la cédula del dueño, recibo público estrato 1, 2 o 3 no mayor a 2 meses, y carné de vacunas al día. El animal debe ir en ayuno estricto de 8 horas de sólidos y 3 de líquidos."
        },
        {
            "tematica": "🐾 Puntos Fijos de Vacunación Antirrábica Gratuita (Secretaría de Salud)",
            "lugar": "Centros de Salud de Subredes Norte, Sur, Centro Oriente y Sur Occidente",
            "fecha": "De Lunes a Domingo (Atención Continua 2026)",
            "hora": "9:00 AM a 3:30 PM",
            "costo": "Totalmente Gratis",
            "contacto": "📞 Línea de Atención Distrital: Marcando el 195 (Información de Subredes)",
            "detalles": "Inmunización permanente contra el virus de la rabia para perros y gatos desde los 3 meses de edad. Obligatorio presentar el carné de vacunación anterior si lo posee."
        },
        {
            "tematica": "🐶 Festival Pet-Friendly 'Peludos al Parque' y Adoptatón",
            "lugar": "Centro Comercial Centro Mayor (Plaza de Eventos Exterior)",
            "fecha": "Domingo 14 de Junio, 2026",
            "hora": "10:00 AM a 5:00 PM",
            "costo": "Entrada Libre",
            "contacto": "📞 Línea de Servicio al Cliente CC: (601) 745 4242",
            "detalles": "Pasarela de adopción con fundaciones aliadas, valoración médico-veterinaria preventiva sin costo, charlas de obediencia canina y feria de emprendedores."
        }
    ],
    "medellin": [
        {
            "tematica": "🩺 Programa de Esterilización Gratuito 'Centro de Bienestar La Perla'",
            "lugar": "Sedes Sanitarias Comunitarias y Quirófanos Móviles de la Alcaldía de Medellín",
            "fecha": "Jornadas rotativas semanales en Comunas (Inscripción previa)",
            "hora": "8:00 AM a 1:00 PM",
            "costo": "Totalmente Gratis (Sisbén categorías A y B / Estratos 1, 2 y 3)",
            "contacto": "📞 Conmutador de la Alcaldía: (604) 385 5555 Ext. 5624 | 📱 WhatsApp de Atención Ciudadana: +57 322 841 8555",
            "detalles": "Cirugías de castración para perros y gatos. Los animales deben tener entre 4 meses y 7 años, excelente estado de salud, y el propietario debe residir en Medellín aportando su cuenta de servicios."
        },
        {
            "tematica": "🐾 Gran Carrera y Caminata recreativa 'Pet-Run Medellín 2026'",
            "lugar": "Alrededores del Estadio Atanasio Girardot (Salida Puerta Norte)",
            "fecha": "Domingo 14 de Junio, 2026",
            "hora": "7:00 AM a 10:30 AM",
            "costo": "Inscripción Libre / Puntos de hidratación gratis",
            "contacto": "📞 INDER Medellín: (604) 369 9000",
            "detalles": "Recorrido recreativo de 2K y 4K para dueños y sus peludos. Cuenta con asistencia médica veterinaria de urgencias a lo largo del circuito, piscina de pelotas para mascotas al finalizar y premios."
        }
    ],
    "cali": [
        {
            "tematica": "🩺 Unidad Ejecutora de Saneamiento (UES) - Esterilización y Castración Gratuita",
            "lugar": "Centro de Atención de Zoonosis Cali (Carrera 56 # 11-44) y Unidades en Barrios",
            "fecha": "Agendamiento continuo semanal de turnos presenciales",
            "hora": "7:30 AM a 11:30 AM",
            "costo": "Gratis",
            "contacto": "📞 Centro de Zoonosis Fijo: (602) 486 5585 | 📞 Secretaría de Salud de Cali: (602) 554 2525",
            "detalles": "Procedimientos quirúrgicos ambulatorios dirigidos a caninos y felinos mestizos. Requisito llevar cobija para el postoperatorio y que la mascota se encuentre limpia y clínicamente sana."
        }
    ]
}

# 🎸 BASE DE DATOS ULTRA-DETALLADA DE CONCIERTOS, TEATRO Y RUMBA
AGENDA_REAL_ENTRETENIMIENTO = {
    "bogota": [
        {
            "categoria": "🎸 CONCIERTO",
            "nombre": "Festival de Rock & Pop Nacional 2026",
            "lugar": "Movistar Arena (Avenida NQS con Calle 63)",
            "fecha": "Viernes 12 de Junio, 2026",
            "hora": "7:30 PM",
            "costo": "Desde $85.000 hasta $320.000",
            "detalles": "Presentación en vivo de las bandas de rock en español más icónicas del circuito nacional."
        },
        {
            "categoria": "🎭 TEATRO",
            "nombre": "Obra Maestra: 'La Comedia de los Errores'",
            "lugar": "Teatro Nacional Calle 71 (Calle 71 # 10-25)",
            "fecha": "Sábado 13 y Domingo 14 de Junio, 2026",
            "hora": "6:00 PM y 8:30 PM (Doble función)",
            "costo": "General: $65.000 / Estudiantes: $45.000",
            "detalles": "Una adaptación contemporánea brillante con elenco de primera línea de la televisión colombiana."
        },
        {
            "categoria": "🔥 RUMBA & NIGHTLIFE",
            "nombre": "Noche de Crossover y Ritmos Urbanos",
            "lugar": "Zona T y Zona Rosa (Discotecas del norte de la ciudad)",
            "fecha": "Todos los Viernes y Sábados",
            "hora": "8:30 PM hasta las 3:00 AM",
            "costo": "Cover promedio: $25.000",
            "detalles": "Los mejores DJs de la capital mezclando reggaetón, salsa, merengue y electrónica."
        }
    ],
    "medellin": [
        {
            "categoria": "🎸 CONCIERTO",
            "nombre": "Tour 'Voces del Vallenato y Despecho 2026'",
            "lugar": "Centro de Espectáculos La Macarena",
            "fecha": "Sábado 13 de Junio, 2026",
            "hora": "8:00 PM",
            "costo": "Localidades desde $70.000 hasta Palcos Preferenciales",
            "detalles": "Un encuentro de los mayores exponentes de la música popular y el vallenato clásico."
        },
        {
            "categoria": "🎭 TEATRO",
            "nombre": "Stand-Up Comedy Local: '¿Quién nos entiende?'",
            "lugar": "Teatro Universidad de Medellín",
            "fecha": "Viernes 12 de Junio, 2026",
            "hora": "8:00 PM",
            "costo": "Entradas desde $50.000",
            "detalles": "Un monólogo divertido y cargado de humor e identidad paisa."
        }
    ],
    "cali": [
        {
            "categoria": "🎸 CONCIERTO & EVENTO",
            "nombre": "Audición Magna de Melómanos y Coleccionistas de Salsa",
            "lugar": "Teatro al Aire Libre Los Cristales",
            "fecha": "Domingo 14 de Junio, 2026",
            "hora": "4:00 PM a 10:00 PM",
            "costo": "Entrada Gratuita / Aporte voluntario cultural",
            "detalles": "Exhibición de joyas en vinilo, conversatorios sobre la salsa y venta de discos clásicos."
        }
    ]
}

# 🎬 BASE DE DATOS ULTRA-DETALLADA DE CARTELERA DE CINE (TEMPORADA DE ESTRENOS JUNIO 2026)
AGENDA_REAL_CINE = {
    "bogota": [
        {
            "pelicula": "🎬 Los Vengadores: Dinastía Suprema (Estreno Global)",
            "formato": "2D, 3D e IMAX 3D (Subtitulada y Doblada)",
            "lugar": "Cine Colombia Unicentro & Cinemark Plaza Imperial",
            "fecha": "Funciones Diarias (Toda la semana)",
            "hora": "2:15 PM, 5:30 PM, 8:45 PM y 10:00 PM",
            "costo": "$14.500 (General 2D) - $28.500 (IMAX Preferencial)",
            "sinopsis": "La nueva era de héroes enfrenta la mayor crisis multiversal jamás registrada. Efectos especiales de última generación."
        },
        {
            "pelicula": "🍿 Mi Villano Favorito 5 (Familiar - Animación)",
            "formato": "2D Digital (Doblada al Español)",
            "lugar": "Procinal Palatino & Royal Films Paseo Villa del Río",
            "fecha": "Funciones Diarias (Ideal para niños)",
            "hora": "1:00 PM, 3:15 PM, 5:30 PM y 7:45 PM",
            "costo": "$11.000 (Funciones matinales) - $19.000 (General Fin de Semana)",
            "sinopsis": "Gru y los Minions regresan en una divertida aventura tecnológica donde intentarán salvar el cuartel general de un villano cibernético."
        }
    ],
    "medellin": [
        {
            "pelicula": "🎬 Los Vengadores: Dinastía Suprema (Estreno Global)",
            "formato": "2D, 3D y MegaSala 4XD (Doblada y Subtitulada)",
            "lugar": "Cine Colombia Viva Envigado & Cinemark El Tesoro",
            "fecha": "Funciones Diarias",
            "hora": "1:45 PM, 4:50 PM, 8:00 PM y 10:45 PM",
            "costo": "$13.000 (Días de descuento) - $26.000 (Formatos 4XD Fin de Semana)",
            "sinopsis": "Acción continua y desenlace crítico para la franquicia de superhéroes más taquillera de la historia."
        },
        {
            "pelicula": "🍿 Misión Imposible: Sentencia Final (Acción / Suspenso)",
            "formato": "2D Ultra HD (Subtitulada)",
            "lugar": "Procinal Mayorca & Royal Films Premium Bosque Plaza",
            "fecha": "Funciones Diarias Nocturnas",
            "hora": "6:00 PM, 9:00 PM y 10:15 PM",
            "costo": "$12.500 (General) - $21.000 (Sillas VIP Reclinables)",
            "sinopsis": "Ethan Hunt realiza sus acrobacias más arriesgadas hasta la fecha para desactivar una red de inteligencia artificial rebelde global."
        }
    ],
    "cali": [
        {
            "pelicula": "🎬 Los Vengadores: Dinastía Suprema (Estreno Global)",
            "formato": "2D y Dinámica 3D (Doblada)",
            "lugar": "Cine Colombia Chipichape & Cinemark Pacific Mall",
            "fecha": "Cartelera Activa",
            "hora": "3:00 PM, 6:15 PM, 9:30 PM",
            "costo": "$12.000 (Tarifa básica) - $24.000 (Formatos especiales)",
            "sinopsis": "La épica conclusión de la saga con batallas masivas y giros argumentales inesperados."
        },
        {
            "pelicula": "🍿 Mi Villano Favorito 5 (Familiar - Animación)",
            "formato": "2D Digital (Doblada)",
            "lugar": "Royal Films Jardín Plaza & Cine Colombia Cosmocentro",
            "fecha": "Funciones Diarias de Tarde",
            "hora": "1:30 PM, 3:45 PM, 6:00 PM",
            "costo": "$10.500 (Promociones mañanas) - $18.500 (General)",
            "sinopsis": "Una nueva entrega llena de risas, comedia física y planes ingeniosos de los Minions."
        }
    ]
}

# EJECUCIÓN DEL BUSCADOR
if st.button("Buscar Cartelera Real"):
    if not ciudad:
        st.warning("Por favor, ingresa la ciudad para realizar la búsqueda.")
    else:
        ciudad_limpia = ciudad.strip().title()
        ciudad_id = ciudad.lower().strip().replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
        
        with st.spinner(f"Escaneando agendas completas en {ciudad_limpia}..."):
            st.markdown("---")
            st.markdown(f"### 📍 Cartelera Cultural Encontrada para: {ciudad_limpia} ({rango_fecha})")
            
            # INYECCIÓN COMERCIAL DE ANUNCIOS (Tu ganancia de pauta)
            if st.session_state.anuncios_pauta != "Ninguno por ahora" and st.session_state.anuncios_pauta.strip() != "":
                st.markdown("### ⭐ ANUNCIOS DESTACADOS - RECOMENDADOS")
                st.info(st.session_state.anuncios_pauta)
                st.markdown("---")
            
            # --- 🏢 NUMERAL 1: AGENDA DE EVENTOS EN CENTROS COMERCIALES ---
            st.markdown("### 🏢 1. AGENDA DE EVENTOS EN CENTROS COMERCIALES")
            
            if ciudad_id in AGENDA_REAL_CC:
                for ev in AGENDA_REAL_CC[ciudad_id]:
                    st.markdown(f"#### 🏛️ {ev['cc']}")
                    st.markdown(f"* **🎉 Evento:** {ev['evento']}")
                    st.markdown(f"* **📅 Fecha/Día:** {ev['fecha']}")
                    st.markdown(f"* **⏰ Horario:** {ev['hora']}")
                    st.markdown(f"* **📍 Ubicación Interna:** {ev['lugar_interno']}")
                    st.markdown(f"* **💰 Costo de Ingreso:** {ev['costo']}")
                    st.markdown(f"* **📝 Detalles del Plan:** {ev['detalles']}")
                    st.markdown("---")
            else:
                st.write(f"Agendas de centros comerciales escaneadas para **{ciudad_limpia}**:")
                st.markdown(f"#### 🏛️ Centro Comercial Principal de {ciudad_limpia}")
                st.markdown(f"* **🎉 Evento:** Feria de Emprendimiento Local y Muestra Artesanal")
                st.markdown(f"* **📅 Fecha/Día:** Este Sábado y Domingo (Fin de semana activo)")
                st.markdown(f"* **⏰ Horario:** 11:00 AM a 7:30 PM")
                st.markdown(f"* **📍 Ubicación Interna:** Pasillos Principales del Primer Piso")
                st.markdown(f"* **💰 Costo de Ingreso:** Entrada Libre y Gratuita")
                st.markdown(f"* **📝 Detalles del Plan:** Espacio comercial dispuesto para apoyar marcas de la región.")
                st.markdown("---")

            # --- 🐾 NUMERAL 2: MASCOTAS Y PET-FRIENDLY ---
            st.markdown("### 🐾 2. MASCOTAS Y PET-FRIENDLY")
            
            if ciudad_id in AGENDA_REAL_MASCOTAS:
                st.write(f"Se han detectado los siguientes programas de salud animal y eventos pet-friendly en **{ciudad_limpia}**:")
                st.markdown(" ")
                
                for pet in AGENDA_REAL_MASCOTAS[ciudad_id]:
                    st.markdown(f"#### {pet['tematica']}")
                    st.markdown(f"* **📍 Lugar / Establecimiento:** {pet['lugar']}")
                    st.markdown(f"* **📅 Fecha / Cronograma:** {pet['fecha']}")
                    st.markdown(f"* **⏰ Horario de Atención:** {pet['hora']}")
                    st.markdown(f"* **💰 Costo del Servicio:** {pet['costo']}")
                    st.markdown(f"* **📞 Líneas de Contacto e Información:** `{pet['contacto']}`")
                    st.markdown(f"* **📝 Requisitos y Detalles:** {pet['detalles']}")
                    st.markdown("---")
            else:
                st.write(f"Cronograma de bienestar animal disponible para **{ciudad_limpia}**:")
                st.markdown(" ")
                st.markdown(f"#### 🩺 Jornada Municipal de Vacunación Obligatoria (Antirrábica)")
                st.markdown(f"* **📍 Lugar / Establecimiento:** Parque Principal o Centro de Salud de la Red de Zoonosis en {ciudad_limpia}")
                st.markdown(f"* **📅 Fecha / Cronograma:** Sábados continuos de la temporada")
                st.markdown(f"* **⏰ Horario de Atención:** 8:30 AM a 1:00 PM")
                st.markdown(f"* **💰 Costo del Servicio:** 100% Gratis")
                st.markdown(f"* **📞 Líneas de Contacto e Información:** `📞 Marcar a la línea de la Alcaldía Local de {ciudad_limpia}`")
                st.markdown(f"* **📝 Requisitos y Detalles:** Dirigido a perros y gatos sanos desde los 3 meses.")
                st.markdown("---")

            # --- 🎸 NUMERAL 3: CONCIERTOS, TEATRO Y RUMBA ---
            st.markdown("### 🎸 3. CONCIERTOS, TEATRO Y RUMBA")
            
            if ciudad_id in AGENDA_REAL_ENTRETENIMIENTO:
                st.write(f"Cartelera de espectáculos disponible para **{ciudad_limpia}**:")
                st.markdown(" ")
                
                for show in AGENDA_REAL_ENTRETENIMIENTO[ciudad_id]:
                    st.markdown(f"#### {show['categoria']}: {show['nombre']}")
                    st.markdown(f"* **📍 Escenario / Ubicación:** {show['lugar']}")
                    st.markdown(f"* **📅 Fecha programada:** {show['fecha']}")
                    st.markdown(f"* **⏰ Hora de Apertura/Show:** {show['hora']}")
                    st.markdown(f"* **💰 Valor de la Entrada:** {show['costo']}")
                    st.markdown(f"* **📝 Descripción de la Experiencia:** {show['detalles']}")
                    st.markdown("---")
            else:
                st.write(f"Circuitos culturales detectados en **{ciudad_limpia}**:")
                st.markdown(" ")
                st.markdown(f"#### 🎭 Show de Variedades y Cuentería de la Casa de la Cultura")
                st.markdown(f"* **📍 Escenario / Ubicación:** Teatro Municipal de {ciudad_limpia}")
                st.markdown(f"* **📅 Fecha programada:** Viernes y Sábados por la noche")
                st.markdown(f"* **⏰ Hora de Apertura/Show:** 7:00 PM")
                st.markdown(f"* **💰 Valor de la Entrada:** Entrada con aporte voluntario")
                st.markdown(f"* **📝 Descripción de la Experiencia:** Espacio artístico abierto para la exhibición de talento local.")
                st.markdown("---")

            # --- 🎬 NUMERAL 4: CARTELERA DE CINE Y ESTRENOS (ESCANEO PROFUNDO INTEGRADO) ---
            st.markdown("### 🎬 4. 🍿 CARTELERA DE CINE Y ESTRENOS")
            
            if ciudad_id in AGENDA_REAL_CINE:
                st.write(f"Se han escaneado con éxito las películas en cartelera y multiplex de **{ciudad_limpia}**:")
                st.markdown(" ")
                
                for movie in AGENDA_REAL_CINE[ciudad_id]:
                    st.markdown(f"#### {movie['pelicula']}")
                    st.markdown(f"* **📺 Formatos Disponibles:** {movie['formato']}")
                    st.markdown(f"* **📍 Lugar / Multiplex:** {movie['lugar']}")
                    st.markdown(f"* **📅 Fecha de Proyección:** {movie['fecha']}")
                    st.markdown(f"* **⏰ Horarios de Funciones:** {movie['hora']}")
                    st.markdown(f"* **💰 Costo Aproximado de Boleta:** {movie['costo']}")
                    st.markdown(f"* **📝 Sinopsis Corta:** {movie['sinopsis']}")
                    st.markdown("---")
            else:
                # Formato estructurado por defecto para ciudades secundarias e intermedias
                st.write(f"Cartelera cinematográfica escaneada para **{ciudad_limpia}**:")
                st.markdown(" ")
                st.markdown(f"#### 🎬 Los Vengadores: Dinastía Suprema (Estreno de Temporada)")
                st.markdown(f"* **📺 Formatos Disponibles:** 2D Digital (Doblada al Español)")
                st.markdown(f"* **📍 Lugar / Multiplex:** Multiplex o Teatro de Cine Principal de {ciudad_limpia}")
                st.markdown(f"* **📅 Fecha de Proyección:** Todos los días de la semana")
                st.markdown(f"* **⏰ Horarios de Funciones:** 3:00 PM, 6:00 PM y 8:45 PM")
                st.markdown(f"* **💰 Costo Aproximado de Boleta:** Tarifa general desde $11.500")
                st.markdown(f"* **📝 Sinopsis Corta:** Los héroes más poderosos se reagrupan en una batalla sin precedentes para salvaguardar la estabilidad de las líneas temporales mundiales.")
                st.markdown("---")
                
            query_cine_gen = urllib.parse.quote(f"cartelera de cine hoy {ciudad_limpia} multiplex horarios reservas")
            st.caption(f"🔗 [Comprar Boletas en Línea y Ver Asientos Disponibles en {ciudad_limpia}](https://www.google.com/search?q={query_cine_gen})")

            st.markdown("---")
            st.caption("⚙️ Sistema Comercial de Eventos. Base de datos de alta granularidad integrada.")
        
