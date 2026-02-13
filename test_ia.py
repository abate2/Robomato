from ultralytics import YOLO
import cv2
import os 

# 1. Cargamos el modelo el mismo que se movio desde  el one drive de tu pc local
modelo_path = os.path.join('runs', 'train_definitivo', 'weights', 'best.pt')
model = YOLO(modelo_path)

# 2. Ruta de una imagen para probar (asegúrate de que este archivo exista)
ruta_img = os.path.join('datasets', 'tomates', 'images', 'unriped tomato_292.png')

# 3. Realizar la detección
print("La IA está pensando...")
results = model(ruta_img)

# 4. Mostrar los resultados
for r in results: 
    img_con_cuadros = r.plot()
    cv2.imshow('Prueba de IA - Resultado Final', img_con_cuadros)
    print("¡Listo! Si ves cuadros sobre los tomates, la IA es un éxito.")
    print("Presiona cualquier tecla sobre la imagen para cerrar.")
    cv2.waitKey(0)

cv2.destroyAllWindows()
