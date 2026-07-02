import streamlit as st
from streamlit_option_menu import option_menu
import mysql.connector
import requests
import base64
from PIL import Image
import io
import os

# Configuración de la página estilo Móvil
st.set_page_config(page_title="AgroConnect", page_icon="🌱", layout="centered")

# --- FUNCIÓN PARA CARGAR LA IMAGEN DE FONDO (2_20260701_054241_0000.jpg) ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

# Intentar cargar la imagen de fondo de la interfaz
ruta_fondo = "2_20260701_054241_0000.jpg"
img_base64 = get_base64_image(ruta_fondo)

# --- CONEXIÓN CON XAMPP ---
def obtener_conexion():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="agroconnect_db"
    )

# --- FUNCIONES AUXILIARES ---
def obtener_tasa_bcv():
    return 36.50  # Tasa oficial del BCV simulada

def obtener_clima():
    import random
    estados = ["☀️ Soleado - Ideal para la jornada de siembra", "🌧️ Lluvioso - Se recomienda resguardar maquinaria", "⛅ Parcialmente Nublado"]
    return random.choice(estados)

# --- CONTROL DE SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None
if "username_actual" not in st.session_state:
    st.session_state.username_actual = None
if "ubicacion_actual" not in st.session_state:
    st.session_state.ubicacion_actual = "Lara, Venezuela"

