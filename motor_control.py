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
        self.LIMIT_Z = 550
        self.OFFSET_CAMARA_PINZA_Z = 50 # mm (Ajustar según montaje físico)

        # Estados de los finales de carrera (False = Libre, True = Presionado)
        self.stop_x = False
        self.stop_y = False
        self.stop_z = False

        self.pos_x, self.pos_y, self.pos_z = 0, 0, 0

        # Índice para controlar la fila actual en el ciclo de trabajo
        self.fila_actual_index = 0 

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
        # Actualiza el índice (0, 1, 2 o 3) basándose en la fila (1, 2, 3 o 4)
        self.fila_actual_index = num_fila - 1
        target_x = self.FILAS_X[self.fila_actual_index]
        print(f">>> [X] Moviendo a Fila {num_fila} (Carril central: {target_x}mm)")
        self._enviar_comando(f"G0 X{target_x}")
        self.pos_x = target_x

    def mover_a_centro(self, error_x, error_y):
        """
        Ajusta la posición usando X (horizontal) y Z (vertical) para centrar el tomate.
        """
        kp = 0.5 # Ganancia proporcional para ajuste suave

        if abs(error_x) > 15:# Ajustamos a 15px para más precisión
            desplazamiento_x = int(error_x * kp)
            nueva_pos_x = self.pos_x + desplazamiento_x
            self._enviar_comando(f"G0 X{nueva_pos_x}")
            self.pos_x = nueva_pos_x

        # Usamos error_y (el de la imagen que otorga la camara) para ajustar el eje Z (Altura)
        # Importante saber que el error_y es el de la imagen, no tiene que ver con el eje Y mecanico
        if abs(error_y) > 15:
            desplazamiento_z = int(error_y * kp)
            nueva_pos_z = self.pos_z + desplazamiento_z
            # Seguridad: No exceder el límite de 550mm
            nueva_pos_z = max(0, min(nueva_pos_z, self.LIMIT_Z))
            self._enviar_comando(f"G0 Z{nueva_pos_z}")
            self.pos_z = nueva_pos_z


    def cortar(self):
        """Ejecuta el movimiento de compensación y activa el MG995."""
        # Subimos en Z para que la pinza ocupe el lugar donde la cámara vio el pedúnculo
        posicion_corte_z = self.pos_z - self.OFFSET_CAMARA_PINZA_Z
        print(f">>> [BRAZO] Subiendo a posición de corte: {posicion_corte_z}mm")
        self._enviar_comando(f"G0 Z{posicion_corte_z}")

        print(">>> [PINZA] Cerrando cuchillas (MG995)...")
        self._enviar_comando("M3") # Comando para activar el corte en el Arduino
        time.sleep(1)
        
        
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

    
    def descargar_en_lateral(self):
        """
        Lógica para recolección por gravedad y retorno al carril de escaneo.
        """
        print(">>> [SISTEMA] Corte realizado. Esperando caída por gravedad...")
        time.sleep(1.5) # Tiempo para que el tomate ruede por la manguera

        # NUEVO: Regresar al centro de la fila en X para retomar el zig-zag
        target_x = self.FILAS_X[self.fila_actual_index] 
        print(f">>> [X] Regresando al carril de la fila: {target_x}mm")      
        self._enviar_comando(f"G0 X{target_x}")
        self.pos_x = target_x # Mover a la posición de descarga lateral




