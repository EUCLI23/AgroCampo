import streamlit as st
import mysql.connector
import random

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

# Historial del Chat de la IA
if "historial_ia" not in st.session_state:
    st.session_state.historial_ia = [
        {"role": "assistant", "content": "¡Hola! Soy AgroIA, tu consultor agrícola integral. Ahora puedo ayudarte con planes de fertilidad, dosificación de abonos, control fitosanitario, insumos químicos o biológicos, y análisis visual de cosechas. ¿En qué puedo colaborarte hoy?"}
    ]

# Estructuras temporales en memoria
if "db_publicaciones" not in st.session_state:
    st.session_state.db_publicaciones = [
        {"id": 1, "autor": "Euclimar García", "contenido": "Iniciando la siembra de maíz en la zona alta.", "imagen": None},
        {"id": 2, "autor": "Jetsiber Simancas", "contenido": "Recomendaciones para el control de plagas orgánico.", "imagen": None}
    ]
if "db_market" not in st.session_state:
    st.session_state.db_market = [
        {"id": 1, "titulo": "Sacos de Fertilizante NPK", "precio": "25.00", "descripcion": "Alta calidad para fases de crecimiento.", "foto": None}
    ]
if "likes_dados" not in st.session_state:
    st.session_state.likes_dados = {}

# LÓGICA DE RESPUESTAS AGROIA
def responder_ia(mensaje_usuario, tiene_foto=False):
    msg = mensaje_usuario.lower()
    if tiene_foto:
        return "📸 *Análisis de Imagen AgroIA:* He recibido la captura de tu cultivo/plaga. Visualmente detecto patrones que podrían asociarse a un déficit nutricional o ataque temprano de áfidos. Te sugiero monitorear el envés de las hojas y verificar si hay clorosis."
    if "fertilidad" in msg or "fertilizante" in msg or "abono" in msg or "npk" in msg:
        return "🌿 *Recomendación de Fertilidad:* Para crecimiento prioriza fuentes altas en Nitrógeno (Urea). Para floración y llenado, requiere Fósforo y Potasio (NPK 12-24-12)."
    elif "plaga" in msg or "insecto" in msg or "veneno" in msg:
        return "🛡️ *Control Fitosanitario:* Para insectos chupadores evalúa aplicaciones técnicas o biológicas como el jabón potásico con extracto de neem."
    return "📋 *Consulta Registrada:* ¿Podrías indicarme la edad actual del cultivo o adjuntar una foto de la anomalía para darte una respuesta exacta?"

