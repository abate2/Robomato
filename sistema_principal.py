import cv2
from ultralytics import YOLO
import os
import time
# Importamos tus funciones de conexión
from conexion_firebase import conectar_firebase, enviar_reporte

#Variables decada cuanto se enviara un reporte  
MINUTOS_ENTRE_REPORTES = 10
SEGUNDOS_ENTRE_REPORTES = MINUTOS_ENTRE_REPORTES * 60

# 1. Configuración Inicial
modelo_path = os.path.join('runs','train_definitivo', 'weights', 'best.pt')
model = YOLO(modelo_path)

# Conectamos a Firebase usando tu función
ref_db = conectar_firebase()

# 2. Variables para el conteo inteligente (Tracking)
# Usamos sets para guardar IDs únicos y que no se repitan
ids_maduros_contados = set()
ids_verdes_contados = set()

# 3. Iniciar Cámara
cap = cv2.VideoCapture(0)
print("Sincronizando con Firebase y activando IA...")

#Guarda el tiempo exacto en que se ejecuta la línea dentro de la variable en segundos desde la época (1 de enero de 1970).
utl_sincronizacion = time.time() # Para no saturar Firebase, enviaremos datos cada 10 segundos

while True:
    ret, frame = cap.read()
    if not ret: break

    # 4. IA con Tracking (persist=True mantiene el ID del tomate en movimiento)
    #🧩 4. conf=0.7 El nivel mínimo de confianza (70%).
    results = model.track(frame, persist=True, conf=0.7, tracker="bytetrack.yaml")

    # Simulación de sensores (Cámbialos manualmente para probar)
    temp_simulada = 27  # Simulamos un día caluroso
    humedad_simulada = 46  # Simulamos suelo seco si se baja de 45 la bomba se activara
    # Lógica de decisión
    estado_bomba = "ON" if humedad_simulada < 45 else "OFF"
    estado_ventilador = "ON" if temp_simulada > 28 else "OFF" 

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

    # 5. Dibujar resultados en pantalla
    annotated_frame =results[0].plot()

    # Texto informativo en la imagen
    cv2.putText(annotated_frame, f"Maduros: {len(ids_maduros_contados)}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(annotated_frame, f"Verdes: {len(ids_verdes_contados)}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Texto informativo en la imagen bomba
    color_bomba = (255, 0, 0) if estado_bomba == "ON" else (100, 100, 100) # Azul si está ON
    cv2.putText(annotated_frame, f"BOMBA: {estado_bomba}", (20,150), cv2.FONT_HERSHEY_SIMPLEX, 1, color_bomba,2)
    # Aviso de Ventilador
    color_vent = (0, 165, 255) if estado_ventilador == "ON" else (100, 100, 100) # # Naranja si está ON
    cv2.putText(annotated_frame, f"VENTILADOR: {estado_ventilador}", (20, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, color_vent, 2)

    cv2.imshow('Control de Cosecha Inteligente', annotated_frame)
  
    # 6. Sincronización Automática con Firebase cada 10 segundos
    if time.time() - utl_sincronizacion > SEGUNDOS_ENTRE_REPORTES: 
        print(f"Enviando reporte... Maduros totales: {len(ids_maduros_contados)}")
        enviar_reporte(ref_db, len(ids_maduros_contados), len(ids_verdes_contados), temp_simulada, humedad_simulada, estado_bomba, estado_ventilador)
        utl_sincronizacion = time.time()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()#Se libera la camara para que sea usada con otros programas
cv2.destroyAllWindows()


"""4. tracker="bytetrack.yaml"
🟢 ByteTrack es un algoritmo de tracking muy bueno para tiempo real.
Se encarga de:

-Asignar IDs a cada objeto
-Mantener esos IDs aunque el objeto se mueva
-Reidentificar objetos que salen y vuelven
-Suavizar errores en detección
"""