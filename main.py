import streamlit as st
import mysql.connector
import base64
import os
import sys
import subprocess
import requests  # <-- Añadido para conectar con la tasa del dólar en vivo

# Configuración de página estilo móvil
st.set_page_config(page_title="AgroCampo", page_icon="🌱", layout="centered")

# --- CONEXIÓN CON XAMPP ---
def obtener_conexion():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="bd_agrocampo"
    )

def obtener_tasa_bcv():
    """
    Obtiene la tasa oficial del BCV en tiempo real a través de una API abierta.
    Mantiene el valor del viernes durante el fin de semana de forma automática.
    """
    try:
        # Consulta a API de indicadores económicos de Venezuela
        url = "https://pydolarvenezuela-api.vercel.app/api/v1/dollar?page=bcv"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            datos = response.json()
            return float(datos['monitors']['usd']['price'])
    except Exception as e:
        # Si la API falla o no hay internet, usa el valor base actual de referencia
        return 674.93
        
    return 674.93

def obtener_clima():
    return "☀️ Soleado - Ideal para la jornada de siembra"

# --- CONTROL DE SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None
if "username_actual" not in st.session_state:
    st.session_state.username_actual = None
if "id_usuario_actual" not in st.session_state:
    st.session_state.id_usuario_actual = None
if "ubicacion_actual" not in st.session_state:
    st.session_state.ubicacion_actual = "Lara, Venezuela"
if "pantalla_actual" not in st.session_state:
    st.session_state.pantalla_actual = "Novedades"  
if "pantalla_auth" not in st.session_state:
    st.session_state.pantalla_auth = "login"
if "likes_dados" not in st.session_state:
    st.session_state.likes_dados = {}  # {id_publicacion: True}

