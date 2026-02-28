// Firmware simplificado para Arduino Mega + RAMPS 1.6
#include <AccelStepper.h>

// Pines RAMPS 1.6
#define X_STEP_PIN 54
#define X_DIR_PIN  55
#define X_STOP_PIN 3

#define Y_STEP_PIN 60
#define Y_DIR_PIN  61
#define Y_STOP_PIN 14

#define Z_STEP_PIN 46
#define Z_DIR_PIN  48
#define Z_STOP_PIN 18

AccelStepper stepperX(1, X_STEP_PIN, X_DIR_PIN);
AccelStepper stepperY(1, Y_STEP_PIN, Y_DIR_PIN);
AccelStepper stepperZ(1, Z_STEP_PIN, Z_DIR_PIN);

void setup() {
  Serial.begin(115200);
  
  // Configuración de límites y velocidad
  stepperX.setMaxSpeed(1000);
  stepperY.setMaxSpeed(1000);
  stepperZ.setMaxSpeed(800);
  
  pinMode(X_STOP_PIN, INPUT_PULLUP);
  pinMode(Y_STOP_PIN, INPUT_PULLUP);
  pinMode(Z_STOP_PIN, INPUT_PULLUP);
}

void loop() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    // Aquí el Arduino procesará comandos como "G0 X100 Y500 Z200"
    // enviando las señales a los drivers TMC2209
  }
}