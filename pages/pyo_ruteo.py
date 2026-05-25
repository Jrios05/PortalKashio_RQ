import streamlit as st
import json
from modulos.componente_ruteo import renderizar_interfaz_ruteo, preparar_datos_tabla, generar_json

st.set_page_config(page_title="Configuración de Ruteo", layout="wide")

st.title("⚙️ Modificar Ruteo y Titularidad (Configuración)")
st.info("Utiliza esta pantalla para ajustar los parámetros técnicos de ruteo y generar un nuevo JSON, sin necesidad de crear un comercio desde cero ni enviar correos.")

# --- INVOCAMOS EL COMPONENTE UNA VEZ MÁS ---
config_ruteo = renderizar_interfaz_ruteo()
df_resumen = preparar_datos_tabla(config_ruteo)
json_final = generar_json(config_ruteo)

# --------------------------------------------
st.header("📋 Resumen de Configuración")
st.dataframe(df_resumen, use_container_width=True, hide_index=True)
st.divider()

st.header("3. JSON Resultante")
st.code(json.dumps(json_final, indent=4, ensure_ascii=False), language='json')
st.download_button(label="Descargar JSON", file_name="config.json", mime="application/json", data=json.dumps(json_final, indent=4))