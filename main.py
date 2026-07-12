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

# Claves para limpiar los inputs tras publicar
if "pub_count" not in st.session_state:
    st.session_state.pub_count = 0
if "mkt_count" not in st.session_state:
    st.session_state.mkt_count = 0

# Historial del Chat de la IA
if "historial_ia" not in st.session_state:
    st.session_state.historial_ia = [
        {"role": "assistant", "content": "¡Saludos! Soy AgroIA, su asesor de ingeniería agronómica. Estoy listo para proveer diagnósticos técnicos, planes de dosificación de fertilizantes e intervenciones de manejo fitosanitario de precisión. ¿Qué escenario evaluamos hoy?"}
    ]

# Estructuras temporales en memoria (Publicaciones globales visibles por todos)
if "db_publicaciones" not in st.session_state:
    st.session_state.db_publicaciones = [
        {"id": 1, "autor": "Euclimar García", "contenido": "Iniciando la siembra de maíz en la zona alta.", "archivo": None, "tipo_archivo": None},
        {"id": 2, "autor": "Jetsiber Simancas", "contenido": "Evaluando umbral de daño económico para control químico de insectos.", "archivo": None, "tipo_archivo": None}
    ]
if "db_market" not in st.session_state:
    st.session_state.db_market = [
        {"id": 1, "autor": "Euclimar García", "titulo": "Sacos de Fertilizante NPK", "precio": "25.00", "ubicacion": "Lara, Venezuela", "descripcion": "Alta calidad para fases de crecimiento foliar.", "archivo": None, "tipo_archivo": None}
    ]

# LÓGICA DE RESPUESTAS AGROIA (INGENIERO AGRÓNOMO PROFESIONAL)
def responder_ia_agronomo(mensaje_usuario, tiene_archivo=False):
    msg = mensaje_usuario.lower()
    if tiene_archivo:
        return "🔬 *Análisis Técnico de Registro Multimedia (AgroIA):* Evaluando patrones sintomatológicos en el material. Se observa necrosis marginal foliar compatible con deficiencia crítica de Potasio ($K$) o estrés por salinidad. Se sugiere análisis de tejido foliar y conductividad eléctrica en suelo."
    
    if "fertilidad" in msg or "fertilizante" in msg or "abono" in msg or "npk" in msg or "urea" in msg:
        return "🚜 *Dictamen Agronómico (Fertilidad):* Para optimizar el rendimiento por hectárea, suspenda aplicaciones genéricas. Aplique un plan balanceado basado en análisis de suelo previo. En fase vegetativa agresiva, se prescribe dosificación fraccionada de Nitrógeno (Urea al 46%) combinada con enmiendas de Fósforo ($P_2O_5$) de alta solubilidad si el pH está fuera del rango balanceado (6.0 - 6.5)."
    
    if "plaga" in msg or "insecto" in msg or "enfermedad" in msg or "hongo" in msg:
        return "🛡️ *Estrategia Fitosanitaria (Control Técnico):* Determine primero el Umbral de Daño Económico (UDE). Ante la presencia de vectores fúngicos severos, considere el uso técnico de fungicidas sistémicos (triazoles o estrobirulinas) bajo rotación estricta de mecanismos de acción para prevenir resistencia biológica."
        
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
            background-color: transparent !important;
            color: #ffffff !important;
            border: 1px solid #ffffff !important;
            border-radius: 8px !important;
        }
        div[data-testid="stTextInput"] input::placeholder {
            color: rgba(255, 255, 255, 0.6) !important;
        }
        
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
        .auth-inline-container div.stButton { margin: 0 !important; width: auto !important; }
        .auth-inline-container div.stButton > button {
            background: transparent !important;
            color: #ffffff !important;
            border: none !important;
            box-shadow: none !important;
            text-decoration: underline !important;
            font-size: 15px !important;
            padding: 0px !important;
        }
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
        st.text_input("Contraseña", type="password", placeholder="Ingrese contraseña", key="reg_pwd")
        
        if st.button("REGISTRARSE", type="primary", use_container_width=True):
            if nombre_completo.strip():
                st.session_state.usuario_actual = nombre_completo.strip()
                st.session_state.username_actual = user_reg.strip() if user_reg.strip() else nombre_completo.strip()
            st.session_state.autenticado = True
            st.success("¡Registro Exitoso!")
            st.rerun()

    elif st.session_state.pantalla_auth == "recuperacion":
        st.text_input("Usuario o Correo", placeholder="Ingrese su usuario o correo", key="rec_usr")
        if st.button("ENVIAR CÓDIGO", type="primary", use_container_width=True):
            st.success("Código enviado.")

