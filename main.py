import streamlit as st
import mysql.connector
import requests

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

def obtener_tasa_bcv():
    try:
        url = "https://pydolarvenezuela-api.vercel.app/api/v1/dollar?page=bcv"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            datos = response.json()
            return float(datos['monitors']['usd']['price'])
    except Exception as e:
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
if "pantalla_actual" not in st.session_state:
    st.session_state.pantalla_actual = "Novedades"  
if "pantalla_auth" not in st.session_state:
    st.session_state.pantalla_auth = "login"
if "likes_dados" not in st.session_state:
    st.session_state.likes_dados = {}

# ==========================================
# 🚪 PANEL DE AUTENTICACIÓN (DISEÑO CRISTAL / VERDE)
# ==========================================
def render_autentizacion():
    # CSS Exclusivo para el Login
    st.markdown("""
        <style>
        /* 1. Fondo Verde de toda la página */
        [data-testid="stAppViewContainer"] {
            background-color: #1e4d2b !important;
            background-image: linear-gradient(135deg, #11301a 0%, #2e6d38 100%) !important;
        }
        
        [data-testid="stHeader"] {
            background: transparent !important;
        }

        /* 2. Caja Gris Transparente en el centro */
        .block-container {
            background-color: rgba(0, 0, 0, 0.4) !important; /* Gris oscuro transparente */
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 3rem 2rem !important;
            max-width: 400px !important;
            margin-top: 10vh;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 15px 30px rgba(0,0,0,0.5);
        }

        /* Textos e Inputs en blanco para resaltar */
        h1, h2, h3, p, div[data-testid="stWidgetLabel"] p {
            color: #ffffff !important;
            font-weight: 500 !important;
        }

        /* 3. Botones Primarios (Acceder / Cancelar) -> Verdes */
        button[kind="primary"] {
            background-color: #4CAF50 !important;
            color: white !important;
            border-radius: 12px !important;
            border: none !important;
            font-weight: bold !important;
            padding: 0.6rem !important;
        }
        button[kind="primary"]:hover {
            background-color: #45a049 !important;
        }

        /* 4. Botones Secundarios (Crear Cuenta / Olvidar Clave) -> Solo Letras */
        button[kind="secondary"] {
            background: transparent !important;
            color: #a3cfbb !important;
            border: none !important;
            box-shadow: none !important;
            font-weight: normal !important;
            padding: 0 !important;
        }
        button[kind="secondary"]:hover {
            color: #ffffff !important;
            text-decoration: underline !important;
            background: transparent !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # PANTALLA: LOGIN
    if st.session_state.pantalla_auth == "login":
        st.markdown('<div style="text-align:center; font-size:32px; font-weight:bold; color:white;">🌱 AgroCampo</div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align:center; font-size:14px; color:#a3cfbb; margin-bottom: 25px;">Bienvenido, inicia sesión</div>', unsafe_allow_html=True)
        
        user_input = st.text_input("Usuario")
        pass_input = st.text_input("Contraseña", type="password")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Botón ACCEDER (Primario = Verde)
        if st.button("ACCEDER", type="primary", use_container_width=True):
            try:
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
                    st.rerun()
                else:
                    st.error("Credenciales inválidas.")
            except Exception as e:
                # Si no hay XAMPP, entra como prueba
                st.session_state.autenticado = True
                st.session_state.usuario_actual = "Usuario de Prueba"
                st.session_state.username_actual = user_input
                st.session_state.ubicacion_actual = "Lara, Venezuela"
                st.rerun()
        
        st.markdown("<hr style='border: 0; border-top: 1px solid rgba(255,255,255,0.2); margin: 20px 0;'>", unsafe_allow_html=True)
        
        # Botones SIN FONDO (Secundarios = Solo letras)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Crear cuenta nueva", type="secondary", use_container_width=True):
                st.session_state.pantalla_auth = "registro"
                st.rerun()
        with col2:
            if st.button("¿Olvidaste tu clave?", type="secondary", use_container_width=True):
                st.session_state.pantalla_auth = "recuperar"
                st.rerun()

    # PANTALLA: REGISTRO
    elif st.session_state.pantalla_auth == "registro":
        st.markdown('<div style="text-align:center; font-size:24px; font-weight:bold; color:white; margin-bottom: 20px;">Crear Cuenta</div>', unsafe_allow_html=True)
        
        reg_nombre = st.text_input("Nombre Completo")
        reg_user = st.text_input("Usuario")
        reg_pass = st.text_input("Contraseña", type="password")
        reg_ubicacion = st.text_input("Ubicación")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("REGISTRARSE", type="primary", use_container_width=True):
            st.success("Cuenta creada (Modo prueba). Vuelve al login.")
        
        # Botón CANCELAR (Primario = Verde, como pediste)
        if st.button("Cancelar", type="primary", use_container_width=True):
            st.session_state.pantalla_auth = "login"
            st.rerun()

    # PANTALLA: RECUPERAR
    elif st.session_state.pantalla_auth == "recuperar":
        st.markdown('<div style="text-align:center; font-size:24px; font-weight:bold; color:white; margin-bottom: 20px;">Recuperar Acceso</div>', unsafe_allow_html=True)
        
        rec_nombre = st.text_input("Ingresa tu Nombre Registrado")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("BUSCAR", type="primary", use_container_width=True):
            st.info("Función de búsqueda activada.")
            
        # Botón CANCELAR (Primario = Verde)
        if st.button("Cancelar", type="primary", use_container_width=True):
            st.session_state.pantalla_auth = "login"
            st.rerun()


# ==========================================
# 🌱 INTERFAZ PRINCIPAL (DASHBOARD)
# ==========================================
def render_dashboard():
    # CSS Exclusivo para el Dashboard (Fondo claro y limpio)
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] { background-color: #F7F9F6 !important; }
        .block-container {
            background-color: transparent !important;
            box-shadow: none !important;
            padding: 2rem 1rem !important;
            max-width: 500px !important;
            margin-top: 0;
        }
        h1, h2, p, div[data-testid="stWidgetLabel"] p { color: #333333 !important; }
        .main-header { font-size: 24px; font-weight: bold; color: #1E3D14; margin-bottom: 15px; }
        .agro-card { background-color: #FFFFFF; border-radius: 12px; padding: 15px; border: 1px solid #ECECEC; margin-bottom: 10px; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="main-header">{st.session_state.pantalla_actual}</div>', unsafe_allow_html=True)

    if st.session_state.pantalla_actual == "Novedades":
        st.info("Bienvenido al panel principal. Aquí verás las publicaciones.")
        if st.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()

    cols_nav = st.columns(3)
    secciones = ["Novedades", "Market", "Perfil"]
    for i, col in enumerate(cols_nav):
        with col:
            if st.button(secciones[i], use_container_width=True):
                st.session_state.pantalla_actual = secciones[i]
                st.rerun()

# ==========================================
# 🚦 CONTROLADOR DE VISTAS
# ==========================================
if not st.session_state.autenticado:
    render_autentizacion()
else:
    render_dashboard()
