from ultralytics import YOLO

# 1. Cargamos el modelo base (Nano, el más rápido)
model = YOLO('yolov8n.pt')

## 2. ¡A entrenar! 
# epochs=20 significa que leerá el set de fotos 20 veces
# imgsz=640 es el tamaño estándar de imagen para YOLO
results = model.train(
    data='data.yaml', 
    epochs=20, 
    imgsz=640, 
    project='C:/Proyectos/Tomato_red_project/runs', # <--- ESTO FUERZA LA RUTA
    name='train_definitivo'
)


