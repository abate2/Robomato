import cv2
from ultralytics import YOLO
import os
import time

# 1. Cargamos tu modelo definitivo
modelo_path = os.path.join('runs','train_definitivo', 'weights', 'best.pt') 

# 7. os.path.exists() verifica si el archivo está realmente ahí.
if not os.path.exists(modelo_path):
    print(f"❌ ERROR: No encuentro el modelo en: {modelo_path} ")
    exit()

# Carga tu modelo YOLO entrenado por ti usando el archivo .pt que se encuentra en la ruta especificada
model = YOLO(modelo_path)

# 2. Iniciamos la cámara (0 es la cámara por defecto de tu laptop/PC)Si tuvieras una webcam USB, normalmente sería 1.
print("Iniciando cámara...Por favor, espera un momento.")
cap = cv2.VideoCapture(0)

# Pausa de 2 segundos para que la cámara "despierte"
time.sleep(2) 

if not cap.isOpened():
    print("❌ ERROR: No se pudo abrir la cámara. Verifica si otra app la está usando.")
    exit()

print("✅ Cámara lista. Presiona 'q' para salir.")


while True:
    #9. Capturar cuadro por cuadro
    ret, frame = cap.read()
    if not ret:
        print("❌ Error al recibir imagen de la cámara. Reintentando...")
        continue

    # 3. La IA hace la predicción en tiempo real
    # stream=True ayuda a que el video sea más fluido
    results = model.predict(frame, stream=True, conf=0.8)

    #4. Dibujar los resultados  en el video 
    # Si no hay detecciones, mostramos el frame limpio
    annotated_frame = frame  # Inicializamos con el frame original
    for r in results:
        annotated_frame = r.plot()

    #5
    cv2.imshow('Sistema de Monitoreo de Tomates - IA', annotated_frame)

    #6 Salir con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
        
#Limpiar todo al salir
cap.release()
cv2.destroyAllWindows()
print("Programa cerrado correctamente.")

"""3# Perfecto, results es un objeto muy importante en YOLO y entenderlo te permite:
-obtener coordenadas
-saber qué clase detectó
-Saber qué confianza tiene
-acceder a la imagen con cuadros
-procesar cada detección de forma avanzada
✔ annotated_frame = el fotograma original + las anotaciones hechas por la IA

5# Por ejemplo, YOLO o tu propio código puede dibujar sobre la imagen:

-Cuadros de detección (bounding boxes)
-Etiquetas (tomate_maduro, tomate_verde)
-Porcentajes de confianza
-Colores
-Líneas o puntos

✔ 3. ord('q')

6#
1. cv2.waitKey(1)

Espera 1 milisegundo para ver si se presionó una tecla.
Si se presiona una, devuelve el código de esa tecla.
Si no se presiona nada, devuelve -1.

ord() convierte una letra a su código ASCII.Ejemplo ord('q') = 113
& 0xFF = Esto hace un AND binario para quedarse solo con los últimos 8 bits del código de la tecla .

9. Leer la imagen de la cámara
ret, frame = cap.read()
ret = True/False (si se leyó bien)
frame = imagen capturada

11. Hacer predicción con YOLO
results = model.predict(frame, stream=True, conf=0.4)
-Pasa el frame a YOLO para detección.
-stream=True → más rápido para video.
- conf=0.4 → solo muestra detecciones ≥ 40% confianza.
"""