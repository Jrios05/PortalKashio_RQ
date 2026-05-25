import streamlit as st

# Configuración principal de la página web
st.set_page_config(page_title="Portal de Operaciones", layout="wide", initial_sidebar_state="expanded")

# --- 1. DEFINIR LAS PÁGINAS ---

# Módulo PAYMENT
pay_creacion = st.Page("pages/pyi_creacionComercio.py", title="Creación de comercio", icon="🏢")
pay_canales = st.Page("pages/pyi_configuracion.py", title="Configuración de Canales de pago", icon="💳")

# Módulo PAYOUT
payout_creacion = st.Page("pages/pyo_creacionComercio.py", title="Creación de comercio", icon="🏢")
payout_config = st.Page("pages/pyo_ruteo.py", title="Configuración Ruteo y titularidad", icon="⚙️")

# --- 2. ARMAR LA NAVEGACIÓN CON LA JERARQUÍA DE LA IMAGEN ---
pg = st.navigation({
    "Payment": [pay_creacion,pay_canales],
    "Payout": [payout_creacion,payout_config]
})

# Ejecutar la navegación
pg.run()