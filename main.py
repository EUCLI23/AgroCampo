import streamlit as st
import mysql.connector
import random
import time

# Configuración de página
st.set_page_config(page_title="AgroCampo", page_icon="🌱", layout="centered")

# --- CONEXIÓN CON XAMPP ---
def obtener_conexion():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="bd_agrocampo"
    )

# --- FUNCIONES DE BASE DE DATOS ---
def guardar_publicacion_db(autor, contenido, ubicacion):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = "INSERT INTO publicaciones (autor, contenido, ubicacion) VALUES (%s, %s, %s)"
        cursor.execute(query, (autor, contenido, ubicacion))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error al guardar en la base de datos: {e}")
        return False

def listar_publicaciones_db():
    try:
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM publicaciones ORDER BY id DESC")
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        return resultados
    except Exception as e:
        return []

def editar_publicacion_db(id_pub, nuevo_contenido):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = "UPDATE publicaciones SET contenido = %s WHERE id = %s"
        cursor.execute(query, (nuevo_contenido, id_pub))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error al editar: {e}")
        return False

def eliminar_publicacion_db(id_pub):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = "DELETE FROM publicaciones WHERE id = %s"
        cursor.execute(query, (id_pub,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error al eliminar: {e}")
        return False

def cambiar_contrasena_db(usuario, nueva_clave):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = "UPDATE usuarios SET contrasena = %s WHERE usuario = %s"
        cursor.execute(query, (nueva_clave, usuario))
        conn.commit()
        filas_afectadas = cursor.rowcount
        cursor.close()
        conn.close()
        return filas_afectadas > 0
    except Exception as e:
        st.error(f"Error de base de datos al cambiar contraseña: {e}")
        return False


# --- CONTROL DE SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = "Gabriel Peraza"
if "username_actual" not in st.session_state:
    st.session_state.username_actual = "GabrielP"
if "ubicacion_actual" not in st.session_state:
    st.session_state.ubicacion_actual = "Lara, Venezuela"

if "pantalla_actual" not in st.session_state:
    st.session_state.pantalla_actual = "Novedades"  
if "pantalla_auth" not in st.session_state:
    st.session_state.pantalla_auth = "login"

if "pub_count" not in st.session_state:
    st.session_state.pub_count = 10
if "mkt_count" not in st.session_state:
    st.session_state.mkt_count = 0
if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0  

# Estructura temporal para novedades con soporte de fotos en vivo
if "db_novedades_locales" not in st.session_state:
    st.session_state.db_novedades_locales = [
        {"id": 1, "autor": "Euclimar García", "contenido": "Iniciando la siembra de maíz en la zona alta.", "ubicacion": "Lara, Venezuela", "imagen": None}
    ]

if "historial_ia" not in st.session_state:
    st.session_state.historial_ia = [
        {"role": "assistant", "content": "¡Saludos! Soy AgroIA, su asesor de ingeniería agronómica. Estoy listo para proveer diagnósticos técnicos, planes de dosificación de fertilizantes e intervenciones de manejo fitosanitario de precisión. ¿Qué escenario evaluamos hoy?", "imagen": None}
    ]

if "db_market" not in st.session_state:
    st.session_state.db_market = [
        {"id": 1, "autor": "Euclimar García", "titulo": "Sacos de Fertilizante NPK", "precio": "25.00", "ubicacion": "Lara, Venezuela", "descripcion": "Alta calidad para fases de crecimiento foliar.", "imagen": None}
    ]

def responder_ia_agronomo(mensaje_usuario, tiene_archivo=False):
    msg = mensaje_usuario.lower()
    if tiene_archivo:
        return "🔬 *Análisis Técnico de Registro Multimedia (AgroIA):* Evaluando patrones sintomatológicos en el material visual suministrado al nivel de ingeniería agronómica. Se observa una carga potencial de maleza densa o anomalías foliares. Se recomienda un control cultural/mecánico inicial previo al trasplante y el monitoreo de plagas asociadas al monte."
    if "fertilidad" in msg or "fertilizante" in msg or "abono" in msg or "npk" in msg or "urea" in msg:
        return "🚜 *Dictamen Agronómico (Fertilidad):* Para optimizar el rendimiento por hectárea, suspenda aplicaciones genéricas. Aplique un plan balanceado basado en análisis de suelo previo. En fase vegetativa agresiva, se prescribe dosificación fraccionada de Nitrógeno (Urea al 46%) combinada con enmiendas de Fósforo ($P_2O_5$) de alta solubilidad si el pH está fuera del rango balanceado (6.0 - 6.5)."
    if "plaga" in msg or "insecto" in msg or "enfermedad" in msg or "hongo" in msg or "monte" in msg or "maleza" in msg:
        return "🛡️ *Estrategia Fitosanitaria (Manejo de Malezas y Suelo):* Ante la presencia de alta densidad de maleza ('mucho monte') previo a la siembra de pimentón, se sugiere realizar un desmalezado mecánico o rastreo para incorporar la materia orgánica, o evaluar una application localizada de herbicida si el umbral lo requiere. Esto evitará la competencia por nutrientes y luz con las plántulas."
    return "📊 *Consulta Registrada por Ingeniería:* Para estructurar la prescripción técnica idónea, provea los datos del cultivo, etapa fenológica exacta, densidad de siembra y tipo de suelo predominante."

# ==========================================
# 🚪 PANEL DE AUTENTICACIÓN
# ==========================================
def render_autentizacion():
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] {
            background-color: #1e4d2b !important;
            background-image: linear-gradient(135deg, #11301a 0%, #2e6d38 100%) !important;
        }
        [data-testid="stHeader"] { background: transparent !important; }
        .block-container {
            background-color: rgba(0, 0, 0, 0.4) !important;
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 2.5rem 1.5rem !important;
            max-width: 420px !important;
            margin-top: 5vh;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        h1, h2, h3, p, div[data-testid="stWidgetLabel"] p { color: #ffffff !important; }
        div[data-testid="stTextInput"] input {
            background-color: transparent !important; color: #ffffff !important; border: 1px solid #ffffff !important; border-radius: 8px !important;
        }
        button[kind="primary"] {
            background-color: #4CAF50 !important; color: white !important; border-radius: 12px !important; font-weight: bold !important; padding: 0.6rem !important;
        }
        .auth-inline-container { display: flex !important; justify-content: space-between !important; align-items: center !important; width: 100% !important; margin-top: 25px !important; }
        .auth-inline-container div.stButton > button { background: transparent !important; color: #ffffff !important; border: none !important; text-decoration: underline !important; font-size: 15px !important; padding: 0px !important; }
        </style>
    """, unsafe_allow_html=True)

    if st.session_state.pantalla_auth == "login":
        st.markdown('<div style="text-align:center; font-size:32px; font-weight:bold; color:white; margin-bottom:20px;">🌱 AgroCampo</div>', unsafe_allow_html=True)
        user_input = st.text_input("Usuario", placeholder="Ingrese usuario", key="login_user")
        pass_input = st.text_input("Contraseña", type="password", placeholder="Ingrese contraseña", key="login_pass")
        
        if st.button("ACCEDER", type="primary", use_container_width=True):
            st.session_state.autenticado = True
            if user_input.strip():
                st.session_state.username_actual = user_input
                st.session_state.usuario_actual = user_input
            st.rerun()
            
        st.markdown('<div class="auth-inline-container">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Crear cuenta", key="goto_register"):
                st.session_state.pantalla_auth = "registro"
                st.rerun()
        with col2:
            if st.button("¿Olvidó su clave?", key="goto_recovery"):
                st.session_state.pantalla_auth = "recuperacion"
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.pantalla_auth == "registro":
        st.markdown('<div style="text-align:center; font-size:26px; font-weight:bold; color:white; margin-bottom:20px;">📝 Registro</div>', unsafe_allow_html=True)
        nombre_completo = st.text_input("Nombre Completo", placeholder="Ingrese su nombre", key="reg_nom")
        user_reg = st.text_input("Nombre de Usuario", placeholder="Ingrese usuario deseado", key="reg_usr")
        region_reg = st.text_input("Ubicación / Región Agrícola", placeholder="Ej. Lara, Venezuela", key="reg_ubi")
        st.text_input("Contraseña", type="password", placeholder="Ingrese contraseña", key="reg_pwd")
        
        if st.button("REGISTRARSE", type="primary", use_container_width=True):
            if nombre_completo.strip() and user_reg.strip():
                st.session_state.usuario_actual = nombre_completo.strip()
                st.session_state.username_actual = user_reg.strip()
                st.session_state.ubicacion_actual = region_reg.strip() if region_reg.strip() else "Lara, Venezuela"
                st.session_state.autenticado = True
                st.rerun()

    elif st.session_state.pantalla_auth == "recuperacion":
        st.text_input("Usuario o Correo", placeholder="Ingrese su usuario o correo", key="rec_usr")
        if st.button("ENVIAR CÓDIGO", type="primary", use_container_width=True):
            st.success("Código enviado.")

# ==========================================
# 🌱 INTERFAZ PRINCIPAL
# ==========================================
def render_dashboard():
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] { background-color: #F7F9F6 !important; }
        .block-container { max-width: 550px !important; padding: 1.5rem 1rem !important; }
        .main-header { font-size: 34px; font-weight: 900; color: #1E3D14 !important; text-align: center; margin-top: 55px !important; margin-bottom: 15px; }
        
        .agro-card { background-color: #FFFFFF !important; border-radius: 14px; padding: 18px; border: 1px solid #EAEAEA; margin-bottom: 5px; color: #111111 !important; }
        .agro-card b, .agro-card p, .agro-card div, .agro-card span { color: #111111 !important; font-size: 15px; }
        
        .chat-card { background-color: #FFFFFF !important; border-radius: 14px; padding: 18px; border: 1px solid #EAEAEA; margin-bottom: 10px; color: #111111 !important; }
        .chat-card p, .chat-card span, .chat-card b, .chat-card div { color: #111111 !important; font-size: 15px !important; }
        
        div[data-testid="stWidgetLabel"] p, label p { color: #1E3D14 !important; font-weight: bold !important; }
        h5 { color: #1E3D14 !important; font-weight: bold !important; margin-top: 10px; margin-bottom: 15px; }
        
        /* Asegurar que las cajas de entrada tengan texto negro legible */
        div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea, div[data-testid="stNumberInput"] input { 
            background-color: #ffffff !important; 
            color: #000000 !important; 
            border: 1px solid #cccccc !important; 
            border-radius: 8px !important; 
        }
        
        div[data-testid="stFileUploader"] section { background-color: #ffffff !important; border: 1px dashed #2e6d38 !important; border-radius: 10px !important; padding: 15px !important; }
        div[data-testid="stFileUploader"] section div[data-testid="stMarkdownContainer"] p, div[data-testid="stFileUploader"] small, div[data-testid="stFileUploader"] span { color: #111111 !important; font-weight: 500 !important; }
        div[data-testid="stFileUploader"] button { background-color: #2e6d38 !important; color: #ffffff !important; border: 1px solid #1e4d2b !important; border-radius: 8px !important; font-weight: bold !important; padding: 6px 14px !important; }
        
        /* Estilos específicos para los tres puntos flotantes */
        .btn-tres-puntos button {
            background: transparent !important;
            color: #555555 !important;
            border: none !important;
            font-size: 22px !important;
            padding: 0px !important;
            margin: 0px !important;
            float: right;
        }
        .btn-tres-puntos button:hover {
            color: #1E3D14 !important;
        }
        
        .menu-horizontal-container { display: flex !important; flex-direction: row !important; justify-content: space-between !important; width: 100% !important; gap: 4px !important; margin-bottom: 15px !important; }
        .menu-horizontal-container div.element-container, .menu-horizontal-container div.stButton { flex: 1 1 0% !important; width: auto !important; margin: 0 !important; }
        div.stButton > button { background-color: #2e6d38 !important; color: #ffffff !important; border-radius: 8px !important; border: 1px solid #1e4d2b !important; font-weight: bold !important; font-size: 12px !important; padding: 10px 1px !important; width: 100% !important; }
        div.stButton > button:hover { background-color: #1e4d2b !important; }
        
        .weather-container { background-color: #e3f2fd !important; border-radius: 16px; padding: 22px; border: 1px solid #bbdefb; margin-top: 10px; }
        .weather-title { font-size: 24px; font-weight: bold; color: #0d47a1 !important; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; }
        .weather-temp { font-size: 46px; font-weight: 900; color: #1565c0 !important; margin: 0; line-height: 1; }
        .weather-details { font-size: 16px; color: #1e88e5 !important; font-weight: 600; margin-top: 10px; }
        .weather-alert { background-color: #fff3e0; border-left: 5px solid #ffb74d; padding: 12px; border-radius: 8px; margin-top: 15px; color: #e65100 !important; font-weight: bold; font-size: 14px; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-header">🌱 AGROCAMPO</div>', unsafe_allow_html=True)
    busqueda = st.text_input("", placeholder="🔍 Buscar...", key="barra_busqueda_global")

    st.markdown('<div class="menu-horizontal-container">', unsafe_allow_html=True)
    cols_nav = st.columns(5)
    secciones = ["Novedades", "Market", "AgroIA", "Clima", "Perfil"]
    iconos = ["📰 Novedades", "🛒 Market", "🤖 AgroIA", "🌤️ Clima", "👤 Perfil"]
    
    for indice, col in enumerate(cols_nav):
        with col:
            es_activa = secciones[indice] == st.session_state.pantalla_actual
            label = f"✨ {iconos[indice]}" if es_activa else iconos[indice]
            if st.button(label, key=f"nav_top_{secciones[indice]}"):
                st.session_state.pantalla_actual = secciones[indice]
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<hr style='border:0; border-top: 1px solid #ddd; margin: 10px 0;'>", unsafe_allow_html=True)

    # --- NOVEDADES ---
    if st.session_state.pantalla_actual == "Novedades":
        st.markdown("<h4 style='color:#1E3D14;'>Publicaciones de la Comunidad</h4>", unsafe_allow_html=True)
        with st.expander("➕ Crear Publicación", expanded=False):
            nuevo_texto = st.text_area("¿Qué está pasando en tu cultivo?", placeholder="Escribe aquí tu estado...", key=f"txt_pub_{st.session_state.pub_count}")
            pub_media = st.file_uploader("Subir foto o video (Opcional):", type=["png", "jpg", "jpeg", "mp4", "mov"])
            add_ubi = st.checkbox("📍 Agregar ubicación geográfica")
            pub_ubicacion = st.text_input("Ubicación:", placeholder="Ej. Lara, Venezuela") if add_ubi else ""
            
            if st.button("Publicar", type="primary", use_container_width=True):
                if nuevo_texto.strip() or pub_media is not None:
                    id_nueva = random.randint(100, 9999)
                    guardar_publicacion_db(st.session_state.usuario_actual, nuevo_texto, pub_ubicacion)
                    
                    nueva_noticia = {
                        "id": id_nueva,
                        "autor": st.session_state.usuario_actual,
                        "contenido": nuevo_texto,
                        "ubicacion": pub_ubicacion,
                        "imagen": pub_media
                    }
                    st.session_state.db_novedades_locales.insert(0, nueva_noticia)
                    st.session_state.pub_count += 1
                    st.rerun()

        # Renderizar la lista unificada
        for indice, post in enumerate(st.session_state.db_novedades_locales):
            col_contenido, col_puntos = st.columns([0.9, 0.1])
            
            with col_contenido:
                st.markdown(f'<div class="agro-card"><b>👤 {post["autor"]}</b> {f"📍 {post["ubicacion"]}" if post.get("ubicacion") else ""}<p>{post["contenido"]}</p></div>', unsafe_allow_html=True)
                if post.get("imagen") is not None:
                    st.image(post["imagen"], width=350)
            
            with col_puntos:
                abrir_opciones = False
                if post["autor"] == st.session_state.usuario_actual:
                    st.markdown('<div class="btn-tres-puntos">', unsafe_allow_html=True)
                    if st.button("⋮", key=f"puntos_{post['id']}_{indice}"):
                        key_menu = f"menu_activo_{post['id']}"
                        st.session_state[key_menu] = not st.session_state.get(key_menu, False)
                    st.markdown('</div>', unsafe_allow_html=True)
                    abrir_opciones = st.session_state.get(f"menu_activo_{post['id']}", False)

            if abrir_opciones:
                st.markdown("<div style='background-color:#f0f2f6; padding:12px; border-radius:10px; border-left:4px solid #2e6d38; margin-top:-10px; margin-bottom:15px;'>", unsafe_allow_html=True)
                txt_edicion = st.text_input("Editar texto de la publicación:", value=post["contenido"], key=f"input_edit_{post['id']}_{indice}")
                
                col_btn_edit, col_btn_elim = st.columns(2)
                with col_btn_edit:
                    if st.button("Guardar Cambios ✏️", key=f"btn_edit_{post['id']}_{indice}", use_container_width=True):
                        editar_publicacion_db(post["id"], txt_edicion)
                        post["contenido"] = txt_edicion
                        st.session_state[f"menu_activo_{post['id']}"] = False
                        st.toast("¡Publicación actualizada!")
                        st.rerun()
                with col_btn_elim:
                    if st.button("Eliminar Estado 🗑️", key=f"btn_elim_{post['id']}_{indice}", use_container_width=True):
                        eliminar_publicacion_db(post["id"])
                        st.session_state.db_novedades_locales.pop(indice)
                        st.session_state[f"menu_activo_{post['id']}"] = False
                        st.toast("¡Publicación eliminada!")
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
                
            st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)

    # --- MARKET ---
    elif st.session_state.pantalla_actual == "Market":
        st.markdown("<h4 style='color:#1E3D14;'>🛒 Mercado de Insumos</h4>", unsafe_allow_html=True)
        
        with st.expander("➕ Publicar un Producto para la Venta", expanded=False):
            mkt_titulo = st.text_input("📦 Nombre del Producto / Insumo:", placeholder="Ej: Sacos de Fertilizante NPK, Semillas, etc.")
            
            # Restricción estricta con st.number_input (ahora con texto negro legible mediante CSS)
            mkt_precio = st.number_input("💵 Precio ($):", min_value=0.0, step=0.01, format="%.2f")
            
            mkt_desc = st.text_area("📝 Descripción:", placeholder="Detalles de calidad, estado o uso recomendado...")
            mkt_foto = st.file_uploader("📸 Adjuntar Foto del Producto:", type=["png", "jpg", "jpeg"])
            
            add_ubi_mkt = st.checkbox("📍 Especificar ubicación de entrega", value=True)
            mkt_ubicacion = st.text_input("Ubicación de venta:", value=st.session_state.ubicacion_actual) if add_ubi_mkt else "No especificada"
            
            if st.button("Publicar Oferta 🚀", type="primary", use_container_width=True):
                if mkt_titulo.strip() and mkt_precio > 0:
                    nuevo_item = {
                        "id": len(st.session_state.db_market) + 1,
                        "autor": st.session_state.usuario_actual,
                        "titulo": mkt_titulo.strip(),
                        "precio": f"{mkt_precio:.2f}",
                        "ubicacion": mkt_ubicacion.strip(),
                        "descripcion": mkt_desc.strip(),
                        "imagen": mkt_foto
                    }
                    st.session_state.db_market.insert(0, nuevo_item)
                    st.success("¡Producto agregado exitosamente al catálogo!")
                    st.rerun()

        for item in st.session_state.db_market:
            st.markdown(f"""
                <div class="agro-card">
                    <b style="font-size:18px; color:#1E3D14 !important;">📦 {item["titulo"]}</b><br>
                    <span style="color:#d32f2f !important; font-weight:bold; font-size:16px;">Precio: {item["precio"]}$</span> | 📍 <i>{item["ubicacion"]}</i><br>
                    <small style="color:#777;">Vendedor: {item["autor"]}</small>
                    <p style="margin-top:8px; font-size:15px;">{item["descripcion"]}</p>
                </div>
            """, unsafe_allow_html=True)
            
            if item.get("imagen") is not None:
                st.image(item["imagen"], use_container_width=True)
                
            st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)

    # --- AGROIA ---
    elif st.session_state.pantalla_actual == "AgroIA":
        st.markdown("<h4 style='color:#1E3D14;'>🔬 Consultoría AgroIA</h4>", unsafe_allow_html=True)
        
        for chat in st.session_state.historial_ia:
            rol_nombre = "🤖 AGROIA" if chat["role"] == "assistant" else "👤 TÚ"
            st.markdown(f'<div class="chat-card"><b>{rol_nombre}:</b><br>{chat["content"]}</div>', unsafe_allow_html=True)
            if chat.get("imagen") is not None:
                st.image(chat["imagen"], caption="Material visual bajo evaluación", width=250)
        
        st.markdown("<hr style='border-top:1px dashed #ccc;'>", unsafe_allow_html=True)
        
        st.markdown("##### Enviar consulta al Ingeniero Agrónomo Virtual")
        foto_cultivo = st.file_uploader("📸 Adjuntar registro fotográfico del cultivo (Opcional):", type=["png", "jpg", "jpeg"], key="uploader_ia")
        consulta_texto = st.text_input("✍️ Describa los síntomas observados o su consulta técnica:", placeholder="Ej: Tengo mucho monte en el cultivo o requiero plan de NPK...", key="input_texto_ia")
        
        if st.button("Enviar a Consultoría 🚀", type="primary", use_container_width=True):
            if consulta_texto.strip() or foto_cultivo is not None:
                tiene_foto = foto_cultivo is not None
                texto_usuario = consulta_texto if consulta_texto.strip() else "Se adjunta material fotográfico para evaluación diagnóstica."
                
                st.session_state.historial_ia.append({
                    "role": "user",
                    "content": texto_usuario,
                    "imagen": foto_cultivo
                })
                
                respuesta = responder_ia_agronomo(texto_usuario, tiene_archivo=tiene_foto)
                st.session_state.historial_ia.append({
                    "role": "assistant",
                    "content": respuesta,
                    "imagen": None
                })
                st.rerun()

    # --- 🌤️ CLIMA (CON VARIACIÓN DEL TIEMPO REALISTA) ---
    elif st.session_state.pantalla_actual == "Clima":
        st.markdown("<h4 style='color:#1E3D14;'>🌤️ Estación Meteorológica</h4>", unsafe_allow_html=True)
        
        # Simulación dinámica usando la semilla del tiempo actual para generar pequeños cambios continuos
        random.seed(int(time.time()) // 60) # Cambia el valor sutilmente cada minuto
        temperatura_dinamica = round(random.uniform(26.0, 31.5), 1)
        humedad_dinamica = random.randint(58, 72)
        
        st.markdown(f"""
            <div class="weather-container">
                <div class="weather-title">📍 {st.session_state.ubicacion_actual}</div>
                <div class="weather-temp">{temperatura_dinamica}°C</div>
                <div class="weather-details">
                    💧 Humedad Relativa: <b>{humedad_dinamica}%</b><br>
                    💨 Estado del Tiempo: <b>Condiciones cambiantes en tiempo real</b>
                </div>
        """, unsafe_allow_html=True)
        
        if temperatura_dinamica >= 24 and temperatura_dinamica <= 30:
            st.markdown("""
                <div class="weather-alert">
                    📢 <b>RECOMENDACIÓN TÉCNICA:</b><br>
                    El ambiente se encuentra <b>APTO PARA SEMBRAR Y REGAR</b>. Las condiciones de evapotranspiración son estables. Se aconseja realizar labores de campo antes del incremento térmico de la tarde.
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="weather-alert">
                    📢 <b>RECOMENDACIÓN TÉCNICA:</b><br>
                    Pico térmico elevado observado. Monitorear el estrés hídrico de las plantas. Apto principalmente para labores de control mecánico, preparación de abonos o mantenimiento estructural.
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

    # --- PERFIL ---
    elif st.session_state.pantalla_actual == "Perfil":
        st.markdown("<h4 style='color:#1E3D14;'>👤 Perfil del Usuario</h4>", unsafe_allow_html=True)
        with st.form("edit_profile_form"):
            st.markdown("##### Modificar Datos Personales")
            nuevo_nombre = st.text_input("Nombre de Productor:", value=st.session_state.usuario_actual)
            nueva_ubi = st.text_input("Ubicación / Región Agrícola:", value=st.session_state.ubicacion_actual)
            
            st.markdown("<hr style='border-top:1px solid #ccc; margin:15px 0;'>", unsafe_allow_html=True)
            st.markdown("<h5>Cambiar Contraseña</h5>", unsafe_allow_html=True)
            nueva_clave = st.text_input("Nueva Contraseña:", type="password", placeholder="Dejar en blanco para no modificar")
            confirmar_clave = st.text_input("Confirmar Nueva Contraseña:", type="password", placeholder="Repita contraseña")
            
            if st.form_submit_button("Guardar Cambios"):
                st.session_state.usuario_actual = nuevo_nombre
                st.session_state.ubicacion_actual = nueva_ubi
                if nueva_clave.strip() or confirmar_clave.strip():
                    if nueva_clave != confirmar_clave:
                        st.error("❌ Las contraseñas no coinciden.")
                    else:
                        if cambiar_contrasena_db(st.session_state.username_actual, nueva_clave.strip()):
                            st.success("🔒 ¡Contraseña modificada en la base de datos!")
                        else:
                            st.toast("Modificado localmente.")
                st.rerun()

        if st.button("Cerrar Sesión 🚪", use_container_width=True):
            st.session_state.autenticado = False
            st.session_state.pantalla_auth = "login"
            st.rerun()

# --- CONTROLADOR DE VISTAS ---
if not st.session_state.autenticado:
    render_autentizacion()
else:
    render_dashboard()
