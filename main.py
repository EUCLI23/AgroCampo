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
        {"id": 1, "autor": "Euclimar García", "contenido": "Iniciando la siembra de maíz en la zona alta.", "likes": 5, "comentarios": ["¡Mucho éxito!", "Excelente zona"]},
        {"id": 2, "autor": "Jetsiber Simancas", "contenido": "Recomendaciones para el control de plagas orgánico.", "likes": 12, "comentarios": ["Me sirvió mucho."]}
    ]
if "db_market" not in st.session_state:
    st.session_state.db_market = [
        {"id": 1, "titulo": "Sacos de Fertilizante NPK", "precio": "25.00", "descripcion": "Alta calidad para fases de crecimiento.", "foto": None}
    ]
if "likes_dados" not in st.session_state:
    st.session_state.likes_dados = {}

# LÓGICA DE RESPUESTAS AMPLIADA DE AGROIA (Soporte de Fertilidad, Insumos y Fotos)
def responder_ia(mensaje_usuario, tiene_foto=False):
    msg = mensaje_usuario.lower()
    
    if tiene_foto:
        return "📸 *Análisis de Imagen AgroIA:* He recibido la captura de tu cultivo/plaga. Visualmente detecto patrones que podrían asociarse a un déficit nutricional o ataque temprano de áfidos. Te sugiero monitorear el envés de las hojas y verificar si hay clorosis. ¿Qué síntomas o coloración notas tú prioritariamente?"

    if "fertilidad" in msg or "fertilizante" in msg or "abono" in msg or "npk" in msg or "nutricion" in msg:
        return "🌿 *Recomendación de Fertilidad y Suelos:* Para maximizar el rendimiento, es crucial un plan basado en la etapa fenológica. En vegetativo, prioriza fuentes altas en Nitrógeno (Urea o Nitrato de Amonio). Para floración y llenado, requiere Fósforo y Potasio (NPK 12-24-12 o similar). Si buscas opciones orgánicas, el humus líquido o compost maduro aportan excelentes ácidos húmicos."
    
    elif "plaga" in msg or "insecto" in msg or "enfermedad" in msg or "veneno" in msg or "hongo" in msg:
        return "🛡️ *Control Fitosanitario:* Si presentas ataques severos de insectos chupadores (como mosca blanca o pulgón), puedes evaluar aplicaciones técnicas controladas o alternativas biológicas como el jabón potásico con extracto de neem. Si es un hongo (antracnosis, mildiu), aplica fungicidas a base de cobre respetando los tiempos de carencia antes de la cosecha."
    
    elif "maiz" in msg or "maíz" in msg:
        return "🌽 *Manejo de Maíz:* Requiere un suelo con excelente drenaje. Recuerda aplicar el primer reabono nitrogenado entre los 20 y 25 días después de la emergencia (etapa V4-V6) para asegurar el vigor del tallo."
    
    elif "lara" in msg or "clima" in msg:
        return "📍 *Condiciones Regionales (Lara):* Dadas las características de suelos y clima de la región, optimiza los riegos en las horas frescas y vigila la salinidad si utilizas aguas de pozo profundo."
    
    else:
        return "📋 *Consulta Registrada:* Interesante planteamiento sobre tu agro-ecosistema. Para darte una dosificación precisa por hectárea o un tratamiento fitosanitario exacto, ¿podrías indicarme la edad actual del cultivo o adjuntar una foto de la anomalía?"

