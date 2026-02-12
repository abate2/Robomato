from ultralytics import YOLO

# Cargamos un modelo pre-entrenado de Google (detecta 80 cosas, incluyendo personas y frutas)
model = YOLO('yolov8n.pt') # 1. Carga el modelo YOLOv8 nano (el más pequeño y rápido)

# Probamos con tu imagen de prueba
results = model.predict(source='./imagenes/Riped tomato_35.jpeg', save=True) # 2. Analiza la imagen y guarda el resultado con las detecciones

print("¡YOLO está vivo! Revisa la carpeta 'runs/detect/predict' para ver el resultado.")
