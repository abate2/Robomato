import firebase_admin
from firebase_admin import credentials, db
import datetime
import config
import json
import os

#42. Función para conectar a Firebase

def conectar_firebase():
    try:    
        if not firebase_admin._apps: # 43. Verifica si Firebase ya está inicializado para no inicializarlo varias veces y causar un error
            cred = credentials.Certificate(config.CREDENTIALS_JASON)
            firebase_admin.initialize_app(cred,{
                'databaseURL': config.DATABASE_URL # se importa del archivo config.py para mantener la seguridad de las claves fuera del código principal la url
            })
        # 44. Referencia a la "carpeta" donde guardaremos los datos
        return db.reference('monitoreo_cultivo')
    except Exception as e:
        print(f"Error al conectar a Firebase: {e}")
        return None

#45. Función para enviar el reporte a Firebase
def enviar_reporte(referencia, maduros, verdes, temp, humedad, bomba, ventilador): 
    total = maduros + verdes
    if total <= 0:
        print("⚠️ No se detectaron tomates. No se envió reporte.")
        return
    
    nueva_lectura = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "maduros": maduros,
        "verdes": verdes,
        "porcentajes_madurez": int((maduros / total * 100)),
        "sensores_simulados": {
            "temperatura": temp, # Dato simulado 
            "humedad_suelo": humedad, # Dato simulado
            "estado_bomba": bomba, # Dato simulado
            "estado_ventilador": ventilador # Dato simulado
        }
    }
    # Intentar enviar a Firebase
    try:
        if referencia:
            # 1. Intentar subir datos pendientes primero
            subir_datos_pendientes(referencia)
            
            # 2. Subir la lectura actual
            referencia.push(nueva_lectura)
            print(f"🚀 Sincronización ONLINE exitosa. Bomba: {bomba}")
        else:
            raise Exception("Referencia a DB no disponible")
            
    except Exception:
        # 3. Si falla, guardar localmente (El Escudo)
        print("📡 ⚠️ Sin conexión. Guardando reporte en respaldo local...")
        guardar_localmente(nueva_lectura)

def guardar_localmente(datos):
    archivo = "backup_datos.json"
    respaldos = []
    
    if os.path.exists(archivo):
        with open(archivo, "r") as f:
            respaldos = json.load(f)
    
    respaldos.append(datos)
    
    with open(archivo, "w") as f:
        json.dump(respaldos, f, indent=4)

def subir_datos_pendientes(referencia):
    archivo = "backup_datos.json"
    if os.path.exists(archivo):
        print("📤 Detectados datos guardados localmente. Sincronizando...")
        with open(archivo, "r") as f:
            datos_pendientes = json.load(f)
        
        for dato in datos_pendientes:
            referencia.push(dato)
        
        os.remove(archivo) # Limpieza automática tras subir
        print("✅ Respaldo local sincronizado y limpiado.")


