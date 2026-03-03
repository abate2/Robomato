# Aqui se  tiene la logica de los motores
import serial
import time 
import platform # Nueva librería para detectar el sistema operativo

class MotorController:
    def __init__(self):
        # Detectar el puerto según el sistema operativo
        sistema = platform.system()
        if sistema == "Windows":
            puerto = "COM3"  # Cambia el 3 por el número que veas en el Administrador de Dispositivos
        else:
            puerto = "/dev/ttyACM0" # Ruta estándar para Raspberry Pi
        # Intentar conectar con el Arduino
        try:
            self.ser = serial.Serial(puerto, 115200, timeout=2)
            time.sleep(2) # Espera a que el Arduino se reinicie tras conectar si no se  da  tiempo no tomara  las  ordenes
            print(">>> [CONEXIÓN] Arduino Mega detectado y vinculado.")
        except Exception as e:
            print(f"!!! [ERROR] No se pudo conectar con el Arduino: {e}")
            self.ser = None # El sistema sabrá que no hay hardware

        #Configuración de  ines (Ejemplo para Raspberry Pi / GPIO)
        self.STEPS_X_MM = 80# Pasos necesarios para mover 1mm en X
        self.STEPS_Y_MM = 80# Pasos necesarios para mover 1mm en Y
        self.STEPS_Z_MM = 400# Pasos necesarios para mover 1mm en Z (Tornillo T8) 

        # Límites físicos (mm)
        self.LIMIT_X = 2000
        self.LIMIT_Y  = 1000
        self.LIMIT_Z = 800

        # Estados de los finales de carrera (False = Libre, True = Presionado)
        self.stop_x = False
        self.stop_y = False
        self.stop_z = False

        self.pos_x, self.pos_y, self.pos_z = 0, 0, 0

        # Definición de Filas (Eje X)
        self.FILAS_X = [250, 750, 1250, 1750]

    def realizar_homing(self):
        """Envía al Arduino a buscar los 3 finales de carrera."""
        print(">>> [SISTEMA] Iniciando Homing General en el Punto Cero...")
        self._enviar_comando("G28") # Comando que activa la lógica del Arduino
        
        # Esperamos confirmación del Arduino
        self.pos_x, self.pos_y, self.pos_z = 0, 0, 0
        print(">>> [SISTEMA] Robot calibrado y listo en Fila 1.")


    def escanear_vertical(self):
        """Mueve el Eje Z usando la precisión del tornillo T8."""
        if self.pos_z == 0:
            print(f">>> [Z] Bajando {self.LIMIT_Z}mm para monitoreo...")
            self._enviar_comando(f"G0 Z{self.LIMIT_Z}")
            self.pos_z = self.LIMIT_Z
        else:
            print(">>> [Z] Subiendo a posición de seguridad...")
            self._enviar_comando("G0 Z0")
            self.pos_z = 0

    def mover_a_fila(self, num_fila):
        target_x = self.FILAS_X[num_fila - 1]
        print(f">>> [X] Moviendo a Fila {num_fila}")
        self._enviar_comando(f"G0 X{target_x}")
        self.pos_x = target_x

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

    def cortar(self):
            print(">>> [BRAZO] Extendiendo actuador Z...")
            time.sleep(0.5)
            print(">>> [TIJERA] Realizando corte...")
            time.sleep(1)
            print(">>> [BRAZO] Retrayendo actuador Z.")

    def descargar_en_lateral(self):
        print(">>> [Y] Llevando tomate a zona de descarga...")
        self._enviar_comando("G0 Y0") # Vuelve al inicio del riel Y para soltar
        self.pos_y = 0
        # Baja el brazo si es necesario para la canasta
        self.cortar()
        
    def regresar_a_inicio(self):
        print("Moviendo actuadores a Coordenada X=0, Y=0 (Punto de descarga)")
        self.pos_x = 0
        self.pos_y = 0
        time.sleep(2) # Simulación del tiempo de viaje congela el sofware por un momento para darle  tiempo  a movimiento que se ha ordenado previamente         

    def _enviar_comando(self, cmd):
        """Envía comandos con verificación de errores."""
        if self.ser is None:
            print(f"[MODO SIMULACIÓN] Comando omitido: {cmd}")
            return

        try:
            self.ser.write(f"{cmd}\n".encode())
            # Espera el "OK" del Arduino para confirmar que terminó
            respuesta = self.ser.readline().decode().strip()
            if respuesta == "OK":
                return True
        except Exception as e:
            print(f"!!! [CRÍTICO] Error de comunicación durante el comando {cmd}: {e}")
            return False


    def _enviar_pulsos(self, eje, pasos):
        # Bloqueo de seguridad: No mover si el sensor de ese eje está activo en dirección negativa
        if pasos < 0 and getattr(self, f"stop_{eje.lower()}"):
            print(f"!!! [ALERTA] Final de carrera {eje} activo. Movimiento bloqueado.")
            return
        # Aquí iría el comando serial hacia el Arduino Mega
        # self.serial_arduino.write(f"MOVE {eje} {pasos}\n".encode()) 
        pass





