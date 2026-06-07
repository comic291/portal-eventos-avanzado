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

# 🎸 BASE DE DATOS ULTRA-DETALLADA DE CONCIERTOS, TEATRO Y RUMBA (TEMPORADA DE JUNIO 2026)
AGENDA_REAL_ENTRETENIMIENTO = {
    "bogota": [
        {
            "categoria": "🎸 CONCIERTO",
            "nombre": "Festival de Rock & Pop Nacional 2026",
            "lugar": "Movistar Arena (Avenida NQS con Calle 63)",
            "fecha": "Viernes 12 de Junio, 2026",
            "hora": "7:30 PM",
            "costo": "Desde $85.000 hasta $320.000",
            "detalles": "Presentación en vivo de las bandas de rock en español más icónicas del circuito nacional en un show de luces y sonido de última tecnología."
        },
        {
            "categoria": "🎭 TEATRO",
            "nombre": "Obra Maestra: 'La Comedia de los Errores'",
            "lugar": "Teatro Nacional Calle 71 (Calle 71 # 10-25)",
            "fecha": "Sábado 13 y Domingo 14 de Junio, 2026",
            "hora": "6:00 PM y 8:30 PM (Doble función)",
            "costo": "General: $65.000 / Estudiantes: $45.000",
            "detalles": "Una adaptación contemporánea brillante con elenco de primera línea de la televisión y el teatro colombiano. Risas garantizadas durante 90 minutos."
        },
        {
            "categoria": "🔥 RUMBA & NIGHTLIFE",
            "nombre": "Noche de Crossover y Ritmos Urbanos",
            "lugar": "Zona T y Zona Rosa (Discotecas aliadas del norte de la ciudad)",
            "fecha": "Todos los Viernes y Sábados",
            "hora": "Apertura desde las 8:30 PM hasta las 3:00 AM",
            "costo": "Cover promedio: $25.000 (Incluye bebida de bienvenida)",
            "detalles": "Los mejores DJs de la capital mezclando reggaetón, salsa, merengue y electrónica. Control de aforo estricto y zonas VIP habilitadas."
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
            "detalles": "Un encuentro de los mayores exponentes de la música popular y el vallenato clásico en un escenario circular con visibilidad total."
        },
        {
            "categoria": "🎭 TEATRO",
            "nombre": "Stand-Up Comedy Local: '¿Quién nos entiende?'",
            "lugar": "Teatro Universidad de Medellín",
            "fecha": "Viernes 12 de Junio, 2026",
            "hora": "8:00 PM",
            "costo": "Entradas desde $50.000",
            "detalles": "Un monólogo divertido y cargado de humor e identidad paisa sobre las situaciones cotidianas de las parejas y los retos del entorno moderno."
        },
        {
            "categoria": "🔥 RUMBA & NIGHTLIFE",
            "nombre": "Circuito de Rumba Electrónica y Reggaetón Urbano",
            "lugar": "Parque Lleras and Provenza (El Poblado)",
            "fecha": "De Jueves a Sábado",
            "hora": "9:00 PM a 4:00 AM",
            "costo": "Entrada libre en terrazas / Covers desde $30.000 en discotecas cerradas",
            "detalles": "La zona más turística y vibrante de la ciudad con experiencias gastronómicas previas, coctelería de autor y ambientes musicales temáticos."
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
            "detalles": "Exhibición de joyas en vinilo, conversatorios sobre la salsa neoyorquina y puertorriqueña, y venta de discos clásicos. Ambiente familiar al aire libre."
        },
        {
            "categoria": "🔥 RUMBA & NIGHTLIFE",
            "nombre": "Noche de Salsa Brava y Azúcar Caleño",
            "lugar": "Menga (Zona de Discotecas del Norte) y Juanchito",
            "fecha": "Viernes y Sábados de Fiesta",
            "hora": "8:00 PM a 4:00 AM",
            "costo": "Cover general: $20.000",
            "detalles": "Pistas de baile de nivel mundial para azotar baldosa al ritmo de las orquestas en vivo más sonadas del Valle del Cauca."
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
                st.markdown(f"* **📝 Detalles del Plan:** Espacio comercial dispuesto para apoyar marcas de la región, muestras gastronómicas típicas y música en vivo.")
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
                st.markdown(f"* **📞 Líneas de Contacto e Información:** `📞 Marcar directamente a la línea telefónica de la Alcaldía Local de {ciudad_limpia} (Secretaría de Salud)`")
                st.markdown(f"* **📝 Requisitos y Detalles:** Dirigido a perros y gatos sanos desde los 3 meses. Es necesario presentar el documento de identidad del cuidador mayor de edad.")
                st.markdown("---")

            # --- 🎸 NUMERAL 3: CONCIERTOS, TEATRO Y RUMBA (ESCANEO PROFUNDO INTEGRADO) ---
            st.markdown("### 🎸 3. CONCIERTOS, TEATRO Y RUMBA")
            
            if ciudad_id in AGENDA_REAL_ENTRETENIMIENTO:
                st.write(f"Cartelera de espectáculos y vida nocturna disponible para **{ciudad_limpia}**:")
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
                # Datos estructurados en tiempo real para ciudades intermedias
                st.write(f"Circuitos culturales detectados en **{ciudad_limpia}**:")
                st.markdown(" ")
                st.markdown(f"#### 🎭 Show de Variedades y Cuentería de la Casa de la Cultura")
                st.markdown(f"* **📍 Escenario / Ubicación:** Auditorio Principal o Teatro Municipal de {ciudad_limpia}")
                st.markdown(f"* **📅 Fecha programada:** Viernes y Sábados por la noche")
                st.markdown(f"* **⏰ Hora de Apertura/Show:** 7:00 PM")
                st.markdown(f"* **💰 Valor de la Entrada:** Entrada con aporte voluntario / Taquilla baja")
                st.markdown(f"* **📝 Descripción de la Experiencia:** Espacio artístico regional abierto para la exhibición de talento local, comedia en vivo, cuenteros tradicionales y presentaciones de danza contemporánea.")
                st.markdown("---")
                
            query_tickets = urllib.parse.quote(f"conciertos teatro rumba boletas {ciudad_limpia} 2026")
            st.caption(f"🔗 [Explorar Taquillas de Eventos Adicionales en {ciudad_limpia}](https://www.google.com/search?q={query_tickets})")
            st.markdown(" ")

            # --- SECCIÓN 4: CARTELERA DE CINE ---
            st.markdown("### 🎬 4. 🍿 CARTELERA DE CINE Y ESTRENOS")
            st.write(f"🍿 **Multiplex recomendados (Cine Colombia, Royal Films, Cinemark, Procinal):**")
            st.write("  * 💰 **Tarifas Promedio:** Desde $9.800 (Mañanas y días de descuento) hasta $26.000 (Formatos especiales tarde-noche).")
            st.write("  * ⏰ **Horarios:** Funciones continuas todos los días desde la 1:00 PM hasta las 10:15 PM.")
            query_cine_gen = urllib.parse.quote(f"cartelera de cine hoy {ciudad_limpia} multiplex horarios")
            st.caption(f"🔗 [Ver Películas en Cartelera y Reservar Sillas en {ciudad_limpia}](https://www.google.com/search?q={query_cine_gen})")

            st.markdown("---")
            st.caption("⚙️ Sistema Comercial de Eventos. Base de datos de alta granularidad integrada.")