# ==========================================
# 🚪 PANEL DE AUTENTICACIÓN (FILA INLINE FORZADA)
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
            box-shadow: 0 15px 30px rgba(0,0,0,0.5);
        }
        h1, h2, h3, p, div[data-testid="stWidgetLabel"] p { color: #ffffff !important; font-weight: 500 !important; }
        
        button[kind="primary"] {
            background-color: #4CAF50 !important;
            color: white !important;
            border-radius: 12px !important;
            font-weight: bold !important;
            padding: 0.6rem !important;
            border: none !important;
        }
        
        /* Contenedor Flex para obligar a los botones a estar uno al lado del otro en móvil */
        .auth-inline-container {
            display: flex !important;
            flex-direction: row !important;
            justify-content: space-between !important;
            align-items: center !important;
            width: 100% !important;
            margin-top: 20px !important;
            gap: 10px;
        }
        .auth-inline-container div.stButton {
            width: auto !important;
            margin: 0 !important;
        }
        .auth-inline-container div.stButton > button {
            background: transparent !important;
            color: #a3cfbb !important;
            border: none !important;
            box-shadow: none !important;
            text-decoration: underline !important;
            font-size: 14px !important;
            padding: 5px !important;
            white-space: nowrap !important;
        }
        .auth-inline-container div.stButton > button:hover {
            color: #ffffff !important;
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
            
        # CONTENEDOR FLEX INLINE FORZADO PARA MÓVIL
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
        st.markdown('<div style="text-align:center; font-size:26px; font-weight:bold; color:white; margin-bottom:20px;">📝 Registro de Productor</div>', unsafe_allow_html=True)
        reg_nombre = st.text_input("Nombre Completo", key="reg_nom")
        reg_user = st.text_input("Nombre de Usuario", key="reg_usr")
        reg_pass = st.text_input("Contraseña", type="password", key="reg_pwd")
        reg_ubi = st.text_input("Ubicación (Ej: Lara, Venezuela)", key="reg_ubc")
        
        if st.button("REGISTRARSE", type="primary", use_container_width=True):
            if reg_nombre.strip() and reg_user.strip() and reg_pass.strip():
                st.session_state.usuario_actual = reg_nombre
                st.session_state.username_actual = reg_user
                st.session_state.ubicacion_actual = reg_ubi if reg_ubi.strip() else "Lara, Venezuela"
                st.session_state.autenticado = True
                st.success("¡Cuenta creada exitosamente!")
                st.rerun()
            else:
                st.error("Por favor rellene los campos obligatorios.")
                
        st.markdown('<div class="auth-inline-container" style="justify-content:center;">', unsafe_allow_html=True)
        if st.button("Volver al Inicio de Sesión", key="back_to_login_reg"):
            st.session_state.pantalla_auth = "login"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.pantalla_auth == "recuperacion":
        st.markdown('<div style="text-align:center; font-size:24px; font-weight:bold; color:white; margin-bottom:20px;">🔑 Recuperar Acceso</div>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:14px; text-align:center;">Introduzca su usuario o correo para verificar sus datos.</p>', unsafe_allow_html=True)
        rec_user = st.text_input("Usuario o Correo Electrónico", key="rec_usr")
        
        if st.button("ENVIAR CÓDIGO", type="primary", use_container_width=True):
            if rec_user.strip():
                st.success(f"Código enviado a: {rec_user}")
            else:
                st.error("Por favor introduzca su usuario.")
                
        st.markdown('<div class="auth-inline-container" style="justify-content:center;">', unsafe_allow_html=True)
        if st.button("Volver al Inicio de Sesión", key="back_to_login_rec"):
            st.session_state.pantalla_auth = "login"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 🌱 INTERFAZ PRINCIPAL (DASHBOARD RESPONSIVO)
# ==========================================
def render_dashboard():
    # CSS Adaptativo Avanzado con Flexbox nativo para el menú de navegación superior
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] { background-color: #F7F9F6 !important; }
        .block-container { background-color: transparent !important; box-shadow: none !important; padding: 1.5rem 1rem !important; max-width: 550px !important; }
        .main-header { font-size: 34px; font-weight: 900; color: #1E3D14 !important; text-align: center; margin-bottom: 5px; letter-spacing: 1px; }
        .agro-card { background-color: #FFFFFF; border-radius: 14px; padding: 18px; border: 1px solid #EAEAEA; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
        .post-author { font-weight: bold; color: #1E3D14; font-size: 15px; }
        
        label, div[data-testid="stWidgetLabel"] p { color: #1E3D14 !important; font-weight: 600 !important; }
        .stMarkdown p, p, span { color: #333333 !important; }
        
        /* FORZAR MENÚ HORIZONTAL SIEMPRE (PC Y MÓVIL) */
        .menu-horizontal-container {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            justify-content: space-between !important;
            align-items: center !important;
            width: 100% !important;
            gap: 6px !important;
            margin-bottom: 10px !important;
        }
        .menu-horizontal-container div.element-container, 
        .menu-horizontal-container div.stButton {
            flex: 1 1 0% !important;
            width: auto !important;
            margin: 0 !important;
        }
        .menu-horizontal-container div.stButton > button {
            background-color: #2e6d38 !important; 
            color: white !important; 
            border-radius: 8px !important;
            border: 1px solid #1e4d2b !important; 
            font-weight: bold !important;
            font-size: 12px !important; /* Optimizado para ajustar texto en móvil */
            padding: 8px 2px !important;
            width: 100% !important;
            white-space: nowrap !important;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .menu-horizontal-container div.stButton > button:hover { 
            background-color: #24572c !important; 
            color: white !important; 
        }
        
        .btn-logout > div.stButton > button { background-color: #d32f2f !important; border: 1px solid #b71c1c !important; color: white !important;}
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-header">🌱 AGROCAMPO</div>', unsafe_allow_html=True)
    busqueda = st.text_input("🔍 Buscar publicaciones, productos o amigos...", placeholder="Ej. Maíz, Lara, Fertilizante...", key="barra_busqueda_global")

    # CONTENEDOR FLEX INLINE FORZADO PARA MENÚ SUPERIOR ADAPTATIVO
    st.markdown('<div class="menu-horizontal-container">', unsafe_allow_html=True)
    cols_nav = st.columns(4)
    secciones = ["Novedades", "Market", "AgroIA", "Perfil"]
    iconos = ["📰 Novs", "🛒 Mkt", "🤖 IA", "👤 Perf"] # Textos cortos para evitar desbordes en celulares chicos
    
    for indice, col in enumerate(cols_nav):
        with col:
            es_activa = secciones[indice] == st.session_state.pantalla_actual
            label = f"✨ {iconos[indice]}" if es_activa else iconos[indice]
            if st.button(label, key=f"nav_top_{secciones[indice]}"):
                st.session_state.pantalla_actual = secciones[indice]
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<hr style='border:0; border-top: 1px solid #ddd; margin: 10px 0;'>", unsafe_allow_html=True)

    # --- PANTALLA: NOVEDADES ---
    if st.session_state.pantalla_actual == "Novedades":
        with st.expander("📝 Compartir algo con la comunidad agrícola"):
            nuevo_post = st.text_area("¿Qué está pasando en tus tierras?", placeholder="Escribe aquí tu actualización...", key="txt_nuevo_post")
            if st.button("Publicar al Instante", key="btn_publicar_post", use_container_width=True):
                if nuevo_post.strip():
                    st.session_state.db_publicaciones.insert(0, {
                        "id": len(st.session_state.db_publicaciones) + 1,
                        "autor": st.session_state.usuario_actual,
                        "contenido": nuevo_post,
                        "likes": 0,
                        "comentarios": []
                    })
                    st.success("¡Publicado con éxito!")
                    st.rerun()

        st.markdown("<h4 style='color:#1E3D14;'>Publicaciones de la Comunidad</h4>", unsafe_allow_html=True)
        for post in st.session_state.db_publicaciones:
            if busqueda.lower() in post["contenido"].lower() or busqueda.lower() in post["autor"].lower():
                st.markdown(f"""
                    <div class="agro-card">
                        <div class="post-author">👤 {post['autor']}</div>
                        <p style="margin: 8px 0; font-size:15px;">{post['contenido']}</p>
                        <small style="color: #666666;">👍 {post['likes']} Me gusta &nbsp;|&nbsp; 💬 {len(post['comentarios'])} Comentarios</small>
                    </div>
                """, unsafe_allow_html=True)
                
                col_lk, col_cm = st.columns([1, 2])
                with col_lk:
                    llave_like = f"{st.session_state.username_actual}_{post['id']}"
                    ya_dio_like = st.session_state.likes_dados.get(llave_like, False)
                    if st.button("👍 Like" if not ya_dio_like else "✅ Ok", key=f"like_{post['id']}", use_container_width=True):
                        if not ya_dio_like:
                            post["likes"] += 1
                            st.session_state.likes_dados[llave_like] = True
                            st.rerun()
                with col_cm:
                    with st.popover("💬 Comentar", key=f"popover_{post['id']}", use_container_width=True):
                        nuevo_comentario = st.text_input("Escribe tu comentario", key=f"in_com_{post['id']}")
                        if st.button("Enviar", key=f"btn_com_{post['id']}", use_container_width=True):
                            if nuevo_comentario.strip():
                                post["comentarios"].append(f"{st.session_state.usuario_actual}: {nuevo_comentario}")
                                st.rerun()

    # --- PANTALLA: MARKET ---
    elif st.session_state.pantalla_actual == "Market":
        with st.expander("🛒 Publicar un producto en venta"):
            prod_titulo = st.text_input("Nombre del Producto", key="market_titulo")
            prod_precio = st.text_input("Precio ($)", key="market_precio")
            prod_desc = st.text_area("Descripción", key="market_desc")
            
            if st.button("Lanzar al Mercado", key="btn_market_lanzar", use_container_width=True):
                if prod_titulo.strip() and prod_precio.strip():
                    st.session_state.db_market.insert(0, {
                        "id": len(st.session_state.db_market) + 1,
                        "titulo": prod_titulo,
                        "precio": prod_precio,
                        "descripcion": prod_desc,
                        "foto": None
                    })
                    st.success("¡Producto listado con éxito!")
                    st.rerun()

        for item in st.session_state.db_market:
            if busqueda.lower() in item["titulo"].lower() or busqueda.lower() in item["descripcion"].lower():
                st.markdown(f"""
                    <div class="agro-card">
                        <div style="font-size: 18px; font-weight: bold; color: #2e6d38;">📦 {item['titulo']}</div>
                        <div style="font-size: 16px; font-weight: bold; margin: 4px 0;">Precio: {item['precio']}$</div>
                        <p style="margin: 0; font-size: 14px;">{item['descripcion']}</p>
                    </div>
                """, unsafe_allow_html=True)

    # --- PANTALLA: 🤖 AGROIA (Soporte Técnico de Fertilidad y Captura de Foto) ---
    elif st.session_state.pantalla_actual == "AgroIA":
        st.markdown("<h4 style='color:#1E3D14;'>🤖 Consultor Fitosanitario y de Fertilidad</h4>", unsafe_allow_html=True)
        
        # Historial de chat en pantalla
        for chat in st.session_state.historial_ia:
            if chat["role"] == "assistant":
                st.markdown(f"""
                    <div style="background-color: #e8f5e9; padding: 12px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #2e6d38;">
                        <b style="color: #1e4d2b;">🤖 AgroIA:</b><br>{chat['content']}
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div style="background-color: #ffffff; padding: 12px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #1E3D14; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                        <b style="color: #333;">👤 Tú:</b><br>{chat['content']}
                    </div>
                """, unsafe_allow_html=True)
        
        # Módulo de Captura de Fotos integrado para móviles y PC
        with st.expander("📸 Diagnóstico por Imagen (Tomar foto de cosecha / plaga)"):
            imagen_capturada = st.camera_input("Enfoque la hoja, plaga o fruto afectado:")
            if imagen_capturada:
                st.image(imagen_capturada, caption="Muestra cargada para análisis técnico", width=250)

        with st.form("form_chat_ia", clear_on_submit=True):
            entrada_usuario = st.text_input("Pregunta sobre abonos, dosis, plagas o insumos químicos/biológicos:", placeholder="Ej. ¿Qué dosis de NPK uso o qué veneno controla el hongo?")
            enviar_chat = st.form_submit_button("Consultar con AgroIA", use_container_width=True)
            
            if enviar_chat:
                ha_subido_foto = imagen_capturada is not None
                texto_final = entrada_usuario if entrada_usuario.strip() else ("Análisis de imagen capturada" if ha_subido_foto else "")
                
                if texto_final:
                    st.session_state.historial_ia.append({"role": "user", "content": texto_final})
                    respuesta = responder_ia(texto_final, tiene_foto=ha_subido_foto)
                    st.session_state.historial_ia.append({"role": "assistant", "content": respuesta})
                    st.rerun()

    # --- PANTALLA: PERFIL ---
    elif st.session_state.pantalla_actual == "Perfil":
        st.markdown("<h4 style='color:#1E3D14;'>⚙️ Perfil Profesional</h4>", unsafe_allow_html=True)
        with st.form("form_perfil"):
            nuevo_nombre = st.text_input("Modificar Nombre", value=st.session_state.usuario_actual)
            nueva_ubicacion = st.text_input("Modificar Ubicación", value=st.session_state.ubicacion_actual)
            if st.form_submit_button("Guardar Cambios", use_container_width=True):
                st.session_state.usuario_actual = nuevo_nombre
                st.session_state.ubicacion_actual = nueva_ubicacion
                st.success("¡Datos actualizados!")
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="btn-logout">', unsafe_allow_html=True)
        if st.button("Cerrar Sesión 🚪", key="btn_logout_action", use_container_width=True):
            st.session_state.autenticado = False
            st.session_state.pantalla_auth = "login"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 🚦 CONTROLADOR DE VISTAS
# ==========================================
if not st.session_state.autenticado:
    render_autentizacion()
else:
    render_dashboard()