# ==========================================
# 🎨 ESTILOS CSS INSPIRADOS EN LA IMAGEN
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #F7F9F6 !important;
    }
    
    [data-testid="stVerticalBlock"] {
        max-width: 480px;
        margin: 0 auto;
    }
    
    .main-header {
        font-size: 26px;
        font-weight: 700;
        color: #1E3D14;
        margin-bottom: 15px;
        text-align: center;
    }
    
    .pill {
        background-color: #E2EFE0;
        color: #1E3D14;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        display: inline-block;
        margin-right: 8px;
        margin-bottom: 10px;
        border: 1px solid #C2DCBD;
    }
    
    .agro-card {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        margin-bottom: 16px;
        border: 1px solid #ECECEC;
    }
    
    .card-user {
        display: flex;
        align-items: center;
        font-weight: 600;
        color: #222222;
        font-size: 14px;
        margin-bottom: 8px;
    }
    
    .card-location {
        font-weight: 400;
        color: #777777;
        font-size: 12px;
        margin-left: 5px;
    }
    
    .card-text {
        font-size: 14px;
        color: #333333;
        line-height: 1.5;
        margin-bottom: 12px;
    }
    
    .product-tag {
        background-color: #7A604D;
        color: white;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 6px;
    }
    
    .product-price-usd {
        color: #1E3D14;
        font-weight: 700;
        font-size: 18px;
        margin: 4px 0;
    }
    
    .nav-bar-spacer {
        margin-top: 80px;
    }
    
    div[data-testid="stHorizontalBlock"] {
        background-color: #FFFFFF !important;
        border-top: 1px solid #EEEEEE;
        padding: 10px 0px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Consultamos la tasa real antes de renderizar la app
tasa_bcv = obtener_tasa_bcv()

# ==========================================
# 🚪 PANEL DE AUTENTICACIÓN
# ==========================================
def render_autentizacion():
    st.markdown('<div class="main-header">🌱 AgroCampo</div>', unsafe_allow_html=True)
    
    # PANTALLA: LOGIN
    if st.session_state.pantalla_auth == "login":
        st.subheader("Iniciar Sesión")
        user_input = st.text_input("Usuario", key="login_user")
        pass_input = st.text_input("Contraseña", type="password", key="login_pass")
        
        campos_vacios = not user_input.strip() or not pass_input.strip()
        
        if st.button("ACCEDER", key="btn_acceder", disabled=campos_vacios, use_container_width=True):
            try:
                conn = obtener_conexion()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM usuarios WHERE usuario = %s AND contrasena = %s", (user_input, pass_input))
                usuario = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if usuario:
                    st.session_state.autenticado = True
                    st.session_state.id_usuario_actual = usuario.get('id', 1)
                    st.session_state.usuario_actual = usuario['nombre']
                    st.session_state.username_actual = usuario['usuario']
                    st.session_state.ubicacion_actual = usuario['ubicacion']
                    st.rerun()
                else:
                    st.error("Credenciales inválidas.")
            except Exception as e:
                st.session_state.autenticado = True
                st.session_state.id_usuario_actual = 1
                st.session_state.usuario_actual = "Usuario de Prueba"
                st.session_state.username_actual = user_input
                st.rerun()
        
        col_reg, col_rec = st.columns(2)
        with col_reg:
            if st.button("Crear cuenta nueva", key="go_register", use_container_width=True):
                st.session_state.pantalla_auth = "registro"
                st.rerun()
        with col_rec:
            if st.button("¿Olvidaste tu clave?", key="go_recovery", use_container_width=True):
                st.session_state.pantalla_auth = "recuperar"
                st.rerun()

    # PANTALLA: REGISTRO
    elif st.session_state.pantalla_auth == "registro":
        st.subheader("Crear Cuenta Nueva")
        reg_nombre = st.text_input("Nombre Completo", key="reg_nombre")
        reg_user = st.text_input("Nombre de Usuario", key="reg_user")
        reg_pass = st.text_input("Contraseña Nueva", type="password", key="reg_pass")
        reg_ubicacion = st.text_input("Ubicación (Ej: Barquisimeto, Lara)", key="reg_ubicacion")
        
        campos_registro_vacios = not reg_nombre.strip() or not reg_user.strip() or not reg_pass.strip() or not reg_ubicacion.strip()
        
        if st.button("REGISTRARSE", key="btn_registrar", disabled=campos_registro_vacios, use_container_width=True):
            try:
                conn = obtener_conexion()
                cursor = conn.cursor()
                sql = "INSERT INTO usuarios (nombre, usuario, contrasena, ubicacion) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (reg_nombre, reg_user, reg_pass, reg_ubicacion))
                conn.commit()
                cursor.close()
                conn.close()
                st.success("¡Cuenta creada con éxito! Ya puedes iniciar sesión.")
                st.session_state.pantalla_auth = "login"
                st.rerun()
            except Exception as e:
                st.error("Error al guardar en Base de Datos.")

        if st.button("Volver al Login", key="back_login_reg", use_container_width=True):
            st.session_state.pantalla_auth = "login"
            st.rerun()

    # PANTALLA: RECUPERAR
    elif st.session_state.pantalla_auth == "recuperar":
        st.subheader("Recuperar Cuenta")
        rec_nombre = st.text_input("Nombre Completo Registrado", key="rec_nombre")
        campo_rec_vacio = not rec_nombre.strip()
        
        if st.button("BUSCAR CREDENCIALES", key="btn_recuperar", disabled=campo_rec_vacio, use_container_width=True):
            try:
                conn = obtener_conexion()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT usuario, contrasena FROM usuarios WHERE nombre LIKE %s", (f"%{rec_nombre}%",))
                resultado = cursor.fetchone()
                cursor.close()
                conn.close()
                if resultado:
                    st.info(f"🔑 **Datos:**\n\n**Usuario:** {resultado['usuario']}\n\n**Contraseña:** {resultado['contrasena']}")
                else:
                    st.error("No se encontró ningún usuario con ese nombre.")
            except Exception as e:
                st.error("Error de conexión.")
                
        if st.button("Volver al Login", key="back_login_rec", use_container_width=True):
            st.session_state.pantalla_auth = "login"
            st.rerun()

# ==========================================
# 🌱 INTERFAZ PRINCIPAL (DASHBOARD)
# ==========================================
def render_dashboard():
    # Cabeceras dinámicas
    if st.session_state.pantalla_actual == "Novedades":
        st.markdown('<div class="main-header">AgroCampo 🔔</div>', unsafe_allow_html=True)
    elif st.session_state.pantalla_actual == "Consulta (SOS)":
        st.markdown('<div class="main-header">AgroCampo: Expertos</div>', unsafe_allow_html=True)
    elif st.session_state.pantalla_actual == "Market":
        st.markdown('<div class="main-header">AgroCampo: Mercado</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="main-header">{st.session_state.pantalla_actual}</div>', unsafe_allow_html=True)

    # Buscador integrado
    busqueda = st.text_input("Buscar...", label_visibility="collapsed", placeholder="🔍 Buscar...", key="main_search")
    
    # --- 🏠 SECCIÓN: NOVEDADES ---
    if st.session_state.pantalla_actual == "Novedades":
        st.markdown('<div><span class="pill">🌽 Maíz</span><span class="pill">🐛 Plagas</span><span class="pill">🚜 Maquinaria</span></div>', unsafe_allow_html=True)
        
        with st.expander("📝 Compartir algo con la comunidad (Nueva publicación)"):
            texto_post = st.text_area("¿Qué está pasando en tu campo?", key="nuevo_post_texto")
            boton_deshabilitado = not texto_post.strip()
            
            if st.button("Publicar 🚀", key="btn_guardar_post", disabled=boton_deshabilitado):
                try:
                    conn = obtener_conexion()
                    cursor = conn.cursor()
                    sql = "INSERT INTO publicaciones (usuario_nombre, ubicacion, contenido) VALUES (%s, %s, %s)"
                    cursor.execute(sql, (st.session_state.usuario_actual, st.session_state.ubicacion_actual, texto_post))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success("¡Tu estado se ha publicado con éxito!")
                    st.rerun()
                except Exception as e:
                    if "posts_locales" not in st.session_state:
                        st.session_state.posts_locales = []
                    st.session_state.posts_locales.insert(0, {
                        "usuario_nombre": st.session_state.usuario_actual,
                        "ubicacion": st.session_state.ubicacion_actual,
                        "contenido": texto_post
                    })
                    st.success("Publicado (Modo local de pruebas)")
                    st.rerun()

        st.markdown("---")

        lista_publicaciones = []
        try:
            conn = obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM publicaciones ORDER BY id DESC")
            lista_publicaciones = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as e:
            lista_publicaciones = st.session_state.get("posts_locales", [])

        if not lista_publicaciones:
            st.info("📭 El muro está vacío. ¡Sé el primero en interactuar y publicar un estado arriba!")
        else:
            for index, post in enumerate(lista_publicaciones):
                id_unico = post.get('id', index)
                st.markdown(f"""
                    <div class="agro-card">
                        <div class="card-user">👤 {post['usuario_nombre']} <span class="card-location">- {post['ubicacion']}</span></div>
                        <div class="card-text">{post['contenido']}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                col_lk, col_cm = st.columns(2)
                with col_lk:
                    id_like_track = f"like_post_{id_unico}"
                    ya_dio_like = st.session_state.likes_dados.get(id_like_track, False)
                    label_lk = "❤️ Ya te gusta" if ya_dio_like else "❤️ Me Gusta"
                    
                    if st.button(label_lk, key=f"lk_{id_unico}", disabled=ya_dio_like):
                        st.session_state.likes_dados[id_like_track] = True
                        st.rerun()
                with col_cm:
                    st.button("💬 Comentarios", key=f"cm_{id_unico}")

    # --- 🩺 SECCIÓN: CONSULTA SOS ---
    elif st.session_state.pantalla_actual == "Consulta (SOS)":
        st.subheader("Pregunta a los Expertos / Diagnóstico SOS")
        st.warning("Próximamente: Las consultas también se cargarán de forma limpia desde la base de datos.")

    # --- 🛒 SECCIÓN: MERCADO (TASAS DINÁMICAS ACTUALIZADAS) ---
    elif st.session_state.pantalla_actual == "Market":
        # Bloque informativo para el usuario sobre la tasa activa
        st.info(f"💵 Tasa Oficial BCV de hoy: **{tasa_bcv:,.2f} Bs.**")
        
        st.markdown('<div><span class="pill">🚜 Tractores</span><span class="pill">🌾 Semillas</span></div>', unsafe_allow_html=True)
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            precio_usd1 = 41550.00
            st.markdown(f"""
                <div class="agro-card">
                    <span class="product-tag">Usado</span>
                    <div class="card-user" style="font-size:13px; margin:0;">Tractor John Deere</div>
                    <div class="product-price-usd">${precio_usd1:,.2f}</div>
                    <div class="product-price-bs">Monto: {precio_usd1 * tasa_bcv:,.2f} Bs</div>
                </div>
            """, unsafe_allow_html=True)
            st.button("Contactar", key="c_prod1")
        with col_p2:
            precio_usd2 = 20.00
            st.markdown(f"""
                <div class="agro-card">
                    <span class="product-tag" style="background-color:#1E3D14;">Nuevo</span>
                    <div class="card-user" style="font-size:13px; margin:0;">Saco Semillas Maíz</div>
                    <div class="product-price-usd">${precio_usd2:,.2f}</div>
                    <div class="product-price-bs">Monto: {precio_usd2 * tasa_bcv:,.2f} Bs</div>
                </div>
            """, unsafe_allow_html=True)
            st.button("Contactar", key="c_prod2")

    # --- 🌤️ CLIMA & PERFIL ---
    elif st.session_state.pantalla_actual == "Clima":
        st.info(obtener_clima())
    elif st.session_state.pantalla_actual == "Perfil":
        st.write(f"👤 **Usuario:** {st.session_state.usuario_actual} (`@{st.session_state.username_actual}`)")
        st.write(f"📍 **Ubicación:** {st.session_state.ubicacion_actual}")
        if st.button("Cerrar Sesión 🚪", use_container_width=True):
            st.session_state.autenticado = False
            st.session_state.pantalla_auth = "login"
            st.rerun()

    st.markdown('<div class="nav-bar-spacer"></div>', unsafe_allow_html=True)

    # ==========================================
    # 📱 MENÚ DE NAVEGACIÓN INFERIOR (ESTILO INSTAGRAM)
    # ==========================================
    cols_nav = st.columns(5)
    secciones = ["Novedades", "Market", "Consulta (SOS)", "Clima", "Perfil"]
    iconos = ["📰 Feed", "🛒 Market", "💬 SOS", "🌤️ Clima", "👤 Perfil"]
    
    for indice, col in enumerate(cols_nav):
        with col:
            es_activa = secciones[indice] == st.session_state.pantalla_actual
            label = f"🟢 {iconos[indice]}" if es_activa else iconos[indice]
            
            if st.button(label, key=f"nav_{secciones[indice]}", use_container_width=True):
                st.session_state.pantalla_actual = secciones[indice]
                st.rerun()

# ==========================================
# 🚦 CONTROLADOR PRINCIPAL
# ==========================================
if "streamlit_interno" in sys.argv:
    if not st.session_state.autenticado:
        render_autentizacion()
    else:
        render_dashboard()
else:
    if __name__ == "__main__":
        puerto = 8501
        comando_st = f"streamlit run {__file__} streamlit_interno --server.port {puerto} --server.headless true"
        try:
            subprocess.run(comando_st, shell=True, check=True)
        except KeyboardInterrupt:
            print("\n🛑 Servidor apagado.")
            