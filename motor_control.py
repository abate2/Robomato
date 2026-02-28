# Aqui se  tiene la logica de los motores

import time 

class MotorController:
    def __init__(self):
        #Configuración de  ines (Ejemplo para Raspberry Pi / GPIO)
        self.STEPS_X_MM = 80# Pasos necesarios para mover 1mm en X
        self.STEPS_Y_MM = 80# Pasos necesarios para mover 1mm en Y
        self.STEPS_Z_MM = 100 


        # Límites físicos (mm)
        self.LIMIT_X = 4000
        self.LIMIT_Y  = 2500
        self.pos_x, self.pos_y, self.pos_z = 0, 0, 0

    def mover_a_centro(self, error_x, error_y):
        """
        Mueve los motores proporcionalmente al error detectado por YOLO.
        error_x/y: Distancia en píxeles desde el centro de la imagen.
        """

        kp = 0.5 # Constante de proporcionalidad (ajustar en campo)

        if abs(error_x) > 20: # Zona muerta de 20px
            pasos_x = int(error_x * kp)
            self._enviar_pulsos("X", pasos_x)

        if abs(error_y) > 20:
            pasos_y = int(error_y * kp)
            self._enviar_pulsos("Y", pasos_y)

    def _enviar_pulsos(self, eje, pasos):
        # Aquí va la lógica hacia tu Driver (A4988 / TB6600)
        # print(f"Moviendo Eje {eje}: {pasos} pasos")
        pass

    def cortar(self):
            print(">>> [BRAZO] Extendiendo actuador Z...")
            time.sleep(0.5)
            print(">>> [TIJERA] Realizando corte...")
            time.sleep(1)
            print(">>> [BRAZO] Retrayendo actuador Z.")

    def regresar_a_inicio(self):
        print("Moviendo actuadores a Coordenada X=0, Y=0 (Punto de descarga)")
        self.pos_x = 0
        self.pos_y = 0
        time.sleep(2) # Simulación del tiempo de viaje congela  el sofware por un momento para darle  tiempo  a movimiento que se  ha ordenado previamente 


