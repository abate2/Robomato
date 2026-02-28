# este  archivo contiene la logica de control del robot, como la clase MotorController y funciones relacionadas con el movimiento y corte.
class RobomatoBrain:
    def __init__(self, motor_controller):
        # Recibe el controlador de motores que ya creaste
        self.robot = motor_controller

        #estados del ciclo de trabajo de Robomato V1
        self.ESTADO_BUSQUEDA = "buscando"
        self.ESTADO_APROXIMACION = "apuntando"
        self.ESTADO_CORTE = "cortando"
        self.ESTADO_DESCARGA = "descargando cosecha"

        self.estado_actual = self.ESTADO_BUSQUEDA # Estado inicial

    def procesar_detecciones(self, results, ancho_camara, alto_camara):
        """
        Toma las decisiones de movimiento basadas en lo que ve YOLO.
        """
        centro_x = ancho_camara // 2
        centro_y = alto_camara // 2

        if self.estado_actual == self.ESTADO_DESCARGA:
            # Prioridad: Regresar al inicio para soltar el tomate
            print("Estado: DESCARGA. Regresando a X=0, Y=0...")
            self.robot.regresar_a_inicio() # Implementa esta función para volver a la posición inicial
            # Una vez en el inicio (puedes añadir una validación aquí), volvemos a buscar
            self.estado_actual = self.ESTADO_BUSQUEDA
            return self.estado_actual

        # Si hay detecciones
        if results[0].boxes.id is not None:
            # Tomamos el primer tomate maduro detectado (clase 0)
            target = None
            for box in results[0].boxes:
                if int(box.cls[0]) == 0: # Clase 0 = Tomate Maduro
                    target = box
                    break

            if target is not None:  
                x_c, y_c, w, h = target.xywh[0] #.xywh	coordenadas en formato (x, y, ancho, alto)
                confianza = target.conf[0]
                error_x = x_c - centro_x
                error_y = y_c - centro_y

                if self.estado_actual == self.ESTADO_BUSQUEDA:
                    if confianza > 0.8: 
                        print("--> Tomate MADURO detectado. Cambiando a APROXIMACION")
                        self.estado_actual = self.ESTADO_APROXIMACION
                    else: 
                        self.robot._enviar_pulsos("X", 10) #Seguir buscando

                elif self.estado_actual == self.ESTADO_APROXIMACION:
                    self.robot.mover_a_centro(error_x, error_y)
                    if abs(error_x) < 20 and abs(error_y) < 20:
                        self.estado_actual = self.ESTADO_CORTE
            
                elif self.estado_actual == self.ESTADO_CORTE:
                    self.robot.cortar()
                    # Cambio solicitado: Un tomate por descarga
                    print("--> Tomate en mano. Cambiando a DESCARGA para proteger estructura.")
                    self.estado_actual = self.ESTADO_DESCARGA

                else:
                    # No hay maduros a la vista
                    if self.estado_actual == self.ESTADO_BUSQUEDA:
                        self.robot._enviar_pulsos("X", 5)

        else:
            # Si no ve nada, sigue buscando en el pasillo
            if self.estado_actual == self.ESTADO_BUSQUEDA:
                self.robot._enviar_pulsos("X", 5) #Seguir buscando

        return self.estado_actual
