import streamlit as st
import time
from motor_control import MotorController

# 1. Configuración inicial de la página
st.set_page_config(page_title="Robomato V1 - Calibración", page_icon="🤖", layout="wide")

# 2. Inicializar el controlador (Evita que se reinicie la conexión con cada clic)
if 'robot' not in st.session_state:
    try:
        st.session_state.robot = MotorController()
        st.success("🤖 Conexión con Arduino establecida.")
    except:
        st.error("❌ No se detectó el Arduino. Verifique el cable USB.")
        st.session_state.robot = None

robot = st.session_state.robot

# --- INTERFAZ VISUAL ---
st.title("🎮 Panel de Pruebas y Calibración - Robomato V1")

# BOTÓN DE EMERGENCIA (E-STOP)
if st.button("🚨 PARADA DE EMERGENCIA (E-STOP)", type="primary", use_container_width=True):
    if robot and robot.ser:
        robot.ser.write(b"M112\n") 
        st.error("!!! SISTEMA BLOQUEADO !!! Reinicie el Arduino para continuar.")
    else:
        st.warning("Sin conexión activa para detener.")

st.divider()

col_controles, col_monitor = st.columns([2, 1])

with col_controles:
    st.header("🕹️ Movimiento Manual (Jogging)")
    paso = st.select_slider("Distancia (mm)", options=[1, 5, 10, 50, 100], value=10)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("Eje X")
        if st.button("X -"): robot._enviar_comando(f"G0 X-{paso}")
        if st.button("X +"): robot._enviar_comando(f"G0 X{paso}")
    with c2:
        st.subheader("Eje Y")
        if st.button("Y -"): robot._enviar_comando(f"G0 Y-{paso}")
        if st.button("Y +"): robot._enviar_comando(f"G0 Y{paso}")
    with c3:
        st.subheader("Eje Z")
        if st.button("Z - (Subir)"): robot._enviar_comando(f"G0 Z-{paso}")
        if st.button("Z + (Bajar)"): robot._enviar_comando(f"G0 Z{paso}")

    # --- AQUÍ VA EL NUEVO BLOQUE DE COMANDOS DIRECTOS ---
    st.divider()
    st.header("⌨️ Consola G-Code Manual")
    comando_manual = st.text_input("Escribe tu comando (Ej: G0 X100 Y50 Z-20)", "")

    if st.button("Enviar Comando"):
        if comando_manual and robot:
            with st.spinner(f"Enviando {comando_manual}..."):
                exito = robot._enviar_comando(comando_manual)
                if exito:
                    st.success(f"Comando '{comando_manual}' ejecutado.")
                else:
                    st.error("Error en la comunicación.")
        else:
            st.warning("Escribe un comando o verifica la conexión.")

with col_monitor:
    st.header("📊 Estado y Herramientas")
    if st.button("🏠 Realizar HOMING"):
        if robot:
            robot.realizar_homing()
            st.success("Posición 0,0,0 establecida.")
    
    if st.button("✂️ Probar Pinza"):
        if robot:
            robot.cortar()
            st.info("Ciclo de corte ejecutado.")