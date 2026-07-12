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

# Estructuras temporales en memoria por si XAMPP no tiene las tablas creadas aún
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
    st.session_state.likes_dados = {} # Guarda tuplas (usuario, post_id)

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
            padding: 3rem 2rem !important;
            max-width: 400px !important;
            margin-top: 10vh;
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
        }
        button[kind="secondary"] {
            background: transparent !important;
            color: #a3cfbb !important;
            border: none !important;
            box-shadow: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.session_state.pantalla_auth == "login":
        st.markdown('<div style="text-align:center; font-size:32px; font-weight:bold; color:white;">🌱 AgroCampo</div>', unsafe_allow_html=True)
        user_input = st.text_input("Usuario")
        pass_input = st.text_input("Contraseña", type="password")
        
        if st.button("ACCEDER", type="primary", use_container_width=True):
            st.session_state.autenticado = True
            if user_input.strip():
                st.session_state.username_actual = user_input
            st.rerun()

# ==========================================
# 🌱 INTERFAZ PRINCIPAL (SISTEMA COMPLETO)
# ==========================================
def render_dashboard():
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] { background-color: #F7F9F6 !important; }
        .block-container { background-color: transparent !important; box-shadow: none !important; padding: 2rem 1rem !important; max-width: 500px !important; }
        .main-header { font-size: 36px; font-weight: 900; color: #1E3D14 !important; text-align: center; margin-bottom: 5px; letter-spacing: 1px; }
        .sub-header { font-size: 18px; font-weight: bold; color: #2e6d38 !important; margin-bottom: 15px; text-transform: uppercase; }
        .agro-card { background-color: #FFFFFF; border-radius: 14px; padding: 18px; border: 1px solid #EAEAEA; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
        .post-author { font-weight: bold; color: #1E3D14; font-size: 15px; }
        
        div.stButton > button {
            background-color: #2e6d38 !important; color: white !important; border-radius: 10px !important;
            border: 1px solid #1e4d2b !important; font-weight: 600 !important;
        }
        .btn-logout > div.stButton > button { background-color: #d32f2f !important; border: 1px solid #b71c1c !important; }
        </style>
    """, unsafe_allow_html=True)

    # Encabezado principal global pedido
    st.markdown('<div class="main-header">🌱 AGROCAMPO</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header" style="text-align:center;">Sección: {st.session_state.pantalla_actual}</div>', unsafe_allow_html=True)

    # --- PANTALLA: NOVEDADES ---
    if st.session_state.pantalla_actual == "Novedades":
        # Barra de búsqueda integrada abajo del título
        busqueda = st.text_input("🔍 Buscar publicaciones o productores...", placeholder="Ej. Maíz, Lara, Plagas...")

        # Formulario para nueva publicación
        with st.expander("📝 Compartir algo con la comunidad agrícola"):
            nuevo_post = st.text_area("¿Qué está pasando en tus tierras?", placeholder="Escribe aquí tu actualización...")
            if st.button("Publicar al Instante", use_container_width=True):
                if nuevo_post.strip():
                    nuevo_id = len(st.session_state.db_publicaciones) + 1
                    st.session_state.db_publicaciones.insert(0, {
                        "id": nuevo_id,
                        "autor": st.session_state.usuario_actual,
                        "contenido": nuevo_post,
                        "likes": 0,
                        "comentarios": []
                    })
                    st.success("¡Publicado en la red general con éxito!")
                    st.rerun()

        st.markdown("<h4 style='color:#1E3D14;'>Publicaciones de la Comunidad</h4>", unsafe_allow_html=True)
        
        # Renderizado dinámico con filtro de búsqueda
        for post in st.session_state.db_publicaciones:
            if busqueda.lower() in post["contenido"].lower() or busqueda.lower() in post["autor"].lower():
                st.markdown(f"""
                    <div class="agro-card">
                        <div class="post-author">👤 {post['autor']}</div>
                        <p style="color: #444444 !important; margin: 8px 0; font-size:15px;">{post['contenido']}</p>
                        <small style="color: #888888;">👍 {post['likes']} Me gusta &nbsp;|&nbsp; 💬 {len(post['comentarios'])} Comentarios</small>
                    </div>
                """, unsafe_allow_html=True)
                
                col_lk, col_cm = st.columns([1, 2])
                with col_lk:
                    # Sistema estricto de un solo Like por usuario
                    llave_like = f"{st.session_state.username_actual}_{post['id']}"
                    ya_dio_like = st.session_state.likes_dados.get(llave_like, False)
                    
                    if st.button("👍 Dar Like" if not ya_dio_like else "✅ Liked", key=f"like_{post['id']}", use_container_width=True):
                        if not ya_dio_like:
                            post["likes"] += 1
                            st.session_state.likes_dados[llave_like] = True
                            st.rerun()
                
                with col_cm:
                    with st.popover("💬 Comentar"):
                        nuevo_comentario = st.text_input("Escribe tu comentario", key=f"in_com_{post['id']}")
                        if st.button("Enviar", key=f"btn_com_{post['id']}", use_container_width=True):
                            if nuevo_comentario.strip():
                                post["comentarios"].append(f"{st.session_state.usuario_actual}: {nuevo_comentario}")
                                st.rerun()
                
                if post["comentarios"]:
                    with st.expander("Ver comentarios anteriores"):
                        for c in post["comentarios"]:
                            st.caption(c)

    # --- PANTALLA: MARKET ---
    elif st.session_state.pantalla_actual == "Market":
        with st.expander("🛒 Publicar un producto en venta"):
            prod_titulo = st.text_input("Nombre del Producto / Insumo")
            prod_precio = st.text_input("Precio ($)")
            prod_desc = st.text_area("Descripción de la oferta")
            prod_foto = st.file_uploader("Subir Foto del Insumo", type=["png", "jpg", "jpeg"])
            
            if st.button("Lanzar al Mercado", use_container_width=True):
                if prod_titulo.strip() and prod_precio.strip():
                    st.session_state.db_market.insert(0, {
                        "id": len(st.session_state.db_market) + 1,
                        "titulo": prod_titulo,
                        "precio": prod_precio,
                        "descripcion": prod_desc,
                        "foto": prod_foto
                    })
                    st.success("¡Producto listado en el mercado agropecuario!")
                    st.rerun()

        st.markdown("<h4 style='color:#1E3D14;'>Catálogo Disponible</h4>", unsafe_allow_html=True)
        for item in st.session_state.db_market:
            st.markdown(f"""
                <div class="agro-card">
                    <div style="font-size: 18px; font-weight: bold; color: #2e6d38;">📦 {item['titulo']}</div>
                    <div style="font-size: 16px; color: #1E3D14; font-weight: bold; margin: 4px 0;">Precio: {item['precio']}$</div>
                    <p style="color: #555555 !important; margin: 0; font-size: 14px;">{item['descripcion']}</p>
                </div>
            """, unsafe_allow_html=True)
            if item["foto"] is not None:
                st.image(item["foto"], use_container_width=True)

    # --- PANTALLA: PERFIL (CONFIGURABLE) ---
    elif st.session_state.pantalla_actual == "Perfil":
        st.markdown("<h4 style='color:#1E3D14;'>⚙️ Configuración del Perfil Profesional</h4>", unsafe_allow_html=True)
        
        with st.form("form_perfil"):
            nuevo_nombre = st.text_input("Modificar Nombre Completo", value=st.session_state.usuario_actual)
            nueva_ubicacion = st.text_input("Modificar Ubicación Base", value=st.session_state.ubicacion_actual)
            
            if st.form_submit_button("Guardar Cambios Técnicos", use_container_width=True):
                st.session_state.usuario_actual = nuevo_nombre
                st.session_state.ubicacion_actual = nueva_ubicacion
                st.success("¡Datos actualizados correctamente!")
                st.rerun()

        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<div class="btn-logout">', unsafe_allow_html=True)
        if st.button("Cerrar Sesión 🚪", use_container_width=True):
            st.session_state.autenticado = False
            st.session_state.pantalla_auth = "login"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- NAVEGACIÓN INFERIOR MUTABLE ---
    st.markdown("<br><hr style='border:0; border-top: 1px solid #eee; margin: 20px 0;'>", unsafe_allow_html=True)
    cols_nav = st.columns(3)
    secciones = ["Novedades", "Market", "Perfil"]
    iconos = ["📰 Novedades", "🛒 Market", "👤 Perfil"]
    
    for indice, col in enumerate(cols_nav):
        with col:
            if st.button(iconos[indice], key=f"nav_{secciones[indice]}", use_container_width=True):
                st.session_state.pantalla_actual = secciones[indice]
                st.rerun()

# ==========================================
# 🚦 CONTROLADOR DE VISTAS
# ==========================================
if not st.session_state.autenticado:
    render_autentizacion()
else:
    render_dashboard()
    render_dashboard()
