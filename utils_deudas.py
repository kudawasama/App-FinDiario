import os
import pandas as pd
import json

def email_to_filename(email):
    import re
    return re.sub(r'[^a-zA-Z0-9]', '_', email)

def safe_int(val):
    try:
        num = pd.to_numeric(val, errors='coerce')
        if pd.isna(num):
            return 0
        return int(num)
    except Exception:
        return 0

def crear_archivo_csv(email):
    archivo_csv = os.path.join("datos_usuarios", f"deudas_{email_to_filename(email)}.csv")
    if not os.path.exists(archivo_csv):
        os.makedirs(os.path.dirname(archivo_csv), exist_ok=True)
        df_vacio = pd.DataFrame(columns=['Acreedor', 'Monto Total', 'Monto Restante', 'Ultimo Pago', 'Fecha Vencimiento'])
        df_vacio.to_csv(archivo_csv, index=False)

def cargar_datos(email):
    crear_archivo_csv(email)
    archivo_csv = os.path.join("datos_usuarios", f"deudas_{email_to_filename(email)}.csv")
    try:
        df = pd.read_csv(archivo_csv)
        for col in ['Monto Total', 'Monto Restante', 'Ultimo Pago']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        return df
    except pd.errors.EmptyDataError:
        df_vacio = pd.DataFrame(columns=['Acreedor', 'Monto Total', 'Monto Restante', 'Ultimo Pago', 'Fecha Vencimiento'])
        df_vacio.to_csv(archivo_csv, index=False)
        return pd.DataFrame(columns=['Acreedor', 'Monto Total', 'Monto Restante', 'Ultimo Pago', 'Fecha Vencimiento'])

def guardar_datos(email, df):
    archivo_csv = os.path.join("datos_usuarios", f"deudas_{email_to_filename(email)}.csv")
    df.to_csv(archivo_csv, index=False)

def eliminar_deuda(email, indice):
    df = cargar_datos(email)
    if 0 <= indice < len(df):
        df = df.drop(indice).reset_index(drop=True)
        guardar_datos(email, df)
        return True, "Deuda eliminada exitosamente."
    else:
        return False, "Índice de deuda inválido."

def anadir_deuda(email, acreedor, monto_total, fecha_vencimiento):
    df = cargar_datos(email)
    try:
        monto_total = int(monto_total)
    except Exception:
        monto_total = 0
    nueva_fila = {
        'Acreedor': acreedor,
        'Monto Total': monto_total,
        'Monto Restante': monto_total,
        'Ultimo Pago': 0,
        'Fecha Vencimiento': fecha_vencimiento
    }
    df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
    guardar_datos(email, df)

def registrar_pago(email, indice, monto_pago):
    df = cargar_datos(email)
    monto_restante_actual = safe_int(df.loc[indice, 'Monto Restante'])
    try:
        monto_pago = safe_int(monto_pago)
    except Exception:
        return False, "El monto del pago debe ser un número entero válido."
    if monto_pago > monto_restante_actual:
        return False, "El pago no puede ser mayor que el monto restante."
    df.loc[indice, 'Monto Restante'] = monto_restante_actual - monto_pago
    df.loc[indice, 'Ultimo Pago'] = monto_pago
    guardar_datos(email, df)
    return True, "Pago registrado con éxito."
