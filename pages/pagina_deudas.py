import streamlit as st
import os
from utils_deudas import cargar_datos, anadir_deuda, eliminar_deuda, registrar_pago, safe_int

def mostrar_pagina_deudas(user_email):
    st.subheader("Comprobantes y confirmación de pagos")
    # Mostrar comprobantes y permitir confirmación si el usuario pertenece a un grupo
    carpeta = os.path.join("datos_usuarios", f"comprobantes_{user_email.replace('@','_').replace('.','_')}")
    if os.path.exists(carpeta):
        archivos = os.listdir(carpeta)
        if archivos:
            for archivo in archivos:
                st.write(f"Comprobante: {archivo}")
                ruta = os.path.join(carpeta, archivo)
                ext = archivo.split('.')[-1].lower()
                if ext in ["jpg", "jpeg", "png"]:
                    st.image(ruta, caption=archivo, width=200)
                elif ext == "pdf":
                    st.write(f"[Ver PDF]({ruta})")
                # Confirmación de pago por grupo
                if st.button(f"Confirmar pago de {archivo}"):
                    # Aquí se podría guardar la confirmación en un archivo json por grupo
                    st.success(f"Pago confirmado por el grupo para {archivo}")
        else:
            st.info("No hay comprobantes registrados.")
    else:
        st.info("No hay comprobantes registrados.")
    st.header("Gestor de Deudas Personales")
    st.markdown("Usa esta aplicación para controlar tus deudas y registrar tus pagos.")
    
    df = cargar_datos(user_email)
    st.subheader("Tus deudas actuales")
    st.dataframe(df)
    
    st.subheader("Añadir nueva deuda")
    acreedor = st.text_input("Acreedor")
    monto_total = st.number_input("Monto total", min_value=0, step=1)
    fecha_vencimiento = st.date_input("Fecha de vencimiento")
    if st.button("Añadir deuda"):
        anadir_deuda(user_email, acreedor, monto_total, fecha_vencimiento)
        st.success("Deuda añadida correctamente.")
        st.experimental_rerun()
    
    st.subheader("Eliminar deuda")
    indice_eliminar = st.number_input("Índice de la deuda a eliminar", min_value=0, max_value=len(df)-1 if len(df)>0 else 0, step=1)
    if st.button("Eliminar deuda") and len(df)>0:
        exito, mensaje = eliminar_deuda(user_email, indice_eliminar)
        if exito:
            st.success(mensaje)
            st.experimental_rerun()
        else:
            st.error(mensaje)
    
    st.subheader("Registrar pago")
    indice_pago = st.number_input("Índice de la deuda a pagar", min_value=0, max_value=len(df)-1 if len(df)>0 else 0, step=1, key="pago")
    monto_pago = st.number_input("Monto del pago", min_value=0, step=1)
    comprobante = st.file_uploader("Adjuntar comprobante (opcional)", type=["jpg", "jpeg", "png", "pdf"])
    if st.button("Registrar pago") and len(df)>0:
        exito, mensaje = registrar_pago(user_email, indice_pago, monto_pago)
        if exito:
            # Guardar comprobante si se adjunta
            if comprobante:
                carpeta = os.path.join("datos_usuarios", f"comprobantes_{user_email.replace('@','_').replace('.','_')}")
                os.makedirs(carpeta, exist_ok=True)
                nombre = f"pago_{indice_pago}_{df.loc[indice_pago, 'Acreedor']}_{df.loc[indice_pago, 'Fecha Vencimiento']}.{comprobante.name.split('.')[-1]}"
                ruta = os.path.join(carpeta, nombre)
                with open(ruta, "wb") as f:
                    f.write(comprobante.read())
                st.success(f"Pago registrado y comprobante guardado: {nombre}")
            else:
                st.success(mensaje)
            st.experimental_rerun()
        else:
            st.error(mensaje)
