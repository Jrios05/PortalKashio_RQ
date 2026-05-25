import streamlit as st
import pandas as pd
import json

# =====================================================================
# REPOSITORIOS DE DATOS
# =====================================================================
bancos_principales = {
    "psp_w13k323ed23dmd01": "(BCP) - Banco de Crédito del Perú",
    "psp_w13k12312341md02": "(BBVA) - BBVA Continental",
    "psp_w0328223930dmd04": "(Interbank) - Banco International del Perú",
    "psp_w191433107454": "Banco de la Nación",
    "psp_w133203223m3md03": "(Scotiabank)- Scotiabank"
}

billeteras_principales = {
    "psp_w156838159753": "Yape",
    "psp_3e74133b10bb44e6bd81": "PLIN",
    "psp_c6bee88b7b7e49bab8d4": "BIM",
    "psp_258a4fc095414c3b9c44": "LIGO",
    "psp_3f7ac8c5a4c8433288bd": "DALE",
    "psp_12f35441df4e426991e9": "PREXPE",
    "psp_28ed3cdabcbe49b098ee": "OH!"
}

todos_los_psps_dict = {**bancos_principales, **billeteras_principales}

def init_session_state():
    if "custom_routing" not in st.session_state:
        st.session_state.custom_routing = {}
    if "custom_titularidad" not in st.session_state:
        st.session_state.custom_titularidad = {}