# ==========================================
# 🚪 PANEL DE AUTENTICACIÓN (LOGIN - INTACTO)
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
        
        button[kind="primary"] {
            background-color: #4CAF50 !important;
            color: white !important;
            border-radius: 12px !important;
            font-weight: bold !important;
            padding: 0.6rem !important;
        }
        
        .auth-inline-container {
            display: flex !important;
            flex-direction: row !important;
            justify-content: space-between !important;
            align-items: center !important;
            width: 100% !important;
            margin-top: 25px !important;
        }
        .auth-inline-container div.stButton {
            margin: 0 !important;
            width: auto !important;
        }
        .auth-inline-container div.stButton > button {
            background: transparent !important;
            background-color: transparent !important;
            color: #ffffff !important;
            border: none !important;
            box-shadow: none !important;
            text-decoration: underline !important;
            font-size: 15px !important;
            padding: 0px !important;
            outline: none !important;
        }
        .auth-inline-container div.stButton > button:hover, 
        .auth-inline-container div.stButton > button:focus,
        .auth-inline-container div.stButton > button:active {
            background: transparent !important;
            color: #a3cfbb !important;
            border: none !important;
            box-shadow: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.session_state.pantalla_auth == "login":
        st.markdown('<div style="text-align:center; font-size:32px; font-weight:bold; color:white; margin-bottom:20px;">🌱 AgroCampo</div>', unsafe_allow_html=True)
        user_input = st.text_input("Usuario", key="login_user")
        pass_input = st.text_input("Contraseña", type="password", key="login_pass")
        
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
        st.text_input("Nombre Completo", key="reg_nom")
        st.text_input("Nombre de Usuario", key="reg_usr")
        st.text_input("Contraseña", type="password", key="reg_pwd")
        if st.button("REGISTRARSE", type="primary", use_container_width=True):
            st.session_state.autenticado = True
            st.rerun()
        st.markdown('<div class="auth-inline-container" style="justify-content:center;">', unsafe_allow_html=True)
        if st.button("Volver", key="back_reg"):
            st.session_state.pantalla_auth = "login"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.pantalla_auth == "recuperacion":
        st.markdown('<div style="text-align:center; font-size:24px; font-weight:bold; color:white; margin-bottom:20px;">🔑 Recuperar Acceso</div>', unsafe_allow_html=True)
        st.text_input("Usuario o Correo", key="rec_usr")
        if st.button("ENVIAR CÓDIGO", type="primary", use_container_width=True):
            st.success("Código enviado.")
        st.markdown('<div class="auth-inline-container" style="justify-content:center;">', unsafe_allow_html=True)
        if st.button("Volver", key="back_rec"):
            st.session_state.pantalla_auth = "login"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 🌱 INTERFAZ PRINCIPAL
# ==========================================
def render_dashboard():
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] { background-color: #F7F9F6 !important; }
        .block-container { max-width: 550px !important; padding: 1.5rem 1rem !important; }
        
        .main-header { font-size: 34px; font-weight: 900; color: #1E3D14 !important; text-align: center; margin-top: 55px !important; margin-bottom: 15px; }
        
        .agro-card { background-color: #FFFFFF; border-radius: 14px; padding: 18px; border: 1px solid #EAEAEA; margin-bottom: 5px; }
        .agro-card p, .agro-card div { color: #333333 !important; font-size: 15px; }
        
        div[data-testid="stTextInput"] input, 
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stFileUploader"] section {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 1px solid #cccccc !important;
            border-radius: 8px !important;
        }
        
        div[data-testid="stTextInput"] input::placeholder,
        div[data-testid="stTextArea"] textarea::placeholder {
            color: #555555 !important;
        }

        div[data-testid="stFileUploader"] dropzone div {
            color: #000000 !important;
        }
        
        .menu-horizontal-container {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            justify-content: space-between !important;
            align-items: center !important;
            width: 100% !important;
            gap: 6px !important;
            margin-bottom: 15px !important;
        }
        .menu-horizontal-container div.element-container, 
        .menu-horizontal-container div.stButton {
            flex: 1 1 0% !important;
            width: auto !important;
            margin: 0 !important;
        }
        
        div.stButton > button {
            background-color: #2e6d38 !important; 
            color: #ffffff !important; 
            border-radius: 8px !important;
            border: 1px solid #1e4d2b !important; 
            font-weight: bold !important;
            font-size: 13px !important;
            padding: 10px 2px !important;
            width: 100% !important;
            white-space: nowrap !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        }
        
        div.stButton > button:hover,
        div.stButton > button:focus,
        div.stButton > button:active { 
            background-color: #1e4d2b !important; 
            color: #ffffff !important; 
            border: 1px solid #11301a !important;
        }
        
        button[kind="primary"] {
            background-color: #2e6d38 !important;
            color: #ffffff !important;
            border: 1px solid #1e4d2b !important;
            font-weight: bold !important;
        }
        button[kind="primary"]:hover {
            background-color: #1e4d2b !important;
        }
        
        /* Estilo especial y discreto para el botón de eliminar */
        .btn-eliminar > div.stButton > button {
            background-color: #fce8e6 !important;
            color: #cc3333 !important;
            border: 1px solid #f5c2c2 !important;
            font-size: 11px !important;
            padding: 2px 5px !important;
            border-radius: 4px !important;
            margin-top: -5px !important;
        }
        .btn-eliminar > div.stButton > button:hover {
            background-color: #cc3333 !important;
            color: #ffffff !important;
        }

        .btn-logout > div.stButton > button { background-color: #d32f2f !important; color: white !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-header">🌱 AGROCAMPO</div>', unsafe_allow_html=True)
    
    busqueda = st.text_input("🔍 Buscar publicaciones...", placeholder="Buscar...", key="barra_busqueda_global")

    # BARRA DE MENÚ HORIZONTAL
    st.markdown('<div class="menu-horizontal-container">', unsafe_allow_html=True)
    cols_nav = st.columns(4)
    secciones = ["Novedades", "Market", "AgroIA", "Perfil"]
    iconos = ["📰 Novs", "🛒 Mkt", "🤖 IA", "👤 Perf"]
    
    for indice, col in enumerate(cols_nav):
        with col:
            es_activa = secciones[indice] == st.session_state.pantalla_actual
            label = f"✨ {iconos[indice]}" if es_activa else iconos[indice]
            if st.button(label, key=f"nav_top_{secciones[indice]}"):
                st.session_state.pantalla_actual = secciones[indice]
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<hr style='border:0; border-top: 1px solid #ddd; margin: 10px 0;'>", unsafe_allow_html=True)

    # --- CONTENIDO DE LAS PANTALLAS ---
    if st.session_state.pantalla_actual == "Novedades":
        st.markdown("<h4 style='color:#1E3D14;'>Publicaciones de la Comunidad</h4>", unsafe_allow_html=True)
        
        with st.expander("➕ Crear Publicación", expanded=False):
            nuevo_texto = st.text_area("¿Qué está pasando en tu cultivo?", placeholder="Escribe aquí tu estado...", key="txt_nueva_pub")
            nueva_foto = st.file_uploader("Añadir foto (opcional)", type=["png", "jpg", "jpeg"], key="img_nueva_pub")
            
            if st.button("Publicar", type="primary", use_container_width=True, key="btn_guardar_pub"):
                if nuevo_texto.strip() or nueva_foto is not None:
                    st.session_state.db_publicaciones.insert(0, {
                        "id": random.randint(100, 99999), # ID único aleatorio
                        "autor": st.session_state.usuario_actual,
                        "contenido": nuevo_texto,
                        "imagen": nueva_foto
                    })
                    st.success("¡Publicado con éxito!")
                    st.session_state.pantalla_actual = "Novedades"
                    st.rerun()

        # LÓGICA DE BÚSQUEDA FILTRADA
        publicaciones_filtradas = st.session_state.db_publicaciones
        if busqueda.strip():
            publicaciones_filtradas = [
                p for p in st.session_state.db_publicaciones 
                if busqueda.lower() in p["contenido"].lower() or busqueda.lower() in p["autor"].lower()
            ]

        if not publicaciones_filtradas:
            st.info("❌ No encontrado")
        else:
            for post in publicaciones_filtradas:
                st.markdown(f"""
                    <div class="agro-card">
                        <div style="font-weight:bold; color:#1E3D14;">👤 {post['autor']}</div>
                        <p style="margin: 8px 0; font-weight: normal;">{post['contenido']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                if post.get("imagen") is not None:
                    st.image(post["imagen"], use_column_width=True)
                
                # AJUSTE: Si el usuario actual es el dueño, se le renderiza el botón de eliminar abajo de la card
                if post["autor"] == st.session_state.usuario_actual:
                    st.markdown('<div class="btn-eliminar">', unsafe_allow_html=True)
                    if st.button("🗑️ Eliminar mi publicación", key=f"del_{post['id']}", use_container_width=False):
                        st.session_state.db_publicaciones = [p for p in st.session_state.db_publicaciones if p["id"] != post["id"]]
                        st.toast("Publicación eliminada")
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)

    elif st.session_state.pantalla_actual == "Market":
        for item in st.session_state.db_market:
            st.markdown(f"""
                <div class="agro-card">
                    <div style="font-size: 18px; font-weight: bold; color: #2e6d38;">📦 {item['titulo']}</div>
                    <p style="margin: 4px 0;"><b>Precio:</b> {item['precio']}$</p>
                    <p style="margin: 0; font-size: 14px;">{item['descripcion']}</p>
                </div>
            """, unsafe_allow_html=True)

    elif st.session_state.pantalla_actual == "AgroIA":
        st.markdown("<h4 style='color:#1E3D14;'>🤖 AgroIA</h4>", unsafe_allow_html=True)
        for chat in st.session_state.historial_ia:
            color = "#e8f5e9" if chat["role"] == "assistant" else "#ffffff"
            st.markdown(f'<div class="agro-card" style="background-color:{color};"><b>{chat["role"].upper()}:</b><br>{chat["content"]}</div>', unsafe_allow_html=True)
        
        imagen_capturada = st.camera_input("Tomar foto de la cosecha/plaga:")
        with st.form("chat_form"):
            user_text = st.text_input("Tu consulta:")
            if st.form_submit_button("Enviar"):
                if user_text.strip() or imagen_capturada:
                    st.session_state.historial_ia.append({"role": "user", "content": user_text})
                    st.session_state.historial_ia.append({"role": "assistant", "content": responder_ia(user_text, imagen_capturada is not None)})
                    st.rerun()

    elif st.session_state.pantalla_actual == "Perfil":
        st.markdown("<h4 style='color:#1E3D14;'>⚙️ Perfil</h4>")
        if st.button("Cerrar Sesión 🚪", use_container_width=True):
            st.session_state.autenticado = False
            st.session_state.pantalla_auth = "login"
            st.rerun()

# ==========================================
# 🚦 CONTROLADOR DE VISTAS
# ==========================================
if not st.session_state.autenticado:
    render_autentizacion()
else:
    render_dashboard()
