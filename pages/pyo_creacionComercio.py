import streamlit as st
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
# Aquí importamos toda tu lógica desde el nuevo módulo:
from modulos.componente_ruteo import renderizar_interfaz_ruteo, preparar_datos_tabla, generar_json

st.set_page_config(page_title="Configurador Payout", layout="wide")

st.title("🏢 Nuevo comercio Payout (Creación)")
st.header("Datos del Comercio")

col_datos1, col_datos2= st.columns(2)
with col_datos1:
    nombre_comercio = st.text_input("Nombre Comercial de la cuenta")
    razon_social = st.text_input("Razón Social")
    tipo_documento = st.selectbox("Tipo de Documento", ["RUC", "DNI", "CEX"])
    numero_documento = st.text_input("Número de Documento")

with col_datos2:
    tipo_producto = st.selectbox("Tipo de Producto", ["Payout Regular", "Instant Payout"])
    nombre_newUsuario = st.text_input("Nombre Usuario")
    correo_newUsuario = st.text_input("Correo de Usuario")

archivo_adjunto = st.file_uploader("Adjuntar documento", type=["pdf", "docx", "doc"])
st.divider()

# --- MAGIA DE LA MODULARIZACIÓN ---
# Llamamos a las 3 funciones del componente y la app se dibuja sola
config_ruteo = renderizar_interfaz_ruteo()
df_resumen = preparar_datos_tabla(config_ruteo)
json_final = generar_json(config_ruteo)

# ----------------------------------
st.header("📋 Resumen de Configuración")
st.dataframe(df_resumen, use_container_width=True, hide_index=True)
st.divider()

st.subheader("📧 Enviar Solicitud")
mensaje_personalizado = st.text_area("Mensaje opcional para la solicitud:", placeholder="Escribe aquí cualquier detalle adicional")

if st.button("Generar Solicitud"):
    try:
        remitente = st.secrets["EMAIL_USER"]
        password = st.secrets["EMAIL_PASS"]
        destinatario = st.secrets["EMAIL_DEST"]

        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = destinatario
        msg['Subject'] = "ONB-Generación de credenciales-"+ nombre_comercio+" -"+tipo_producto

        tabla_html = df_resumen.to_html(index=False, border=1)
        mensaje_html = f"<p><strong>Detalles:</strong><br>{mensaje_personalizado.replace(chr(10), '<br>')}</p>" if mensaje_personalizado.strip() else ""

        cuerpo_html = f"""
        <html><body>
            <h2>Solicitud de nuevas credenciales para "{nombre_comercio}" - {tipo_producto}</h2>
            {mensaje_html}
            <ul>Nombre del comercio: {nombre_comercio}</ul>
            <ul>Razón Social: {razon_social}</ul>
            <ul>Tipo de documento: {tipo_documento}</ul>
            <ul>Número de documento: {numero_documento}</ul>
            <ul>Tipo de Producto: {tipo_producto}</ul>
            <ul>Nombre de usuario: {nombre_newUsuario}</ul>
            <ul>Corre de usuario: {correo_newUsuario}</ul>
            <h3>Configuración de ruteo y/o titularidad</h3>
            <br>{tabla_html}
        </body></html>
        """
        msg.attach(MIMEText(cuerpo_html, 'html'))

        if archivo_adjunto is not None:
            file_bytes = archivo_adjunto.read()
            adjunto = MIMEApplication(file_bytes, Name=archivo_adjunto.name)
            adjunto['Content-Disposition'] = f'attachment; filename="{archivo_adjunto.name}"'
            msg.attach(adjunto)
            archivo_adjunto.seek(0)

        with smtplib.SMTP('smtp.office365.com', 587) as server:
            server.starttls()
            server.login(remitente, password)
            server.send_message(msg)

        st.success(f"✅ ¡Resumen enviado exitosamente a {destinatario}!")
    except Exception as e:
        st.error(f"❌ Ocurrió un error al enviar el correo: {e}")

st.divider()
st.header("3. JSON Resultante")
st.code(json.dumps(json_final, indent=4, ensure_ascii=False), language='json')
st.download_button(label="Descargar JSON", file_name="config.json", mime="application/json", data=json.dumps(json_final, indent=4))