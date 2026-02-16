import firebase_admin
from firebase_admin import credentials, db
import datetime
import config

def conectar_firebase():
    if not firebase_admin._apps: # 43. Verifica si Firebase ya está inicializado para no inicializarlo varias veces y causar un error
        cred = credentials.Certificate(config.CREDENTIALS_JASON)
        firebase_admin.initialize_app(cred,{
            'databaseURL': config.DATABASE_URL # se importa del archivo config.py para mantener la seguridad de las claves fuera del código principal la url
        })
    # 44. Referencia a la "carpeta" donde guardaremos los datos
    return db.reference('monitoreo_cultivo')

#45. Función para enviar el reporte a Firebase
def enviar_reporte(referencia, maduros, verdes, temp, humedad, bomba, ventilador): 
    total = maduros + verdes
    if total > 0:
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
        referencia.push(nueva_lectura)
        print(f"🚀 Datos sincronizados. Bomba: {bomba}, Ventilador: {ventilador}")
        print("⚠️ No se detectaron tomates. No se envió reporte.")
