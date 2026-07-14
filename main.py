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

# --- FUNCIONES DE BASE DE DATOS PARA PUBLICACIONES ---
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
    st.session_state.pub_count = 0
if "mkt_count" not in st.session_state:
    st.session_state.mkt_count = 0
if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0  

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
        return "🔬 *Análisis Técnico de Registro Multimedia (AgroIA):* Evaluando patrones sintomatológicos en el material visual suministrado. Se observa una carga potencial de maleza densa o anomalías foliares. Se recomienda un control cultural/mecánico inicial previo al trasplante y el monitoreo de plagas asociadas al monte."
    if "fertilidad" in msg or "fertilizante" in msg or "abono" in msg or "npk" in msg or "urea" in msg:
        return "🚜 *Dictamen Agronómico (Fertilidad):* Para optimizar el rendimiento por hectárea, suspenda aplicaciones genéricas. Aplique un plan balanceado basado en análisis de suelo previo. En fase vegetativa agresiva, se prescribe dosificación fraccionada de Nitrógeno (Urea al 46%) combinada con enmiendas de Fósforo ($P_2O_5$) de alta solubilidad si el pH está fuera del rango balanceado (6.0 - 6.5)."
    if "plaga" in msg or "insecto" in msg or "enfermedad" in msg or "hongo" in msg or "monte" in msg or "maleza" in msg:
        return "🛡️ *Estrategia Fitosanitaria (Manejo de Malezas y Suelo):* Ante la presencia de alta densidad de maleza ('mucho monte') previo a la siembra de pimentón, se sugiere realizar un desmalezado mecánico o rastreo para incorporar la materia orgánica, o evaluar una aplicación localizada de herbicida si el umbral lo requiere. Esto evitará la competencia por nutrientes y luz con las plántulas."
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
        region_reg = st.text_input("Ubicación / Región Agrícola", placeholder="Ej. El Tostao, Barquisimeto", key="reg_ubi")
        st.text_input("Contraseña", type="password", placeholder="Ingrese contraseña", key="reg_pwd")
        
        if st.button("REGISTRARSE", type="primary", use_container_width=True):
            if nombre_completo.strip() and user_reg.strip():
                st.session_state.usuario_actual = nombre_completo.strip()
                st.session_state.username_actual = user_reg.strip()
                if region_reg.strip():
                    st.session_state.ubicacion_actual = region_reg.strip()
                else:
                    st.session_state.ubicacion_actual = "No especificada"
                st.session_state.autenticado = True
                st.success(f"¡Registro Exitoso! Bienvenido/a, {st.session_state.usuario_actual}")
                st.rerun()
            else:
                st.error("Por favor, rellene los campos obligatorios (Nombre y Usuario).")

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
        
        .agro-card { background-color: #FFFFFF; border-radius: 14px; padding: 18px; border: 1px solid #EAEAEA; margin-bottom: 5px; position: relative; }
        .agro-card p, .agro-card div { color: #333333 !important; font-size: 15px; }
        
        .chat-card { border-radius: 14px; padding: 18px; border: 1px solid #EAEAEA; margin-bottom: 10px; }
        .chat-card p, .chat-card span, .chat-card b, .chat-card div { color: #111111 !important; font-size: 15px !important; }
        
        /* Etiquetas exteriores en verde oscuro nítido */
        div[data-testid="stWidgetLabel"] p, label p { 
            color: #1E3D14 !important; 
            font-weight: bold !important; 
        }
        
        /* Texto digitado dentro de inputs y áreas de texto */
        div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {
            background-color: #ffffff !important; 
            color: #000000 !important; 
            border: 1px solid #cccccc !important; 
            border-radius: 8px !important;
        }
        
        /* --- 🛠️ CORRECCIÓN DEFINITIVA DE LA CAJA DE SUBIDA DE ARCHIVOS (IMAGEN 10) --- */
        /* Forzamos que el fondo del contenedor del uploader sea blanco o gris muy claro */
        div[data-testid="stFileUploader"] section {
            background-color: #ffffff !important;
            border: 1px dashed #2e6d38 !important;
            border-radius: 10px !important;
            padding: 15px !important;
        }

        /* Todos los textos internos del uploader en color negro nítido */
        div[data-testid="stFileUploader"] section div[data-testid="stMarkdownContainer"] p,
        div[data-testid="stFileUploader"] small,
        div[data-testid="stFileUploader"] span {
            color: #111111 !important;
            font-weight: 500 !important;
        }

        /* Botón interno "Browse files" estilizado correctamente en verde sin textos rotos ni sobrepuestos */
        div[data-testid="stFileUploader"] button {
            background-color: #2e6d38 !important;
            color: #ffffff !important;
            border: 1px solid #1e4d2b !important;
            border-radius: 8px !important;
            font-weight: bold !important;
            padding: 6px 14px !important;
        }
        div[data-testid="stFileUploader"] button:hover {
            background-color: #1e4d2b !important;
        }
        /* -------------------------------------------------------------------------- */
        
        /* Expanders verdes */
        div[data-testid="stExpander"] details summary {
            background-color: #2e6d38 !important;
            border-radius: 8px !important;
            border: none !important;
        }
        div[data-testid="stExpander"] details summary:hover {
            background-color: #1e4d2b !important;
        }
        div[data-testid="stExpander"] details summary p {
            color: #ffffff !important;
            font-weight: bold !important;
            font-size: 16px !important;
        }
        div[data-testid="stExpander"] details summary svg {
            color: #ffffff !important;
            fill: #ffffff !important;
        }
        
        .menu-horizontal-container { display: flex !important; flex-direction: row !important; justify-content: space-between !important; width: 100% !important; gap: 4px !important; margin-bottom: 15px !important; }
        .menu-horizontal-container div.element-container, .menu-horizontal-container div.stButton { flex: 1 1 0% !important; width: auto !important; margin: 0 !important; }
        
        div.stButton > button {
            background-color: #2e6d38 !important; color: #ffffff !important; border-radius: 8px !important; border: 1px solid #1e4d2b !important; font-weight: bold !important; font-size: 12px !important; padding: 10px 1px !important; width: 100% !important;
        }
        div.stButton > button:hover { background-color: #1e4d2b !important; }
        
        div[data-testid="stPopover"] > button {
            background-color: transparent !important;
            color: #777777 !important;
            border: none !important;
            font-size: 18px !important;
            padding: 0px !important;
            font-weight: bold !important;
            float: right;
            margin-top: -10px;
        }
        div[data-testid="stPopover"] > button:hover { color: #1E3D14 !important; background-color: transparent !important; }
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
            
            pub_media = st.file_uploader("Subir foto o video (Opcional):", type=["png", "jpg", "jpeg", "mp4", "mov"], key=f"media_pub_{st.session_state.pub_count}")
            
            add_ubi = st.checkbox("📍 Agregar ubicación geográfica", key=f"chk_ubi_{st.session_state.pub_count}")
            pub_ubicacion = ""
            if add_ubi:
                pub_ubicacion = st.text_input("Ubicación del cultivo:", placeholder="Ej. El Tostao, Barquisimeto", key=f"inp_ubi_{st.session_state.pub_count}")
            
            if st.button("Publicar", type="primary", use_container_width=True):
                if nuevo_texto.strip() or pub_media is not None:
                    exito = guardar_publicacion_db(st.session_state.usuario_actual, nuevo_texto, pub_ubicacion)
                    if exito:
                        st.session_state.pub_count += 1
                        st.success("¡Publicado y guardado en MySQL con éxito!")
                        st.rerun()
                    else:
                        st.session_state.pub_count += 1
                        st.toast("Guardado en modo local temporal.")
                        st.rerun()

        db_publicaciones = listar_publicaciones_db()
        
        if not db_publicaciones:
            db_publicaciones = [
                {"id": -1, "autor": "Euclimar García", "contenido": "Iniciando la siembra de maíz en la zona alta.", "ubicacion": "Lara, Venezuela"},
                {"id": -2, "autor": "Jetsiber Simancas", "contenido": "Evaluando umbral de daño económico para control químico de insectos.", "ubicacion": ""}
            ]

        if busqueda.strip():
            db_publicaciones = [p for p in db_publicaciones if busqueda.lower() in p["contenido"].lower() or busqueda.lower() in p["autor"].lower()]

        for post in db_publicaciones:
            with st.container():
                col_autor, col_menu = st.columns([0.85, 0.15])
                
                with col_autor:
                    if post.get('ubicacion'):
                        st.markdown(f"""
                            <div style="font-weight:bold; color:#1E3D14; margin-bottom: 2px;">👤 {post['autor']}</div>
                            <div style="font-size:12px; color:#666666; margin-bottom: 8px;">📍 {post['ubicacion']}</div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div style="font-weight:bold; color:#1E3D14; margin-bottom: 8px;">👤 {post["autor"]}</div>', unsafe_allow_html=True)
                
                with col_menu:
                    if post["autor"] == st.session_state.usuario_actual and post["id"] > 0:
                        with st.popover("···", help="Opciones de publicación"):
                            st.markdown("<p style='font-weight:bold; margin-bottom:2px;'>📝 Editar publicación</p>", unsafe_allow_html=True)
                            texto_editated = st.text_area("Modificar contenido:", value=post['contenido'], key=f"edit_txt_{post['id']}")
                            
                            if st.button("Guardar cambios", key=f"save_{post['id']}", use_container_width=True):
                                if editar_publicacion_db(post['id'], texto_editated):
                                    st.success("¡Actualizado en MySQL!")
                                    st.rerun()
                                
                            st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
                            
                            if st.button("🗑️ Eliminar publicación", key=f"del_{post['id']}", type="primary", use_container_width=True):
                                if eliminar_publicacion_db(post['id']):
                                    st.toast("Publicación eliminada de la BD")
                                    st.rerun()

                st.markdown(f"""
                    <div class="agro-card" style="margin-top:-10px;">
                        <p style="margin: 0; font-weight: normal;">{post['contenido']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)

    # --- MARKET ---
    elif st.session_state.pantalla_actual == "Market":
        st.markdown("<h4 style='color:#1E3D14;'>🛒 Mercado de Productos e Insumos</h4>", unsafe_allow_html=True)
        
        with st.expander("➕ Publicar Insumo / Producto Agrícola", expanded=False):
            prod_titulo = st.text_input("Nombre del Producto / Insumo:", placeholder="Ej. Pimentón fresco, Urea, Motocultor...", key=f"mk_tit_{st.session_state.mkt_count}")
            prod_precio = st.text_input("Precio ($):", placeholder="Ej. 25.00", key=f"mk_pre_{st.session_state.mkt_count}")
            prod_ubicacion = st.text_input("Dirección / Estado de venta:", value=st.session_state.ubicacion_actual, key=f"mk_ub_{st.session_state.mkt_count}")
            prod_descripcion = st.text_area("Descripción y características del producto:", placeholder="Detalla las condiciones actuales...", key=f"mk_des_{st.session_state.mkt_count}")
            prod_imagen = st.file_uploader("Subir foto del producto:", type=["png", "jpg", "jpeg"], key=f"mk_img_{st.session_state.mkt_count}")
            
            if st.button("Publicar en Mercado", type="primary", use_container_width=True):
                if prod_titulo.strip() and prod_precio.strip():
                    st.session_state.db_market.insert(0, {
                        "id": random.randint(100, 99999),
                        "autor": st.session_state.usuario_actual,
                        "titulo": prod_titulo,
                        "precio": prod_precio,
                        "ubicacion": prod_ubicacion,
                        "descripcion": prod_descripcion,
                        "imagen": prod_imagen
                    })
                    st.session_state.mkt_count += 1
                    st.success("¡Producto publicado con éxito!")
                    st.rerun()

        market_filtrado = st.session_state.db_market
        if busqueda.strip():
            market_filtrado = [m for m in st.session_state.db_market if busqueda.lower() in m["titulo"].lower() or busqueda.lower() in m["descripcion"].lower()]

        for item in market_filtrado:
            st.markdown(f"""
                <div class="agro-card" style="margin-bottom: 10px;">
                    <div style="font-size: 19px; font-weight: bold; color: #2e6d38; margin-bottom: 4px;">📦 {item['titulo']}</div>
                    <div style="font-size: 13px; color: #777777; margin-bottom: 6px;"><b>👤 Vendedor:</b> {item.get('autor', 'Anónimo')}</div>
                    <p style="margin: 4px 0;"><b>💰 Precio:</b> {item['precio']}$</p>
                    <p style="margin: 4px 0;"><b>📍 Ubicación:</b> {item.get('ubicacion', 'No especificada')}</p>
                    <p style="margin: 6px 0; font-size: 14px;">{item['descripcion']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            if item.get("imagen") is not None:
                st.image(item["imagen"], use_container_width=True)
            
            if item.get("autor") == st.session_state.usuario_actual:
                if st.button("🗑️ Retirar Producto", key=f"del_mk_{item['id']}", use_container_width=True):
                    st.session_state.db_market = [m for m in st.session_state.db_market if m["id"] != item["id"]]
                    st.toast("Producto retirado")
                    st.rerun()
            st.markdown("<hr style='border-top:1px solid #ddd; margin:15px 0;'>", unsafe_allow_html=True)

    # --- AGROIA ---
    elif st.session_state.pantalla_actual == "AgroIA":
        st.markdown("<h4 style='color:#1E3D14;'>🔬 Consultoría de Ingeniería Agronómica de Precisión</h4>", unsafe_allow_html=True)
        
        for chat in st.session_state.historial_ia:
            bg_color = "#e8f5e9" if chat["role"] == "assistant" else "#ffffff"
            st.markdown(f"""
                <div class="chat-card" style="background-color: {bg_color}; margin-bottom: 8px;">
                    <span style="font-weight: bold; color: #1E3D14;">{chat["role"].upper()}:</span><br>
                    <span style="font-weight: normal;">{chat["content"]}</span>
                </div>
            """, unsafe_allow_html=True)
            
            if chat.get("imagen") is not None:
                st.image(chat["imagen"], caption="Archivo adjuntado a la consulta", width=250)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.form("chat_form", clear_on_submit=False):
            user_text = st.text_input(
                "Describa las variables de manejo observadas para evaluar:", 
                key=f"ia_input_text_{st.session_state.chat_count}"
            )
            
            foto_ia = st.file_uploader(
                "Subir foto al asistente (Opcional):", 
                type=["png", "jpg", "jpeg"], 
                key=f"ia_input_file_{st.session_state.chat_count}"
            )
            
            if st.form_submit_button("Enviar a Diagnóstico Técnico"):
                if user_text.strip() or foto_ia is not None:
                    texto_usuario = user_text if user_text.strip() else "*(Envió una imagen para evaluación técnica)*"
                    st.session_state.historial_ia.append({
                        "role": "user", 
                        "content": texto_usuario,
                        "imagen": foto_ia
                    })
                    
                    tiene_imagen = (foto_ia is not None)
                    respuesta = responder_ia_agronomo(user_text, tiene_archivo=tiene_imagen)
                    
                    st.session_state.historial_ia.append({
                        "role": "assistant", 
                        "content": respuesta,
                        "imagen": None
                    })
                    
                    st.session_state.chat_count += 1
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
            </div>
        """, unsafe_allow_html=True)

    # --- PERFIL ---
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
