import streamlit as st
from streamlit_gsheets import GSheetsConnection
import modulo_ninos, modulo_adultos, modulo_resumen

# 1. Configuración (Layout centered es mejor para móvil)
st.set_page_config(page_title="BBQ Manager", layout="centered", page_icon="⚽")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    div.stButton > button { border-radius: 20px; }
    [data-testid="stSidebarNav"] { display: none; } 
    
    /* FUERZA LAS BANDERAS EN HORIZONTAL Y SIN FONDO */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:nth-child(1) [data-testid="stHorizontalBlock"] {
        gap: 0rem !important;
    }
    
    [data-testid="stSidebar"] div.stButton > button {
        border: none !important;
        background-color: transparent !important;
        font-size: 28px !important; /* Un poco más grandes para que sea fácil darles con el dedo */
        padding: 0px !important;
        box-shadow: none !important;
        width: auto !important;
        margin: 0 auto !important;
        display: block !important;
    }

    /* ELIMINA MARGENES EXTRA EN LA SIDEBAR */
    [data-testid="stSidebarUserContent"] {
        padding-top: 2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Conexión y Carga
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=600)
def load_config():
    import pandas as pd
    sheet_id = "1L7P6i_vtAOonFxxiaM2Vk-mMka1rEJtfHCf9aJPmjco"
    url_menu = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=config_comida"
    url_lang = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=idiomas"
    return pd.read_csv(url_menu), pd.read_csv(url_lang)

df_menu, df_lang = load_config()

# --- SIDEBAR ESTRUCTURADA ---
with st.sidebar:
    # A. SELECTOR DE IDIOMA (En una sola fila arriba)
    if 'lang_choice' not in st.session_state:
        st.session_state.lang_choice = 'Español'
    
    # Creamos 2 columnas para las banderas
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

    # C. TU LOGO (Abajo del todo, muy pequeño y elegante)
    # Usamos st.spacer o markdown para empujar el logo al fondo
    st.markdown("<br>" * 15, unsafe_allow_html=True) 
    st.divider()
    
    # Aquí es donde achicamos el logo al máximo usando columnas laterales vacías
    # El ratio [2, 1, 2] hace que el logo central sea pequeñito
    _, col_logo_fino, _ = st.columns([2, 1, 2]) 
    with col_logo_fino:
        st.image("assets/logo.png", use_container_width=True)
    
    # Tu firma discreta
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