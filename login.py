import streamlit as st
import os
from dotenv import load_dotenv, find_dotenv
import jwt

try:
    from streamlit_oauth import OAuth2Component
except ModuleNotFoundError:
    OAuth2Component = None

# Cargar .env de forma robusta
load_dotenv(find_dotenv(usecwd=True))

def _get_cred(name: str):
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return os.getenv(name)

CLIENT_ID = _get_cred("CLIENT_ID")
CLIENT_SECRET = _get_cred("CLIENT_SECRET")
REDIRECT_URI = _get_cred("REDIRECT_URI") or "http://localhost:8501"

st.title("Iniciar sesión con Google")

if OAuth2Component is None:
    st.error("Falta 'streamlit-oauth'. Instálalo con pip y agrégalo a requirements.txt")
    st.stop()

missing = [n for n,v in (("CLIENT_ID",CLIENT_ID),("CLIENT_SECRET",CLIENT_SECRET),("REDIRECT_URI",REDIRECT_URI)) if not v]
if missing:
    st.error("Faltan variables de entorno: " + ", ".join(missing))
    st.stop()

oauth2 = OAuth2Component(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    authorize_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
    token_endpoint="https://oauth2.googleapis.com/token",
)

# Estado de sesión
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'user_info' not in st.session_state:
    st.session_state['user_info'] = None

# Barra lateral con login/logout y datos del usuario
with st.sidebar:
    st.header("Autenticación")
    if not st.session_state['authenticated']:
        result = oauth2.authorize_button(
            name="Google",
            redirect_uri=REDIRECT_URI,
            scope="openid email profile",
            key="google_login",
            icon="data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' viewBox='0 0 48 48'%3E%3Cdefs%3E%3Cpath id='a' d='M44.5 20H24v8.5h11.8C34.7 33.9 30.1 37 24 37c-7.2 0-13-5.8-13-13s5.8-13 13-13c3.1 0 5.9 1.1 8.1 2.9l6.4-6.4C34.6 4.1 29.6 2 24 2 11.8 2 2 11.8 2 24s9.8 22 22 22c11 0 21-8 21-22 0-1.3-.2-2.7-.5-4z'/%3E%3C/defs%3E%3CclipPath id='b'%3E%3Cuse xlink:href='%23a' overflow='visible'/%3E%3C/clipPath%3E%3Cpath clip-path='url(%23b)' fill='%23FBBC05' d='M0 37V11l17 13z'/%3E%3Cpath clip-path='url(%23b)' fill='%23EA4335' d='M0 11l17 13 7-6.1L48 14V0H0z'/%3E%3Cpath clip-path='url(%23b)' fill='%2334A853' d='M0 37l30-23 7.9 1L48 0v48H0z'/%3E%3Cpath clip-path='url(%23b)' fill='%234285F4' d='M48 48L17 24l-4-3 35-10z'/%3E%3C/svg%3E",
            use_container_width=False
        )
        if result and "token" in result:
            id_token = result["token"]["id_token"]
            user_info = jwt.decode(id_token, options={"verify_signature": False})
            st.session_state['authenticated'] = True
            st.session_state['user_info'] = user_info
            st.rerun()
    else:
        user_info = st.session_state['user_info'] or {}
        pic = user_info.get('picture')
        if pic:
            st.image(pic, width=48)
        st.write(f"Usuario: {user_info.get('name', '')}")
        st.write(f"Correo: {user_info.get('email', '')}")
        if st.button("Cerrar sesión"):
            st.session_state['authenticated'] = False
            st.session_state['user_info'] = None
            st.rerun()

# Contenido principal
if st.session_state['authenticated']:
    user_info = st.session_state['user_info'] or {}
    st.success("¡Inicio de sesión exitoso!")
    st.write("Correo:", user_info.get("email"))
    st.write("Nombre:", user_info.get("name"))
else:
    st.info("Por favor, inicia sesión con tu cuenta de Google.")
