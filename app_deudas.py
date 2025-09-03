import streamlit as st
import os
import hashlib
import json
st.set_page_config(page_title="Gestor de Deudas Personales", page_icon="💸", layout="wide", initial_sidebar_state="expanded")

# Archivo donde se guardan los usuarios registrados
# --- Gestión de contactos ---
def contactos_file(email):
    return os.path.join("datos_usuarios", f"contactos_{email_to_filename(email)}.json")

def cargar_contactos(email):
    archivo = contactos_file(email)
    if os.path.exists(archivo):
        with open(archivo, "r") as f:
            return json.load(f)
    return []

def guardar_contactos(email, contactos):
    archivo = contactos_file(email)
    with open(archivo, "w") as f:
        json.dump(contactos, f)

def agregar_contacto(email, contacto_email):
    contactos = cargar_contactos(email)
    if contacto_email not in contactos:
        contactos.append(contacto_email)
        guardar_contactos(email, contactos)
        return True, "Contacto agregado."
    else:
        return False, "El contacto ya existe."

def eliminar_contacto(email, contacto_email):
    contactos = cargar_contactos(email)
    if contacto_email in contactos:
        contactos.remove(contacto_email)
        guardar_contactos(email, contactos)
        return True, "Contacto eliminado."
    else:
        return False, "El contacto no existe."
USUARIOS_FILE = "usuarios.json"

# Función para hashear la contraseña
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Cargar usuarios desde el archivo JSON
def cargar_usuarios():
    if os.path.exists(USUARIOS_FILE):
        with open(USUARIOS_FILE, "r") as f:
            return json.load(f)
    return {}

# Guardar usuarios en el archivo JSON
def guardar_usuarios(usuarios):
    with open(USUARIOS_FILE, "w") as f:
        json.dump(usuarios, f)

# Registrar un nuevo usuario
def registrar_usuario(email, password):
    usuarios = cargar_usuarios()
    if email in usuarios:
        return False, "El correo ya está registrado."
    usuarios[email] = hash_password(password)
    guardar_usuarios(usuarios)
    return True, "Usuario registrado exitosamente."

# Autenticar usuario
def autenticar_usuario(email, password):
    usuarios = cargar_usuarios()
    if email in usuarios and usuarios[email] == hash_password(password):
        return True
    return False

# Inicializar variables de sesión
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None

# Sidebar para login/registro
with st.sidebar:
    st.header("Autenticación")
    if not st.session_state['authenticated']:
        tab1, tab2 = st.tabs(["Iniciar sesión", "Registrarse"])
        with tab1:
            email = st.text_input("Correo electrónico")
            password = st.text_input("Contraseña", type="password")
            if st.button("Iniciar sesión"):
                if autenticar_usuario(email, password):
                    st.session_state['authenticated'] = True
                    st.session_state['user_email'] = email
                    st.success("¡Bienvenido!")
                    st.rerun()
                else:
                    st.error("Correo o contraseña incorrectos.")
        with tab2:
            email_reg = st.text_input("Correo electrónico para registro")
            password_reg = st.text_input("Contraseña para registro", type="password")
            if st.button("Registrarse"):
                exito, mensaje = registrar_usuario(email_reg, password_reg)
                if exito:
                    st.success(mensaje)
                else:
                    st.error(mensaje)
    else:
        st.write(f"Usuario: {st.session_state['user_email']}")
        if st.button("Cerrar sesión"):
            st.session_state['authenticated'] = False
            st.session_state['user_email'] = None
            st.rerun()

# Función para convertir email en nombre de archivo seguro
# Usar la función de utils_deudas.py
from utils_deudas import email_to_filename

# Si el usuario está autenticado, define el archivo CSV de deudas
if st.session_state['authenticated']:
    user_email = st.session_state['user_email']

    # --- Footer de privacidad simple ---
    st.markdown("""
    <div style='position:fixed;left:18px;bottom:18px;width:340px;background:rgba(30,30,30,0.92);border-radius:10px;box-shadow:0 2px 12px #0005;padding:12px 18px 10px 18px;font-size:13px;color:#e0e0e0;z-index:99999;opacity:0.97;'>
        <b>Política de privacidad:</b> Tus datos se almacenan únicamente en tu cuenta y no se comparten ni suben a la nube. Puedes descargar o eliminar tus datos en cualquier momento.
    </div>
    """, unsafe_allow_html=True)
    from modulos.pagina_deudas import mostrar_pagina_deudas
    from modulos.pagina_contactos import mostrar_pagina_contactos
    from modulos.pagina_grupos import mostrar_pagina_grupos

    # Definir el menú principal y la variable 'opcion' correctamente
    st.sidebar.header("Menú de opciones")
    opciones = ["Deudas", "Contactos", "Grupos", "Eventos"]
    opcion = st.sidebar.radio("Selecciona una opción:", opciones)
    st.session_state['opcion_deudas'] = opcion

    if opcion == "Deudas":
        mostrar_pagina_deudas(user_email)
    elif opcion == "Contactos":
        mostrar_pagina_contactos(user_email)
    elif opcion == "Grupos":
        mostrar_pagina_grupos(user_email)
    elif opcion == "Eventos":
        from pages.pagina_eventos import mostrar_pagina_eventos
        mostrar_pagina_eventos(user_email)
else:
    st.info("Por favor, inicia sesión con tu cuenta para acceder a la app de deudas.")



