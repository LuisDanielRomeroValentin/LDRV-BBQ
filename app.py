import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import modulo_ninos, modulo_adultos, modulo_resumen

# 1. Configuración
st.set_page_config(page_title="BBQ Manager", layout="centered", page_icon="⚽")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    div.stButton > button { border-radius: 20px; }
    [data-testid="stSidebarNav"] { display: none; } 
    
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:nth-child(1) [data-testid="stHorizontalBlock"] {
        gap: 0rem !important;
    }
    
    [data-testid="stSidebar"] div.stButton > button {
        border: none !important;
        background-color: transparent !important;
        font-size: 28px !important;
        padding: 0px !important;
        box-shadow: none !important;
        width: auto !important;
        margin: 0 auto !important;
        display: block !important;
    }

    [data-testid="stSidebarUserContent"] {
        padding-top: 2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Función para conectar a Google Sheets
@st.cache_resource
def init_connection():
    creds_dict = {
        "type": st.secrets["connections"]["gsheets"]["type"],
        "project_id": st.secrets["connections"]["gsheets"]["project_id"],
        "private_key_id": st.secrets["connections"]["gsheets"]["private_key_id"],
        "private_key": st.secrets["connections"]["gsheets"]["private_key"],
        "client_email": st.secrets["connections"]["gsheets"]["client_email"],
        "client_id": st.secrets["connections"]["gsheets"]["client_id"],
        "auth_uri": st.secrets["connections"]["gsheets"]["auth_uri"],
        "token_uri": st.secrets["connections"]["gsheets"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["connections"]["gsheets"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["connections"]["gsheets"]["client_x509_cert_url"],
    }
    
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client

# Función para leer datos - CON _client para evitar hashing
@st.cache_data(ttl=600)
def read_sheet(_client, sheet_id, worksheet_name):
    sheet = _client.open_by_key(sheet_id)
    worksheet = sheet.worksheet(worksheet_name)
    data = worksheet.get_all_values()
    if not data:
        return pd.DataFrame()
    headers = data[0]
    rows = data[1:]
    return pd.DataFrame(rows, columns=headers)

# Función para actualizar datos (sin caché, no necesita decorador)
def update_sheet(client, sheet_id, worksheet_name, df):
    sheet = client.open_by_key(sheet_id)
    worksheet = sheet.worksheet(worksheet_name)
    worksheet.clear()
    if not df.empty:
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())

# Clase wrapper para mantener compatibilidad con los módulos
class GSheetsConnection:
    def __init__(self, client, sheet_id):
        self.client = client
        self.sheet_id = sheet_id
    
    def read(self, worksheet, ttl=0):
        return read_sheet(self.client, self.sheet_id, worksheet)
    
    def update(self, worksheet, data):
        update_sheet(self.client, self.sheet_id, worksheet, data)

# Inicializar conexión
client = init_connection()

# Obtener el ID de la hoja desde el secrets
sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
sheet_id = sheet_url.split("/d/")[1].split("/")[0]
conn = GSheetsConnection(client, sheet_id)

# Cargar configuración - CON _client para evitar hashing
@st.cache_data(ttl=600)
def load_config(_client, _sheet_id):
    df_menu = read_sheet(_client, _sheet_id, "config_comida")
    df_lang = read_sheet(_client, _sheet_id, "idiomas")
    return df_menu, df_lang

df_menu, df_lang = load_config(client, sheet_id)

# --- SIDEBAR ESTRUCTURADA ---
with st.sidebar:
    # A. SELECTOR DE IDIOMA
    if 'lang_choice' not in st.session_state:
        st.session_state.lang_choice = 'Español'
    
    col_banderas = st.columns(2)
    with col_banderas[0]:
        if st.button("🇪🇸", key="btn_es"):
            st.session_state.lang_choice = 'Español'
            st.rerun()
    with col_banderas[1]:
        if st.button("🇬🇧", key="btn_en"):
            st.session_state.lang_choice = 'English'
            st.rerun()
    
    t = df_lang.set_index("Key")[st.session_state.lang_choice].to_dict()
    
    st.markdown("---")
    
    # B. MENÚ DE NAVEGACIÓN
    opcion = st.radio(
        t.get('menu_title', 'Selecciona sección:'),
        options=["Niños", "Adultos", "Resumen"],
        format_func=lambda x: f"👦 {t.get('tab_kids')}" if x == "Niños" else (f"👨‍🏫 {t.get('tab_adults')}" if x == "Adultos" else f"🛒 {t.get('tab_resumen')}")
    )

    # C. LOGO
    st.markdown("<br>" * 15, unsafe_allow_html=True) 
    st.divider()
    
    _, col_logo_fino, _ = st.columns([2, 1, 2]) 
    with col_logo_fino:
        try:
            st.image("assets/logo.png", use_container_width=True)
        except:
            st.caption("📷 LDRV")
    
    st.markdown(
        "<div style='text-align: center; color: gray; font-size: 10px;'>"
        "Developed by LDRV</div>", 
        unsafe_allow_html=True
    )

# --- CUERPO PRINCIPAL ---
st.title(f"⚽ {t.get('title', 'BBQ Manager')}")

if opcion == "Niños":
    modulo_ninos.render(conn, t, df_menu)
elif opcion == "Adultos":
    modulo_adultos.render(conn, t, df_menu)
else:
    modulo_resumen.render(conn, t)