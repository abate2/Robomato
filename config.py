import os 

# 39 Configuración de Firebase
DATABASE_URL = 'https://proyecto-robomato-default-rtdb.firebaseio.com/'
CREDENTIALS_JASON = 'claves.json'

# 43 Configuración de Imagen
# Esto genera la ruta automática sin importar en qué carpeta estés
RUTA_IMAGEN =  os.path.join(os.path.dirname(__file__), 'imagenes','Riped tomato_35.jpeg')