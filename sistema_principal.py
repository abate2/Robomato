import cv2
from ultralytics import YOLO
import os
import time
import config
# Importamos tus funciones de conexión
from conexion_firebase import conectar_firebase, enviar_reporte
from motor_control import MotorController
from robot_brain import RobomatoBrain

# Variables de sincronización y lectura
MINUTOS_ENTRE_LECTURA_SENSORES = 15 # Lectura climática periódica (cada 15 min)
SEGUNDOS_ENTRE_LECTURA_SENSORES = MINUTOS_ENTRE_LECTURA_SENSORES * 60

# Umbrales para automatización ambiental y de riego
UMBRAL_HUMEDAD_SUELO_RIEGO = 45 # Si la humedad de suelo baja del 45%, se activa la bomba
UMBRAL_TEMP_VENTILADOR = 28.0   # Si la temperatura ambiente supera 28°C, se activa ventilación

# 1. Configuración Inicial
print("⏳ Iniciando Robomato... Cargando modelo de Inteligencia Artificial...")
modelo_path = config.RUTA_MODELO
model = YOLO(modelo_path)

# Se instancia la clase RobomatoBrain con el controlador de motores (MotorController)
motor = MotorController()
cerebro = RobomatoBrain(motor)

# Conectamos a Firebase usando tu función
ref_db = conectar_firebase()

# 2. Variables para el conteo inteligente (Tracking) y Telemetría
ids_maduros_contados = set()
ids_verdes_contados = set()

# Variables de sensores (Lecturas iniciales)
temp_real = 25.0
hum_amb_real = 55.0
hum_suelo_real = 50
estado_bomba = "OFF"
estado_ventilador = "OFF"

# Control de reporte diario a Firebase
reporte_diario_enviado = False
utl_lectura_sensores = 0.0 # Se iniciará con lectura inmediata en el primer ciclo

# 3. Iniciar Cámara
cap = cv2.VideoCapture(0)
print("Sincronizando con sensores, Firebase y activando IA...")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    # 4. Lectura periódica de sensores reales desde el Arduino (cada 15 minutos o al inicio)
    if time.time() - utl_lectura_sensores >= SEGUNDOS_ENTRE_LECTURA_SENSORES or utl_lectura_sensores == 0.0:
        telemetria = motor.leer_sensores()
        temp_real = telemetria.get("temperatura", temp_real)
        hum_amb_real = telemetria.get("humedad_ambiental", hum_amb_real)
        hum_suelo_real = telemetria.get("humedad_suelo", hum_suelo_real)
        utl_lectura_sensores = time.time()

        # --- LÓGICA DE RIEGO AUTOMATIZADO ---
        if hum_suelo_real < UMBRAL_HUMEDAD_SUELO_RIEGO:
            if estado_bomba != "ON":
                motor.controlar_bomba(True)
                estado_bomba = "ON"
        else:
            if estado_bomba != "OFF":
                motor.controlar_bomba(False)
                estado_bomba = "OFF"

        # --- LÓGICA DE CONTROL DE VENTILACIÓN ---
        estado_ventilador = "ON" if temp_real > UMBRAL_TEMP_VENTILADOR else "OFF"

    # 5. IA con Tracking (persist=True mantiene el ID del tomate en movimiento)
    results = model.track(frame, persist=True, conf=0.7, tracker="bytetrack.yaml")

    # 6. CEREBRO ROBOT (Acción física)
    alto, ancho, _ = frame.shape
    estado_actual_robot = cerebro.procesar_detecciones(results, ancho, alto)

    if results[0].boxes.id is not None:
        ids = results[0].boxes.id.int().cpu().tolist()
        classes = results[0].boxes.cls.int().cpu().tolist()

        for id_obj, cls in zip(ids, classes):
            # Si la clase es 0 (maduro) y el ID no ha sido contado antes
            if cls == 0:
                ids_maduros_contados.add(id_obj)
            # Si la clase es 1 (verde) y el ID no ha sido contado antes
            elif cls == 1:
                ids_verdes_contados.add(id_obj)

    # 7. Dibujar resultados en pantalla (HUD)
    annotated_frame = results[0].plot()

    # Información de Conteo
    cv2.putText(annotated_frame, f"Maduros: {len(ids_maduros_contados)}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    cv2.putText(annotated_frame, f"Verdes: {len(ids_verdes_contados)}", (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    # Información de Sensores Reales
    color_suelo = (0, 0, 255) if hum_suelo_real < UMBRAL_HUMEDAD_SUELO_RIEGO else (0, 255, 0)
    cv2.putText(annotated_frame, f"Humedad Suelo: {hum_suelo_real}%", (20, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_suelo, 2)
    cv2.putText(annotated_frame, f"Ambiente: {temp_real:.1f}C | Hum: {hum_amb_real:.0f}%", (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # Estado de Actuadores (Bomba y Ventilador)
    color_bomba = (255, 0, 0) if estado_bomba == "ON" else (100, 100, 100) # Azul si está ON
    cv2.putText(annotated_frame, f"BOMBA: {estado_bomba}", (20, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color_bomba, 2)
    color_vent = (0, 165, 255) if estado_ventilador == "ON" else (100, 100, 100) # Naranja si está ON
    cv2.putText(annotated_frame, f"VENTILADOR: {estado_ventilador}", (20, 225), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color_vent, 2)

    # Estado del Ciclo del Robot
    cv2.putText(annotated_frame, f"ROBOT: {estado_actual_robot}", (20, 265), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

    cv2.imshow('Control de Cosecha Inteligente - Robomato V1', annotated_frame)
    
    # 8. Envío de Reporte Consolidado Único a Firebase al terminar la jornada
    if estado_actual_robot == "jornada_finalizada" and not reporte_diario_enviado:
        print("="*60)
        print("🚀 [FIN DE JORNADA] Enviando reporte diario consolidado a Firebase...")
        print(f"   -> Maduros recolectados: {len(ids_maduros_contados)} | Verdes detectados: {len(ids_verdes_contados)}")
        print(f"   -> Humedad suelo final: {hum_suelo_real}% | Temperatura ambiente: {temp_real}C")
        enviar_reporte(ref_db, len(ids_maduros_contados), len(ids_verdes_contados), temp_real, hum_suelo_real, estado_bomba, estado_ventilador, hum_ambiental=hum_amb_real)
        reporte_diario_enviado = True
        print("💤 Jornada concluida con éxito. Robot en modo reposo.")
        print("="*60)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        # Si se cierra manualmente y aún no se había enviado reporte pero hubo conteo
        if not reporte_diario_enviado and (len(ids_maduros_contados) + len(ids_verdes_contados) > 0):
            print("📤 Guardando reporte parcial antes de salir...")
            enviar_reporte(ref_db, len(ids_maduros_contados), len(ids_verdes_contados), temp_real, hum_suelo_real, estado_bomba, estado_ventilador, hum_ambiental=hum_amb_real)
        break

cap.release() # Se libera la cámara
cv2.destroyAllWindows()