# =====================================================================
# INTERFAZ GRÁFICA (UI) COMPARTIDA
# =====================================================================
def renderizar_interfaz_ruteo():
    init_session_state()
    st.title("⚙️ Ruteo y Titularidad")

    # Objeto para almacenar las decisiones del usuario y enviarlas a la tabla/json
    config = {
        "has_default_routing_bancos": False, "default_channel_bancos": None,
        "has_default_routing_billeteras": False, "default_channel_billeteras": None,
        "validate_interbranch": False, "yape_validation": False,
        "yape_merchant_id": "0000", "yape_category_code": "16",
        "activar_titularidad": False, "has_default_tit": False, "default_tit_provider": None
    }

    col1, col2 = st.columns(2)

    with col1:
        st.header("1. Configuración de Ruteo")
        with st.expander("1.1 Bank Transfer", expanded=True):
            st.subheader("Ruteo Global (Bancos)")
            config["has_default_routing_bancos"] = st.checkbox("Activar canal de ruteo por defecto", value=True, key="chk_def_bank")
            if config["has_default_routing_bancos"]:
                config["default_channel_bancos"] = st.selectbox("Canal por defecto:", ["GMONEY", "BATCH", "ALFIN"], key="sel_def_bank")

            st.markdown("---")
            st.subheader("Ruteo Específico (Bancos)")
            banco_id = st.selectbox("Seleccionar Banco:", options=list(bancos_principales.keys()), format_func=lambda x: bancos_principales[x], key="sel_spec_bank")
            canales_bancos = ["GMONEY", "BATCH", "ALFIN"]
            if banco_id == "psp_w13k323ed23dmd01": canales_bancos.append("BCP")
            elif banco_id == "psp_w13k12312341md02": canales_bancos.append("BBVA")

            canal_bank_spec = st.selectbox("Canal de dispersión:", canales_bancos, key="sel_ch_bank")
            if st.button("Agregar Excepción de Banco", key="btn_add_bank"):
                st.session_state.custom_routing[banco_id] = canal_bank_spec

        with st.expander("1.2 Billeteras", expanded=True):
            st.subheader("Ruteo Global (Billeteras)")
            config["has_default_routing_billeteras"] = st.checkbox("Activar canal de ruteo por defecto", value=False, key="chk_def_wall")
            if config["has_default_routing_billeteras"]:
                config["default_channel_billeteras"] = st.selectbox("Canal por defecto:", ["GMONEY"], key="sel_def_wall")

            st.markdown("---")
            st.subheader("Ruteo Específico (Solo Billeteras)")
            wallet_id = st.selectbox("Seleccionar Billetera:", options=list(billeteras_principales.keys()), format_func=lambda x: billeteras_principales[x], key="sel_spec_wall")
            canales_billeteras = ["GMONEY"]
            if wallet_id == "psp_w156838159753": canales_billeteras.append("YAPE")

            canal_wall_spec = st.selectbox("Canal de dispersión:", canales_billeteras, key="sel_ch_wall")
            if st.button("Agregar Excepción de Billetera", key="btn_add_wall"):
                st.session_state.custom_routing[wallet_id] = canal_wall_spec

        if st.button("Limpiar Todo el Ruteo Específico"):
            st.session_state.custom_routing = {}
            st.rerun()

        st.divider()
        st.subheader("Configuraciones Adicionales")
        config["validate_interbranch"] = st.checkbox("Solicitar ruteo para interplaza (BATCH)", value=False)
        if st.session_state.custom_routing.get("psp_w156838159753") == "YAPE":
            config["yape_validation"] = True
            config["yape_merchant_id"] = st.text_input("Yape Merchant ID", value="0000")
            config["yape_category_code"] = st.text_input("Yape Category Code", value="16")

    with col2:
        st.header("2. Configuración de Titularidad")
        is_routing_active = config["has_default_routing_bancos"] or config["has_default_routing_billeteras"] or len(st.session_state.custom_routing) > 0
        config["activar_titularidad"] = st.checkbox("¿Activar Titularidad?", disabled=not is_routing_active)

        if config["activar_titularidad"]:
            with st.expander("2.1 Configuración Global de Titularidad", expanded=True):
                config["has_default_tit"] = st.checkbox("Activar proveedor por defecto", value=True)
                if config["has_default_tit"]:
                    config["default_tit_provider"] = st.selectbox("Proveedor por defecto:", ["GMONEY"])

            with st.expander("2.2 Titularidad Específica", expanded=True):
                tipo_tit = st.radio("Categoría de PSP:", ["Bancos", "Billeteras"], horizontal=True)
                lista_tit = bancos_principales if tipo_tit == "Bancos" else billeteras_principales
                psp_tit_id = st.selectbox(f"Seleccionar {tipo_tit[:-1]}:", options=list(lista_tit.keys()), format_func=lambda x: lista_tit[x])

                opciones_validadores = ["GMONEY"]
                if tipo_tit == "Bancos" and psp_tit_id == "psp_w13k323ed23dmd01":
                    opciones_validadores.append("BCP")

                prov_tit = st.selectbox("Proveedor de Titularidad:", opciones_validadores)
                if st.button(f"Agregar Titularidad a {tipo_tit[:-1]}"):
                    st.session_state.custom_titularidad[psp_tit_id] = prov_tit

            if st.button("Limpiar Titularidad Específica"):
                st.session_state.custom_titularidad = {}
                st.rerun()

    st.divider()
    return config