# --- ESTILOS VISUALES GENERALES Y LOGIN ---
if not st.session_state.autenticado:
    # Si no está autenticado, inyectamos el fondo de la imagen 2_20260701_054241_0000.jpg
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{img_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        
        /* Ocultar elementos por defecto de Streamlit en el login para limpiar la vista */
        header, footer, [data-testid="stHeader"] {{
            background: transparent !important;
        }}
        
        /* Contenedor del Login alineado a la izquierda */
        .login-container {{
            max-width: 450px;
            margin-top: 80px;
            font-family: 'Arial Black', Gadget, sans-serif;
        }}
        
        /* Etiquetas personalizadas (USUARIO / CONTRASEÑA) en verde oscuro militar */
        .login-label {{
            color: #1e3d14 !important;
            font-size: 22px !important;
            font-weight: 900 !important;
            letter-spacing: 1px;
            margin-bottom: -5px;
            margin-top: 15px;
            text-transform: uppercase;
        }}
        
        /* Customización de las cajas de texto de Streamlit para que combinen */
        .stTextInput > div > div > input {{
            background-color: rgba(255, 255, 255, 0.2) !important;
            border: 2px solid #ffffff !important;
            color: #1e3d14 !important;
            border-radius: 4px !important;
            font-size: 16px !important;
            font-weight: bold !important;
        }}
        
        /* Botones del Login estilo Óvalo Oscuro */
        .login-btn-col button {{
            background-color: #163805 !important;
            color: white !important;
            border-radius: 30px !important;
            padding: 10px 20px !important;
            font-weight: bold !important;
            border: none !important;
            box-shadow: 0px 4px 6px rgba(0,0,0,0.2);
            text-transform: uppercase;
            width: 100%;
        }}
        
        /* Enlaces inferiores (REGISTRAR / RECUPERAR) */
        .login-link-footer {{
            text-align: center;
            margin-top: 20px;
        }}
        .login-link-footer a {{
            color: #000000 !important;
            text-decoration: none !important;
            font-weight: bold !important;
            font-size: 15px !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        </style>
    """, unsafe_allow_html=True)
else:
    # Estilos una vez que ya ingresó a la aplicación principal
    st.markdown("""
        <style>
        .main { background-color: #f9f9f9; }
        .stButton>button { background-color: #2E7D32; color: white; border-radius: 20px; width: 100%; }
        .card { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0px 2px 5px rgba(0,0,0,0.05); margin-bottom: 5px; border-left: 5px solid #2E7D32; }
        .user-header { font-weight: bold; color: #333; margin-bottom: 5px; }
        .location { font-size: 0.85em; color: #777; margin-left: 5px; }
        .bcv-box { background-color: #E8F5E9; padding: 10px; border-radius: 8px; font-weight: bold; text-align: center; color: #1B5E20; margin-bottom: 10px; }
        .comment-box { background-color: #f1f1f1; padding: 8px; border-radius: 8px; margin-top: 5px; font-size: 0.9em; }
        </style>
    """, unsafe_allow_html=True)

tasa_bcv = obtener_tasa_bcv()

# ==========================================
# 🚪 LOGIN / REGISTRO
# ==========================================
if not st.session_state.autenticado:
    
    # Menú horizontal para alternar vistas sin romper el fondo estético
    opcion_auth = option_menu(
        menu_title=None,
        options=["Iniciar Sesión", "Registrarse", "Recuperar Clave"],
        icons=["box-arrow-in-right", "person-plus", "key"],
        orientation="horizontal",
        styles={
            "container": {"background-color": "rgba(255, 255, 255, 0.6)", "padding": "2px"},
            "nav-link-selected": {"background-color": "#163805", "color": "white"}
        }
    )
    
    # Estructura del Login maquetado en la zona izquierda de la imagen
    if opcion_auth == "Iniciar Sesión":
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Espaciador para saltar el logo integrado que ya trae la imagen de fondo
        st.markdown("<br><br><br><br>", unsafe_allow_html=True)
        
        st.markdown('<p class="login-label">USUARIO:</p>', unsafe_allow_html=True)
        user_input = st.text_input("Usuario", label_visibility="collapsed", key="login_user")
        
        st.markdown('<p class="login-label">CONTRASEÑA</p>', unsafe_allow_html=True)
        pass_input = st.text_input("Contraseña", type="password", label_visibility="collapsed", key="login_pass")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Columnas para los dos botones óvalos (Cancelar y Acceder)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.markdown('<div class="login-btn-col">', unsafe_allow_html=True)
            if st.button("CANCELAR", key="btn_cancelar"):
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_btn2:
            st.markdown('<div class="login-btn-col">', unsafe_allow_html=True)
            if st.button("ACCEDER", key="btn_acceder"):
                conn = obtener_conexion()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM usuarios WHERE usuario = %s AND contrasena = %s", (user_input, pass_input))
                usuario = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if usuario:
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = usuario['nombre']
                    st.session_state.username_actual = usuario['usuario']
                    st.session_state.ubicacion_actual = usuario['ubicacion']
                    st.success(f"¡Bienvenido {usuario['nombre']}!")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Enlaces inferiores tal cual la foto
        col_link1, col_link2 = st.columns(2)
        with col_link1:
            st.markdown('<div class="login-link-footer"><a href="#">REGISTRAR</a></div>', unsafe_allow_html=True)
        with col_link2:
            st.markdown('<div class="login-link-footer"><a href="#">RECUPERAR ACCESO</a></div>', unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
                
    elif opcion_auth == "Registrarse":
        st.markdown('<div style="background-color: rgba(255,255,255,0.85); padding: 20px; border-radius: 10px; margin-top:20px;">', unsafe_allow_html=True)
        reg_nombre = st.text_input("Nombre Completo")
        reg_user = st.text_input("Nombre de Usuario")
        reg_pass = st.text_input("Contraseña", type="password")
        reg_ubicacion = st.text_input("Ubicación", value="Lara, Venezuela")
        
        reg_pregunta = st.selectbox("Pregunta de seguridad", ["¿Mascota?", "¿Comida?", "Pueblo natal?"])
        reg_respuesta = st.text_input("Respuesta").lower().strip()
        
        if st.button("Crear Cuenta"):
            if reg_nombre and reg_user and reg_pass and reg_respuesta:
                try:
                    conn = obtener_conexion()
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO usuarios (nombre, usuario, contrasena, ubicacion, pregunta_secreta, respuesta_secreta) VALUES (%s, %s, %s, %s, %s, %s)",
                        (reg_nombre, reg_user, reg_pass, reg_ubicacion, reg_pregunta, reg_respuesta)
                    )
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success("¡Registro exitoso!")
                except mysql.connector.Error:
                    st.error("El usuario ya existe.")
        st.markdown('</div>', unsafe_allow_html=True)

    elif opcion_auth == "Recuperar Clave":
        st.markdown('<div style="background-color: rgba(255,255,255,0.85); padding: 20px; border-radius: 10px; margin-top:20px;">', unsafe_allow_html=True)
        st.subheader("Recuperar Acceso")
        # Aquí puedes mapear la lógica que necesites para recuperar clave
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 🌱 APLICACIÓN PRINCIPAL (Dashboard)
# ==========================================
else:
    st.markdown(f"<div class='bcv-box'>Tasa Oficial BCV: 1 USD = {tasa_bcv:.2f} BsS</div>", unsafe_allow_html=True)
    busqueda = st.text_input("🔍 Buscar publicaciones, productos o expertos...", "")

    col_tit, col_logout = st.columns([4, 1])
    with col_tit:
        st.caption(f"👤 Conectado como: {st.session_state.usuario_actual}")
    with col_logout:
        if st.button("Salir 🚪"):
            st.session_state.autenticado = False
            st.rerun()

    selected = option_menu(
        menu_title=None,
        options=["Inicio", "Perfil", "Market", "Chat", "Clima 🌤️"],
        icons=["house", "person", "shop", "chat-dots", "cloud-sun"],
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"background-color": "#ffffff", "padding": "0px"},
            "icon": {"color": "#2E7D32", "font-size": "14px"}, 
            "nav-link": {"font-size": "12px", "padding": "5px"},
            "nav-link-selected": {"background-color": "#2E7D32", "color": "white"},
        }
    )

    # --- 🏠 PESTAÑA: INICIO ---
    if selected == "Inicio":
        st.subheader("🌾 Comunidad Agrícola")
        
        with st.expander("📝 Publicar en el Feed (Soporta Fotos/Videos)"):
            nuevo_texto = st.text_area("¿Qué está pasando en tu campo?")
            archivo_subido = st.file_uploader("Subir foto o video", type=["png", "jpg", "jpeg", "mp4"])
            
            if st.button("Publicar 🚀"):
                img_base = None
                if archivo_subido:
                    img_base = base64.b64encode(archivo_subido.read()).decode()
                
                conn = obtener_conexion()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO publicaciones (autor, pais, texto, archivo_adjunto, likes) VALUES (%s, %s, %s, %s, 0)", 
                               (st.session_state.usuario_actual, st.session_state.ubicacion_actual, nuevo_texto, img_base))
                conn.commit()
                cursor.close()
                conn.close()
                st.rerun()

        # Cargar Publicaciones
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        if busqueda:
            cursor.execute("SELECT * FROM publicaciones WHERE texto LIKE %s ORDER BY id_publicacion DESC", (f"%{busqueda}%",))
        else:
            cursor.execute("SELECT * FROM publicaciones ORDER BY id_publicacion DESC")
        id_publicaciones = cursor.fetchall()
        cursor.close()
        conn.close()

        for p in id_publicaciones:
            id_pub = p['id_publicacion']
            
            st.markdown(f"""
            <div class="card">
                <div class="user-header">👤 {p['autor']} <span class="location">- 📍 {p['pais']}</span></div>
                <p>{p['texto']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if p['archivo_adjunto']:
                st.image(base64.b64decode(p['archivo_adjunto']), use_container_width=True)
            
            col_like, col_space = st.columns([2, 3])
            with col_like:
                if st.button(f"❤️ {p['likes']} Me Gusta", key=f"like_{id_pub}"):
                    conn = obtener_conexion()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE publicaciones SET likes = likes + 1 WHERE id_publicacion = %s", (id_pub,))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.rerun()

            with st.expander(f"💬 Ver o escribir comentarios"):
                comentario_texto = st.text_input("Escribe un comentario...", key=f"input_txt_{id_pub}")
                if st.button("Comentar ↩️", key=f"btn_com_{id_pub}"):
                    if comentario_texto:
                        conn = obtener_conexion()
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO comentarios (id_publicacion, autor_comentario, texto_comentario) VALUES (%s, %s, %s)",
                                       (id_pub, st.session_state.usuario_actual, comentario_texto))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.rerun()
                
                conn = obtener_conexion()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM comentarios WHERE id_publicacion = %s ORDER BY id_comentario ASC", (id_pub,))
                lista_comentarios = cursor.fetchall()
                cursor.close()
                conn.close()
                
                for c in lista_comentarios:
                    st.markdown(f"""
                    <div class="comment-box">
                        <b>{c['autor_comentario']}:</b> {c['texto_comentario']}
                    </div>
                    """, unsafe_allow_html=True)

    # --- 👤 PESTAÑA: PERFIL ---
    elif selected == "Perfil":
        st.subheader("⚙️ Mi Perfil de Agricultor")
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s", (st.session_state.username_actual,))
        datos_user = cursor.fetchone()
        cursor.close()
        conn.close()

        if datos_user and datos_user['foto_perfil']:
            st.image(base64.b64decode(datos_user['foto_perfil']), width=120)
        
        nuevo_nombre = st.text_input("Editar Nombre Completo", value=datos_user['nombre'])
        nueva_ubi = st.text_input("Editar Ubicación", value=datos_user['ubicacion'])
        nueva_foto = st.file_uploader("Actualizar foto de perfil", type=["png", "jpg", "jpeg"])

        if st.button("Guardar Cambios 💾"):
            foto_b64 = datos_user['foto_perfil']
            if nueva_foto:
                foto_b64 = base64.b64encode(nueva_foto.read()).decode()
            
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET nombre = %s, ubicacion = %s, foto_perfil = %s WHERE usuario = %s",
                           (nuevo_nombre, nueva_ubi, foto_b64, st.session_state.username_actual))
            conn.commit()
            cursor.close()
            conn.close()
            st.session_state.usuario_actual = nuevo_nombre
            st.session_state.ubicacion_actual = nueva_ubi
            st.success("¡Perfil actualizado!")
            st.rerun()

    # --- 🛒 PESTAÑA: MARKET ---
    elif selected == "Market":
        st.subheader("🛒 Mercado Agropecuario")
        with st.expander("💰 Publicar Producto"):
            prod_nombre = st.text_input("Nombre del producto/maquinaria")
            prod_precio_usd = st.number_input("Precio en Dólares ($)", min_value=0.0)
            prod_estado = st.selectbox("Condición", ["Nuevo ✨", "Usado 🔧"])
            foto_prod = st.file_uploader("Subir foto del producto", type=["png", "jpg", "jpeg"])
            
            if st.button("Poner en Venta 🚀"):
                prod_b64 = None
                if foto_prod:
                    prod_b64 = base64.b64encode(foto_prod.read()).decode()
                
                conn = obtener_conexion()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO productos (nombre, precio, estado, archivo_producto) VALUES (%s, %s, %s, %s)", 
                               (prod_nombre, prod_precio_usd, prod_estado, prod_b64))
                conn.commit()
                cursor.close()
                conn.close()
                st.rerun()

        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos ORDER BY id_producto DESC")
        lista_productos = cursor.fetchall()
        cursor.close()
        conn.close()

        cols = st.columns(2)
        for i, prod in enumerate(lista_productos):
            precio_bs = float(prod['precio']) * tasa_bcv
            with cols[i % 2]:
                st.markdown(f"""
                <div class="card">
                    <span class="location">📦 {prod['estado']}</span>
                    <div class="user-header">{prod['nombre']}</div>
                    <h4 style='color: #2E7D32; margin: 2px 0;'>${prod['precio']:.2f} USD</h4>
                    <h5 style='color: #E65100; margin: 2px 0;'>Ref: {precio_bs:.2f} Bs</h5>
                </div>
                """, unsafe_allow_html=True)
                if prod['archivo_producto']:
                    st.image(base64.b64decode(prod['archivo_producto']), use_container_width=True)
                if st.button("⚡ Contactar", key=f"btn_{prod['id_producto']}"):
                    st.success("¡Abriendo chat privado!")

    # --- 💬 PESTAÑA: CHAT PRIVADO ---
    elif selected == "Chat":
        st.subheader("💬 Mensajería Privada")
        destinatario = st.text_input("Usuario del destinatario:")
        msg_texto = st.text_area("Escribe tu mensaje...")
        
        if st.button("Enviar Mensaje 📨"):
            if destinatario and msg_texto:
                conn = obtener_conexion()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO mensajes_privados (remitente, destinatario, mensaje) VALUES (%s, %s, %s)",
                               (st.session_state.username_actual, destinatario, msg_texto))
                conn.commit()
                cursor.close()
                conn.close()
                st.success("¡Mensaje enviado!")

        st.write("---")
        st.subheader("📥 Bandeja de Entrada")
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM mensajes_privados WHERE destinatario = %s ORDER BY id_mensaje DESC", (st.session_state.username_actual,))
        mensajes = cursor.fetchall()
        cursor.close()
        conn.close()

        for m in mensajes:
            st.info(f"📩 **De: {m['remitente']}**: {m['mensaje']}")

    # --- 🌤️ PESTAÑA: CLIMA ---
    elif selected == "Clima 🌤️":
        st.subheader("🌤️ Estado del Tiempo")
        st.write(f"Región activa: **{st.session_state.ubicacion_actual}**")
        pronostico = obtener_clima()
        st.success(pronostico)

