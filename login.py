import streamlit as st
from streamlit_oauth import OAuth2Component
import jwt

# Configura tus credenciales de Google OAuth2
CLIENT_ID = "REMOVED"
CLIENT_SECRET = "REMOVED"
REDIRECT_URI = "http://localhost:8501"

# Inicializa el componente OAuth2 para Google
oauth2 = OAuth2Component(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    authorize_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
    token_endpoint="https://oauth2.googleapis.com/token",
)

st.title("Iniciar sesión con Google")

# Botón de login
result = oauth2.authorize_button(
    name="Iniciar sesión con Google",
    redirect_uri=REDIRECT_URI,
    scope="openid email profile",
    key="google_login"
)




if result and "token" in result:
    st.success("¡Inicio de sesión exitoso!")
    st.write("Token de acceso:", result["token"]["access_token"])
    # Decodificar el id_token para obtener info del usuario
    id_token = result["token"]["id_token"]
    user_info = jwt.decode(id_token, options={"verify_signature": False})
    st.write("Correo:", user_info.get("email"))
    st.write("Nombre:", user_info.get("name"))
else:
    st.info("Por favor, inicia sesión con tu cuenta de Google.")
