import streamlit as st
from utils_deudas import cargar_datos, anadir_deuda, eliminar_deuda, registrar_pago, safe_int

def mostrar_pagina_deudas(user_email):
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
		st.session_state["deuda_añadida"] = True
		st.experimental_rerun()
	if st.session_state.get("deuda_añadida"):
		st.success("Deuda añadida correctamente.")
		st.session_state["deuda_añadida"] = False
    
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
	if st.button("Registrar pago") and len(df)>0:
		exito, mensaje = registrar_pago(user_email, indice_pago, monto_pago)
		if exito:
			st.success(mensaje)
			st.experimental_rerun()
		else:
			st.error(mensaje)
