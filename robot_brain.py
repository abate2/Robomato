# este  archivo contiene la logica de control del robot, como la clase MotorController y funciones relacionadas con el movimiento y corte.
class RobomatoBrain:
    def __init__(self, motor_controller):
        # Recibe el controlador de motores que ya creaste
        self.robot = motor_controller
        self.fila_actual = 1
        self.calibrado = False # Nueva bandera de seguridad

        #estados del ciclo de trabajo de Robomato V1
        self.ESTADO_BUSQUEDA = "buscando"
        self.ESTADO_APROXIMACION = "apuntando"
        self.ESTADO_CORTE = "cortando"
        self.ESTADO_DESCARGA = "descargando cosecha"
        self.estado_actual = self.ESTADO_BUSQUEDA # Estado inicial       

    def procesar_detecciones(self, results, ancho_camara, alto_camara):
        # 1. Seguridad: Homing obligatorio al inicio
        if not self.calibrado:
            self.robot.realizar_homing()
            self.calibrado = True

        # 2. Lógica de Navegación si NO hay detecciones
        if results[0].boxes.id is None:
            if self.estado_actual == self.ESTADO_BUSQUEDA:
                # Realiza barrido vertical (Eje Z) antes de avanzar
                self.robot.escanear_vertical()
                # Avanza un tramo en el pasillo (Eje Y)
                self.robot.pos_y += 150 # Avanza por el ancho del pasillo
                if self.robot.pos_y > self.robot.LIMIT_Y:
                    self.cambiar_de_fila()
            return self.estado_actual

        # 3. Lógica con Detecciones (YOLOv8)
        centro_x, centro_y = ancho_camara // 2, alto_camara // 2
        
        target = None
        for box in results[0].boxes:
            if int(box.cls[0]) == 0: # Clase 0 = Tomate Maduro
                target = box
                break

        if target:
            x_c, y_c, w, h = target.xywh[0]
            error_x = x_c - centro_x
            error_y = y_c - centro_y

            if self.estado_actual == self.ESTADO_BUSQUEDA:
                if target.conf[0] > 0.8:
                    self.estado_actual = self.ESTADO_APROXIMACION
                else:
                    # En lugar de enviar_pulsos, enviamos un comando de movimiento pequeño
                    print("--> [IA] Confianza baja, avanzando 10mm para mejor vista.")
                    self.robot._enviar_comando("G0 Y10") 
                    self.robot.pos_y += 10

            elif self.estado_actual == self.ESTADO_APROXIMACION:
                self.robot.mover_a_centro(error_x, error_y)
                if abs(error_x) < 20 and abs(error_y) < 20:
                    self.estado_actual = self.ESTADO_CORTE

            elif self.estado_actual == self.ESTADO_CORTE:
                self.robot.cortar()
                self.estado_actual = self.ESTADO_DESCARGA

            elif self.estado_actual == self.ESTADO_DESCARGA:
                self.robot.descargar_en_lateral()
                self.estado_actual = self.ESTADO_BUSQUEDA

        return self.estado_actual

    def cambiar_de_fila(self):
        print(">>> [SISTEMA] Fila terminada. Cambiando de surco...")
        self.fila_actual += 1
        if self.fila_actual <= 4:
            self.robot.mover_a_fila(self.fila_actual)
        else:
            print(">>> [SISTEMA] Cosecha finalizada en las 4 filas.")

