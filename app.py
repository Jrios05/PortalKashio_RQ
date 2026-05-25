import streamlit as st

# Configuración principal de la página web
st.set_page_config(page_title="Portal de Operaciones", layout="wide", initial_sidebar_state="expanded")

# --- 1. DEFINIR LAS PÁGINAS ---

# Módulo PAYMENT
pay_creacion = st.Page("pages/pay_creacion.py", title="Creación de comercio", icon="🏢")
pay_canales = st.Page("pages/pay_canales.py", title="Canales de pago", icon="💳")
pay_actualizacion = st.Page("pages/pay_actualizacion.py", title="Actualización de cuenta", icon="🔄")

# Módulo PAYOUT
payout_creacion = st.Page("pages/payout_creacion.py", title="Creación de comercio", icon="🏢")
payout_config = st.Page("pages/payout_ruteo.py", title="Ruteo y titularidad", icon="⚙️")

# --- 2. ARMAR LA NAVEGACIÓN CON LA JERARQUÍA DE LA IMAGEN ---
pg = st.navigation({
    "Payment": [pay_creacion],
    "Payment - Configuración": [pay_canales, pay_actualizacion],
    "Payout": [payout_creacion],
    "Payout - Configuración": [payout_config]
})

# Ejecutar la navegación
pg.run()