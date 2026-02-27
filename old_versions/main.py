import config
import procesamiento_imagen as vision
import conexion_firebase as nube 
import cv2

def iniciar_monitoreo():
    print("Iniciando analisis...")

    # 1. Conectar a Firebase
    referencia_db = nube.conectar_firebase()

    #2. Procesar la imagen
    m, v, img_final, m_roja, m_verde = vision.analizar_cultivo(config.RUTA_IMAGEN)

    if img_final is not None:
        # 3. Mostrar resultados visuales
        cv2.imshow('Filtros de verdes', m_verde)
        cv2.imshow('Filtros de rojos', m_roja)
        cv2.imshow('Deteccion de madurez', img_final)

        print(f"Conteo final: {m} maduros y {v} inmaduros.")
        print("Presiona cualquier tecla en la imagen para enviar a la nube y cerrar.")

        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # 4. Enviar a la nube (solo ocurre después de cerrar las ventanas)
        nube.enviar_reporte(referencia_db, m, v)
    else:
        print("Error: No se pudo cargar la imagen. Revisa la ruta en config.py")


if __name__ == "__main__":
    iniciar_monitoreo()
        

