import cv2 # 1. Librería para procesamiento de imágenes
import numpy as np # 2. Librería para manejar matrices (las imágenes son matrices de números)

def analizar_cultivo(ruta_imagen):
    imagen = cv2.imread(ruta_imagen)
    if imagen is None:
        return 0, 0, None, None, None # 3. Cargamos la imagen desde tu carpeta
    hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
    conteo_maduros = 0
    conteo_verdes = 0
    kernel = np.ones((5,5), np.uint8)

    # --- LÓGICA ROJOS ---
    rojo_bajo1, rojo_alto1 = np.array([0, 100, 100]), np.array([10, 255, 255])
    rojo_bajo2, rojo_alto2 = np.array([160, 100, 100]), np.array([180, 255 , 255])
    mask_roja = cv2.add(cv2.inRange(hsv, rojo_bajo1, rojo_alto1), cv2.inRange(hsv, rojo_bajo2, rojo_alto2))
    mask_roja = cv2.morphologyEx(cv2.morphologyEx(mask_roja, cv2.MORPH_OPEN, kernel), cv2.MORPH_CLOSE, kernel)

    contornos_rojos, _ = cv2.findContours(mask_roja, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in contornos_rojos:
        area = cv2.contourArea(c)
        if area > 400:
            perimetro = cv2.arcLength(c, True)
            circularidad = 4 * np.pi * area / (perimetro * perimetro)
            if circularidad > 0.7:
                conteo_maduros += 1
                ((x, y), radio) = cv2.minEnclosingCircle(c)
                cv2.circle(imagen, (int(x), int(y)), int(radio), (0, 0, 255), 2)
                cv2.putText(imagen, f"Maduro #{conteo_maduros}", (int(x), int(y)-10), 1, 1, (255, 255, 255), 2)

    # --- LÓGICA VERDES ---

    verde_bajo, verde_alto = np.array([35, 40, 40]), np.array([85, 255, 255])
    mask_verde = cv2.inRange(hsv, verde_bajo, verde_alto)
    mask_verde = cv2.morphologyEx(mask_verde, cv2.MORPH_OPEN, kernel)

    contornos_verdes, _ = cv2.findContours(mask_verde, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cv in contornos_verdes:
        area = cv2.contourArea(cv)
        if area > 600:
            perimetro = cv2.arcLength(cv, True)
            circularidad = 4 * np.pi * area / (perimetro * perimetro)
            if circularidad > 0.7:
                conteo_verdes += 1
                ((x, y), radio) = cv2.minEnclosingCircle(cv)
                cv2.circle(imagen, (int(x), int(y)), int(radio), (0, 255, 0), 2)
                cv2.putText(imagen, f"Inmaduro #{conteo_verdes}", (int(x), int(y)-10), 1, 1, (255, 255, 255), 2)

    # --- TABLA DE RESUMEN ---
    cv2.rectangle(imagen, (10, 10), (250, 100), (0, 0, 0), -1)
    cv2.putText(imagen, f"Maduros: {conteo_maduros}", (20, 40), 1, 1.2, (0, 255, 0), 2)
    cv2.putText(imagen, f"Inmaduros: {conteo_verdes}", (20, 70), 1, 1.2, (0, 255, 0), 2)

    return conteo_maduros, conteo_verdes, imagen, mask_roja, mask_verde