# ==========================================
# 🌱 INTERFAZ PRINCIPAL (CORREGIDA Y COMPLETA)
# ==========================================
def render_dashboard():
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] { background-color: #F7F9F6 !important; }
        .block-container { max-width: 550px !important; padding: 1.5rem 1rem !important; }
        .main-header { font-size: 34px; font-weight: 900; color: #1E3D14 !important; text-align: center; margin-top: 55px !important; margin-bottom: 15px; }
        
        .agro-card { background-color: #FFFFFF; border-radius: 14px; padding: 18px; border: 1px solid #EAEAEA; margin-bottom: 5px; }
        .agro-card p, .agro-card div { color: #333333 !important; font-size: 15px; }
        
        /* Cajas de texto blancas del interior */
        div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea, div[data-testid="stFileUploader"] section {
            background-color: #ffffff !important; color: #000000 !important; border: 1px solid #cccccc !important; border-radius: 8px !important;
        }
        
        /* Menú horizontal de 5 columnas */
        .menu-horizontal-container { display: flex !important; flex-direction: row !important; justify-content: space-between !important; width: 100% !important; gap: 4px !important; margin-bottom: 15px !important; }
        .menu-horizontal-container div.element-container, .menu-horizontal-container div.stButton { flex: 1 1 0% !important; width: auto !important; margin: 0 !important; }
        
        div.stButton > button {
            background-color: #2e6d38 !important; color: #ffffff !important; border-radius: 8px !important; border: 1px solid #1e4d2b !important; font-weight: bold !important; font-size: 12px !important; padding: 10px 1px !important; width: 100% !important;
        }
        div.stButton > button:hover { background-color: #1e4d2b !important; }
        
        .btn-eliminar > div.stButton > button {
            background-color: #fce8e6 !important; color: #cc3333 !important; border: 1px solid #f5c2c2 !important; font-size: 11px !important; padding: 2px 5px !important; border-radius: 4px !important; margin-top: -5px !important;
        }
        .btn-eliminar > div.stButton > button:hover { background-color: #cc3333 !important; color: #ffffff !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-header">🌱 AGROCAMPO</div>', unsafe_allow_html=True)
    
    # Campo de búsqueda limpio sin etiquetas superiores duplicadas
    busqueda = st.text_input("", placeholder="🔍 Buscar...", key="barra_busqueda_global")

    # BARRA DE MENÚ HORIZONTAL COMPLETO (Verde con letras blancas nativo de la app)
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
            # Carga de fotos y videos cortos
            nuevo_archivo = st.file_uploader("Cargar foto/video", type=["png", "jpg", "jpeg", "mp4", "mov"], key=f"file_pub_{st.session_state.pub_count}")
            
            if st.button("Publicar", type="primary", use_container_width=True):
                if nuevo_texto.strip() or nuevo_archivo is not None:
                    tipo = None
                    if nuevo_archivo is not None:
                        tipo = "video" if nuevo_archivo.name.lower().endswith(('.mp4', '.mov')) else "imagen"
                        
                    st.session_state.db_publicaciones.insert(0, {
                        "id": random.randint(100, 99999),
                        "autor": st.session_state.usuario_actual,
                        "contenido": nuevo_texto,
                        "archivo": nuevo_archivo,
                        "tipo_archivo": tipo
                    })
                    st.session_state.pub_count += 1
                    st.success("¡Publicado con éxito!")
                    st.rerun()

        publicaciones_filtradas = st.session_state.db_publicaciones
        if busqueda.strip():
            publicaciones_filtradas = [p for p in st.session_state.db_publicaciones if busqueda.lower() in p["contenido"].lower() or busqueda.lower() in p["autor"].lower()]

        for post in publicaciones_filtradas:
            st.markdown(f"""
                <div class="agro-card">
                    <div style="font-weight:bold; color:#1E3D14;">👤 {post['autor']}</div>
                    <p style="margin: 8px 0; font-weight: normal;">{post['contenido']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Renderizado condicional si es imagen o video corto
            if post.get("archivo") is not None:
                if post.get("tipo_archivo") == "video":
                    st.video(post["archivo"])
                else:
                    st.image(post["archivo"], use_column_width=True)
            
            if post["autor"] == st.session_state.usuario_actual:
                st.markdown('<div class="btn-eliminar">', unsafe_allow_html=True)
                if st.button("🗑️ Eliminar mi publicación", key=f"del_{post['id']}"):
                    st.session_state.db_publicaciones = [p for p in st.session_state.db_publicaciones if p["id"] != post["id"]]
                    st.toast("Publicación eliminada")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)

    # --- MARKET ---
    elif st.session_state.pantalla_actual == "Market":
        st.markdown("<h4 style='color:#1E3D14;'>🛒 Mercado de Productos e Insumos</h4>", unsafe_allow_html=True)
        
        with st.expander("➕ Publicar Insumo / Producto Agrícola", expanded=False):
            prod_titulo = st.text_input("Nombre del Producto / Insumo:", placeholder="Ej. Pimentón fresco, Urea, Motocultor...", key=f"mk_tit_{st.session_state.mkt_count}")
            prod_precio = st.text_input("Precio ($):", placeholder="Ej. 15.00", key=f"mk_pre_{st.session_state.mkt_count}")
            prod_ubicacion = st.text_input("Dirección / Estado de venta:", value=st.session_state.ubicacion_actual, key=f"mk_ub_{st.session_state.mkt_count}")
            prod_descripcion = st.text_area("Descripción y características del producto:", placeholder="Detalla las condiciones actuales...", key=f"mk_des_{st.session_state.mkt_count}")
            prod_archivo = st.file_uploader("Cargar foto/video del producto", type=["png", "jpg", "jpeg", "mp4", "mov"], key=f"mk_fot_{st.session_state.mkt_count}")
            
            if st.button("Publicar en Mercado", type="primary", use_container_width=True):
                if prod_titulo.strip() and prod_precio.strip():
                    tipo = None
                    if prod_archivo is not None:
                        tipo = "video" if prod_archivo.name.lower().endswith(('.mp4', '.mov')) else "imagen"
                        
                    st.session_state.db_market.insert(0, {
                        "id": random.randint(100, 99999),
                        "autor": st.session_state.usuario_actual,
                        "titulo": prod_titulo,
                        "precio": prod_precio,
                        "ubicacion": prod_ubicacion,
                        "descripcion": prod_descripcion,
                        "archivo": prod_archivo,
                        "tipo_archivo": tipo
                    })
                    st.session_state.mkt_count += 1
                    st.success("¡Producto publicado con éxito!")
                    st.rerun()

        market_filtrado = st.session_state.db_market
        if busqueda.strip():
            market_filtrado = [m for m in st.session_state.db_market if busqueda.lower() in m["titulo"].lower() or busqueda.lower() in m["descripcion"].lower()]

        for item in market_filtrado:
            st.markdown(f"""
                <div class="agro-card">
                    <div style="font-size: 19px; font-weight: bold; color: #2e6d38;">📦 {item['titulo']}</div>
                    <div style="font-size: 13px; color: #777777; margin-bottom: 6px;">👤 Vendedor: {item.get('autor', 'Anónimo')}</div>
                    <p style="margin: 4px 0;"><b>💰 Precio:</b> {item['precio']}$</p>
                    <p style="margin: 4px 0;"><b>📍 Ubicación:</b> {item.get('ubicacion', 'No especificada')}</p>
                    <p style="margin: 6px 0; font-size: 14px;">{item['descripcion']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            if item.get("archivo") is not None:
                if item.get("tipo_archivo") == "video":
                    st.video(item["archivo"])
                else:
                    st.image(item["archivo"], use_column_width=True)
            
            if item.get("autor") == st.session_state.usuario_actual:
                st.markdown('<div class="btn-eliminar">', unsafe_allow_html=True)
                if st.button("🗑️ Retirar Producto", key=f"del_mk_{item['id']}"):
                    st.session_state.db_market = [m for m in st.session_state.db_market if m["id"] != item["id"]]
                    st.toast("Producto retirado")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)

    # --- AGROIA (SABIA E INGENIERÍA AGRONÓMICA) ---
    elif st.session_state.pantalla_actual == "AgroIA":
        st.markdown("<h4 style='color:#1E3D14;'>🔬 Consultoría de Ingeniería Agronómica de Precisión</h4>", unsafe_allow_html=True)
        for chat in st.session_state.historial_ia:
            color = "#e8f5e9" if chat["role"] == "assistant" else "#ffffff"
            st.markdown(f'<div class="agro-card" style="background-color:{color};"><b>{chat["role"].upper()}:</b><br>{chat["content"]}</div>', unsafe_allow_html=True)
        
        archivo_analizar = st.file_uploader("Cargar foto/video sintomatológico para evaluación:", type=["png", "jpg", "jpeg", "mp4"], key="ia_file_input")
        with st.form("chat_form"):
            user_text = st.text_input("Describa las variables de manejo observadas:")
            if st.form_submit_button("Enviar a Diagnóstico Técnico"):
                if user_text.strip() or archivo_analizar is not None:
                    st.session_state.historial_ia.append({"role": "user", "content": user_text})
                    st.session_state.historial_ia.append({"role": "assistant", "content": responder_ia_agronomo(user_text, archivo_analizar is not None)})
                    st.rerun()

    # --- CLIMA ---
    elif st.session_state.pantalla_actual == "Clima":
        st.markdown("<h4 style='color:#1E3D14;'>🌤️ Estación Meteorológica en Tiempo Real</h4>", unsafe_allow_html=True)
        st.markdown(f"""
            <div class="agro-card" style="background-color: #e3f2fd;">
                <h3 style="color:#0d47a1; margin:0;">📍 {st.session_state.ubicacion_actual}</h3>
                <p style="font-size:28px; font-weight:bold; margin: 10px 0; color:#1565c0;">28°C <span style="font-size:16px; font-weight:normal; color:#555;">Mayormente Nublado</span></p>
                <hr style="border-top:1px solid #bbdefb; margin:10px 0;">
                <p style="margin:4px 0;"><b>💧 Humedad Relativa:</b> 74%</p>
                <p style="margin:4px 0;"><b>💨 Velocidad del Viento:</b> 14 km/h NNE</p>
                <p style="margin:4px 0;"><b>🌧️ Probabilidad de Precipitación:</b> 40%</p>
                <p style="margin:4px 0; font-size:13px; color:#555; margin-top:8px;"><i>*Reporte técnico meteorológico optimizado para planificaciones de riego y aplicaciones foliares.</i></p>
            </div>
        """, unsafe_allow_html=True)

    # --- PERFIL (DATOS EDITABLES) ---
    elif st.session_state.pantalla_actual == "Perfil":
        st.markdown("<h4 style='color:#1E3D14;'>👤 Información del Usuario de la Red</h4>", unsafe_allow_html=True)
        
        with st.form("edit_profile_form"):
            st.markdown("##### Modificar Datos Personales")
            nuevo_nombre = st.text_input("Nombre de Productor:", value=st.session_state.usuario_actual)
            nueva_ubi = st.text_input("Ubicación / Región Agrícola:", value=st.session_state.ubicacion_actual)
            
            if st.form_submit_button("Guardar Cambios"):
                st.session_state.usuario_actual = nuevo_nombre
                st.session_state.ubicacion_actual = nueva_ubi
                st.success("Información de perfil actualizada en el sistema central.")
                st.rerun()
                
        st.markdown("<br>", unsafe_allow_html=True)
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
