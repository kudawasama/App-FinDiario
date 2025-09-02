import streamlit as st
from utils_deudas import cargar_datos, anadir_deuda, eliminar_deuda, registrar_pago, safe_int

def mostrar_pagina_deudas(user_email):
    st.header("Gestor de Deudas Personales")
    st.markdown("Usa esta aplicación para controlar tus deudas y registrar tus pagos.")
    # El menú de opciones ya se gestiona en app_deudas.py
    opcion = st.session_state.get('opcion_deudas', None)
    if opcion == "Añadir Deuda":
        st.header("Añadir Nueva Deuda")
        with st.form("form_anadir_deuda"):
            acreedor = st.text_input("Nombre del acreedor")
            monto_total = st.number_input("Monto total de la deuda", min_value=0, step=1)
            fecha_vencimiento = st.date_input("Fecha de vencimiento")
            enviado = st.form_submit_button("Añadir Deuda")
            if enviado:
                if acreedor and monto_total > 0:
                    fecha_vencimiento_str = fecha_vencimiento.strftime("%d-%m-%Y")
                    anadir_deuda(user_email, acreedor, monto_total, fecha_vencimiento_str)
                    st.success("Deuda añadida exitosamente.")
                else:
                    st.error("Por favor, llena todos los campos.")
    elif opcion == "Listar y Pagar":
        st.header("Listado de Deudas y Pagos")
        df = cargar_datos(user_email)
        if not df.empty:
            st.dataframe(df.style.highlight_max(axis=0, color='red', subset=['Monto Restante']))
            st.subheader("Registrar un Pago")
            with st.form("form_registrar_pago"):
                deuda_a_pagar = st.selectbox(
                    "Selecciona la deuda a pagar:",
                    options=df.index,
                    format_func=lambda x: f"{df.loc[x, 'Acreedor']} - ${safe_int(df.loc[x, 'Monto Restante']):,} restantes"
                )
                monto_pago = st.number_input("Monto del pago", min_value=0, step=1)
                pago_enviado = st.form_submit_button("Registrar Pago")
                if pago_enviado:
                    if monto_pago > 0:
                        exito, mensaje = registrar_pago(user_email, deuda_a_pagar, monto_pago)
                        if exito:
                            st.success(mensaje)
                            st.rerun()
                        else:
                            st.error(mensaje)
                    else:
                        st.error("El monto del pago debe ser un número positivo.")
            st.subheader("Eliminar una Deuda")
            with st.form("form_eliminar_deuda"):
                deuda_a_eliminar = st.selectbox(
                    "Selecciona la deuda a eliminar:",
                    options=df.index,
                    format_func=lambda x: f"{df.loc[x, 'Acreedor']} - ${safe_int(df.loc[x, 'Monto Restante']):,} restantes (vence {df.loc[x, 'Fecha Vencimiento']})"
                )
                eliminar_enviado = st.form_submit_button("Eliminar Deuda")
                if eliminar_enviado:
                    exito, mensaje = eliminar_deuda(user_email, deuda_a_eliminar)
                    if exito:
                        st.success(mensaje)
                        st.rerun()
                    else:
                        st.error(mensaje)
        else:
            st.info("Aún no tienes deudas registradas.")
    elif opcion == "Resumen de Deudas":
        st.header("Resumen General")
        df = cargar_datos(user_email)
        if not df.empty:
            monto_total_deudas = int(df['Monto Total'].sum())
            monto_pagado = int(df['Ultimo Pago'].sum())
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Monto Total de Deudas", value=f"${monto_total_deudas:,}")
            with col2:
                st.metric(label="Monto Total Pagado", value=f"${monto_pagado:,}")
        else:
            st.info("Aún no tienes deudas registradas para mostrar un resumen.")
