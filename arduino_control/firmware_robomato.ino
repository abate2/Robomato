#include <AccelStepper.h>

// Conversión de mm a Pasos (Basado en tornillo T8 y poleas GT2)
const float STEPS_PER_MM_X = 80.0;  // Polea GT2 20 dientes
const float STEPS_PER_MM_Y = 80.0;  // Polea GT2 20 dientes
const float STEPS_PER_MM_Z = 400.0; // Tornillo T8 (8mm avance/vuelta)

// Definición de Pines RAMPS 1.6
#define X_STEP_PIN 54
#define X_DIR_PIN  55
#define X_ENABLE_PIN 38
#define X_MIN_PIN 3

#define Y_STEP_PIN 60
#define Y_DIR_PIN  61
#define Y_ENABLE_PIN 56
#define Y_MIN_PIN 14

#define Z_STEP_PIN 46
#define Z_DIR_PIN  48
#define Z_ENABLE_PIN 62
#define Z_MIN_PIN 18

// Configuración de Motores (1 = Driver A4988/TMC2209)
AccelStepper stepperX(1, X_STEP_PIN, X_DIR_PIN);
AccelStepper stepperY(1, Y_STEP_PIN, Y_DIR_PIN);
AccelStepper stepperZ(1, Z_STEP_PIN, Z_DIR_PIN);

void setup() {
  Serial.begin(115200); // Velocidad de comunicación con la Raspberry Pi

  // Configurar pines de habilitación y finales de carrera
  pinMode(X_ENABLE_PIN, OUTPUT);
  pinMode(Y_ENABLE_PIN, OUTPUT);
  pinMode(Z_ENABLE_PIN, OUTPUT);
  digitalWrite(X_ENABLE_PIN, LOW); // LOW habilita los drivers
  
  pinMode(X_MIN_PIN, INPUT_PULLUP);
  pinMode(Y_MIN_PIN, INPUT_PULLUP);
  pinMode(Z_MIN_PIN, INPUT_PULLUP);

  // Velocidades máximas (Pasos por segundo)
  stepperX.setMaxSpeed(2000);
  stepperX.setAcceleration(500);
  stepperY.setMaxSpeed(2000);
  stepperY.setAcceleration(500);
  stepperZ.setMaxSpeed(1000); // El eje Z es más lento por el tornillo T8
  stepperZ.setAcceleration(300);
}

void loop() {
  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');
    procesarComando(comando);
  }
  
  // Mover motores a su posición destino
  stepperX.run();
  stepperY.run();
  stepperZ.run();
}

void procesarComando(String cmd) {
  if (cmd == "G28") { // Comando de Homing (Calibración)
    realizarHoming();
  } 
  else if (cmd.startsWith("G0")) { // Movimiento lineal
    parsearMovimiento(cmd);
  }
}

void realizarHoming() {
  Serial.println("INICIANDO_HOMING");
  
  // Homing Z primero por seguridad (subir el actuador)
  while (digitalRead(Z_MIN_PIN) == HIGH) {
    stepperZ.setSpeed(-400); 
    stepperZ.runSpeed();
  }
  stepperZ.setCurrentPosition(0);
  
  // Homing X e Y
  // ... (Repetir lógica para X e Y)
  
  Serial.println("OK"); // Avisa a la Raspberry Pi que terminó
}

void parsearMovimiento(String cmd) {
  // Busca la posición de cada letra en la cadena de texto
  int xIdx = cmd.indexOf('X');
  int yIdx = cmd.indexOf('Y');
  int zIdx = cmd.indexOf('Z');

  // Si encuentra 'X', extrae el valor y lo convierte a pasos
  if (xIdx != -1) {
    float valX = cmd.substring(xIdx + 1).toFloat();
    stepperX.moveTo(valX * STEPS_PER_MM_X); 
  }
  
  // Si encuentra 'Y', extrae el valor y lo convierte a pasos
  if (yIdx != -1) {
    float valY = cmd.substring(yIdx + 1).toFloat();
    stepperY.moveTo(valY * STEPS_PER_MM_Y);
  }

  // Si encuentra 'Z', extrae el valor y lo convierte a pasos
  if (zIdx != -1) {
    float valZ = cmd.substring(zIdx + 1).toFloat();
    stepperZ.moveTo(valZ * STEPS_PER_MM_Z);
  }

  Serial.println("OK"); // Confirma a la Raspberry que ya procesó la orden
}
