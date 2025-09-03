import streamlit as st
import os
import json
from utils_grupos_eventos import cargar_grupos, guardar_grupos, cargar_eventos, guardar_eventos

def mostrar_pagina_eventos(user_email):
    st.header("Gestión de Eventos de Grupo")
    grupos = cargar_grupos(user_email)
    if not grupos:
        st.info("Primero debes crear o unirte a un grupo.")
        return
    grupo_nombres = [g['nombre'] for g in grupos]
    grupo_idx = st.selectbox("Selecciona un grupo", range(len(grupo_nombres)), format_func=lambda i: grupo_nombres[i])
    grupo = grupos[grupo_idx]
    eventos = cargar_eventos(grupo['id'])
    st.subheader(f"Eventos en el grupo: {grupo['nombre']}")
    if eventos:
        evento_nombres = [e['nombre'] for e in eventos]
        evento_idx = st.selectbox("Selecciona un evento", range(len(evento_nombres)), format_func=lambda i: evento_nombres[i])
        evento = eventos[evento_idx]
        st.write(f"Administrador: {evento['admin']}")
        st.write("Participantes y montos:")
        montos_editados = {}
        # Historial de pagos
        st.subheader("Historial de pagos")
        if 'historial' not in evento:
            evento['historial'] = []
        for h in evento['historial']:
            st.write(f"{h['fecha']} - {h['usuario']}: ${h['monto']} {'(Confirmado)' if h.get('confirmado') else ''}")
        for p in evento['participantes']:
            monto = evento['montos'].get(p, 0)
            pago = evento['pagos'].get(p, {})
            estado = "Pago pendiente" if not pago.get('confirmado') else "Pago confirmado"
            st.write(f"- {p}: ${monto} | Estado: {estado}")
            # Edición de montos por el administrador
            if user_email == evento['admin']:
                nuevo_monto = st.number_input(f"Editar monto de {p}", min_value=0, value=monto, key=f"edit_monto_{p}")
                montos_editados[p] = nuevo_monto
            if user_email == p:
                st.subheader("Registrar pago")
                monto_pago = st.number_input("Monto a pagar", min_value=0, max_value=monto, step=1, key=f"monto_pago_{p}")
                comprobante = st.file_uploader("Adjuntar comprobante", type=["jpg", "jpeg", "png", "pdf"], key=f"comprobante_{p}")
                if st.button("Registrar pago", key=f"pago_{p}"):
                    from datetime import datetime
                    evento['pagos'][p] = {"monto": monto_pago, "comprobante": comprobante.name if comprobante else None, "confirmado": False}
                    evento['historial'].append({
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "usuario": p,
                        "monto": monto_pago,
                        "confirmado": False
                    })
                    guardar_eventos(grupo['id'], eventos)
                    if comprobante:
                        carpeta = os.path.join("datos_usuarios", f"comprobantes_{grupo['id']}")
                        os.makedirs(carpeta, exist_ok=True)
                        ruta = os.path.join(carpeta, comprobante.name)
                        with open(ruta, "wb") as f:
                            f.write(comprobante.read())
                    st.success("Pago registrado. Espera la confirmación del administrador.")
                    st.experimental_rerun()
            if user_email == evento['admin'] and pago.get('comprobante'):
                st.write(f"Comprobante: {pago['comprobante']}")
                if st.button(f"Confirmar pago de {p}", key=f"confirmar_{p}"):
                    evento['pagos'][p]['confirmado'] = True
                    # Actualizar historial
                    for h in evento['historial']:
                        if h['usuario'] == p and h['monto'] == pago['monto'] and not h.get('confirmado'):
                            h['confirmado'] = True
                    guardar_eventos(grupo['id'], eventos)
                    st.success(f"Pago de {p} confirmado.")
                    st.experimental_rerun()
        # Botón para guardar los montos editados
        if user_email == evento['admin'] and st.button("Guardar montos editados"):
            for p, nuevo_monto in montos_editados.items():
                evento['montos'][p] = nuevo_monto
            guardar_eventos(grupo['id'], eventos)
            st.success("Montos actualizados correctamente.")
            st.experimental_rerun()
        # Mini chat
        st.subheader("Chat del evento")
        if 'chat' not in evento:
            evento['chat'] = []
        for msg in evento['chat']:
            st.write(f"{msg['fecha']} - {msg['usuario']}: {msg['mensaje']}")
        nuevo_msg = st.text_input("Escribe un mensaje", key="chat_msg")
        if st.button("Enviar mensaje", key="enviar_msg") and nuevo_msg:
            from datetime import datetime
            evento['chat'].append({
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "usuario": user_email,
                "mensaje": nuevo_msg
            })
            guardar_eventos(grupo['id'], eventos)
            st.experimental_rerun()
    else:
        st.info("No hay eventos en este grupo.")
    st.subheader("Crear nuevo evento")
    nombre_evento = st.text_input("Nombre del evento")
    admin_evento = user_email
    participantes = st.multiselect("Selecciona participantes", grupo['miembros'], default=[user_email])
    monto_total = st.number_input("Monto total del evento", min_value=0, step=1)
    if st.button("Crear evento") and nombre_evento and participantes and monto_total > 0:
        monto_por_persona = monto_total // len(participantes)
        evento = {
            "id": f"{nombre_evento.replace(' ','_').lower()}_{len(eventos)}",
            "nombre": nombre_evento,
            "admin": admin_evento,
            "participantes": participantes,
            "montos": {p: monto_por_persona for p in participantes},
            "pagos": {}
        }
        eventos.append(evento)
        guardar_eventos(grupo['id'], eventos)
        st.success("Evento creado correctamente.")
        st.experimental_rerun()
