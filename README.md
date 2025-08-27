# App-FinDiario

Gestor simple de deudas personales con Streamlit y login con Google OAuth2.

## Requisitos

- Python 3.10+ (recomendado 3.11)
- PowerShell en Windows

## Entorno y dependencias

1. Crear entorno virtual y activarlo (PowerShell):

	```powershell
	py -m venv .venv
	.\.venv\Scripts\Activate.ps1
	python -m pip install --upgrade pip
	```

2. Instalar dependencias:

	```powershell
	pip install -r requirements.txt
	```

## Configurar Google OAuth2

1. Ve a Google Cloud Console → APIs & Services → Credentials.
2. Crea un OAuth 2.0 Client ID (tipo “Web application”).
3. En “Authorized redirect URIs” añade:
	- `http://localhost:8501`
4. Copia tu Client ID y Client Secret.
5. Crea un archivo `.env` a partir de `.env.example` y rellena:

	```env
	CLIENT_ID=tu-client-id.apps.googleusercontent.com
	CLIENT_SECRET=tu-client-secret
	REDIRECT_URI=http://localhost:8501
	```

Nota: `.env` ya está ignorado en `.gitignore` para evitar subir credenciales.

## Ejecutar la app

```powershell
streamlit run app_deudas.py
```

## Archivos

- `app_deudas.py`: app principal con login y gestión de deudas.
- `deudas.csv`: almacenamiento simple de datos en CSV.
- `login.py`: ejemplo mínimo de login con Google para pruebas.
- `.env.example`: plantilla de variables de entorno.
- `requirements.txt`: dependencias del proyecto.

## Seguridad

- No compartas tu Client Secret.
- En producción, usa HTTPS y dominios/redirect URIs oficiales.