# =====================================================================
# LÓGICA DE TABLA Y JSON
# =====================================================================
def preparar_datos_tabla(config):
    filas = []
    if config["has_default_routing_bancos"]:
        tit_bancos_def = "N/A"
        if config["activar_titularidad"]:
            tit_bancos_def = "ALFIN" if config["default_channel_bancos"] == "ALFIN" else (config["default_tit_provider"] if config["has_default_tit"] else "N/A")
        filas.append({"Categoría": "Bank Transfer", "Banco/PSP": "POR DEFECTO", "Canal": config["default_channel_bancos"], "Titularidad": tit_bancos_def})

    if config["has_default_routing_billeteras"]:
        is_merged = config["has_default_routing_bancos"] and config["default_channel_bancos"] == config["default_channel_billeteras"]
        canal_val = f"{config['default_channel_billeteras']} (Unificado)" if is_merged else config["default_channel_billeteras"]
        tit_wall_def = "N/A"
        if config["activar_titularidad"]:
            tit_wall_def = "ALFIN" if config["default_channel_billeteras"] == "ALFIN" else (config["default_tit_provider"] if config["has_default_tit"] else "N/A")
        filas.append({"Categoría": "Billeteras", "Banco/PSP": "POR DEFECTO", "Canal": canal_val, "Titularidad": tit_wall_def})

    psps_con_override = set(list(st.session_state.custom_routing.keys()) + list(st.session_state.custom_titularidad.keys()))
    for psp in psps_con_override:
        cat = "Bank Transfer" if psp in bancos_principales else "Billeteras"
        nombre = todos_los_psps_dict.get(psp, psp)

        if psp in st.session_state.custom_routing: ruteo = st.session_state.custom_routing[psp]
        elif psp in bancos_principales: ruteo = config["default_channel_bancos"] if config["has_default_routing_bancos"] else "N/A"
        else: ruteo = config["default_channel_billeteras"] if config["has_default_routing_billeteras"] else "N/A"

        if config["activar_titularidad"]:
            if ruteo == "ALFIN": tit = "ALFIN"
            elif psp == "psp_w156838159753" and ruteo == "YAPE": tit = "YAPE"
            elif psp in st.session_state.custom_titularidad: tit = st.session_state.custom_titularidad[psp]
            elif config["has_default_tit"]: tit = config["default_tit_provider"]
            else: tit = "N/A"
        else: tit = "N/A"

        filas.append({"Categoría": cat, "Banco/PSP": nombre, "Canal": ruteo, "Titularidad": tit})

    if config["validate_interbranch"]:
        val_int = config["default_tit_provider"] if (config["activar_titularidad"] and config["has_default_tit"]) else "N/A"
        filas.append({"Categoría": "Interplaza", "Banco/PSP": "Interplaza", "Canal": "BATCH", "Titularidad": val_int})

    return pd.DataFrame(filas)

def generar_json(config):
    resultado = {}
    routing = {}

    if config["has_default_routing_bancos"]: routing["DEFAULT"] = config["default_channel_bancos"]
    if config["has_default_routing_billeteras"]:
        if not (config["has_default_routing_bancos"] and config["default_channel_bancos"] == config["default_channel_billeteras"]):
            for psp_w in billeteras_principales.keys():
                if psp_w not in st.session_state.custom_routing: routing[psp_w] = config["default_channel_billeteras"]

    for psp, canal in st.session_state.custom_routing.items(): routing[psp] = canal
    if routing: resultado["routing"] = routing

    if config["yape_validation"]:
        resultado["yape_validation"] = True
        resultado["yape_configuration"] = {"yape_merchant_id": config["yape_merchant_id"], "yape_category_code": config["yape_category_code"]}

    if config["validate_interbranch"]: resultado["validate_interbranch"] = True

    only_yape_local = (len(st.session_state.custom_routing) == 1 and st.session_state.custom_routing.get("psp_w156838159753") == "YAPE" and not (config["has_default_routing_bancos"] or config["has_default_routing_billeteras"]))

    if config["activar_titularidad"] and not only_yape_local:
        provider = {}
        if config["has_default_tit"]: provider["DEFAULT"] = config["default_tit_provider"]
        for psp, prov in st.session_state.custom_titularidad.items(): provider[psp] = prov
        resultado["account_holder"] = {"provider": provider, "validate": True, "audit_mode": False, "validate_cci": True, "validate_wallet": True, "validate_account": True}

    alfin_ruteado = ((config["has_default_routing_bancos"] and config["default_channel_bancos"] == "ALFIN") or (config["has_default_routing_billeteras"] and config["default_channel_billeteras"] == "ALFIN") or any(c == "ALFIN" for c in st.session_state.custom_routing.values()))
    if alfin_ruteado and config["activar_titularidad"]: resultado["alfin_v3_enabled"] = True

    return resultado