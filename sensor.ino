
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_ADXL345_U.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <math.h>

#define ONE_WIRE_PIN 4
#define CURRENT_PIN 34

const float ACS712_SENSITIVITY = 0.185;
const float VOLTAGE_DIVIDER_FACTOR = 1.5;

const int VIBRATION_SAMPLES = 100;
const int CURRENT_SAMPLES = 200;

Adafruit_ADXL345_Unified accelerometer = Adafruit_ADXL345_Unified(12345);
OneWire oneWire(ONE_WIRE_PIN);
DallasTemperature temperatureSensor(&oneWire);

float currentOffset = 0.0;

float calibrateCurrent() {
    long total = 0;

    for (int i = 0; i < 500; i++) {
        total += analogReadMilliVolts(CURRENT_PIN);
        delay(2);
    }

    return (total / 500.0) / 1000.0 * VOLTAGE_DIVIDER_FACTOR;
}

float readVibrationRMS() {
    float sumSquares = 0.0;
    sensors_event_t event;

    for (int i = 0; i < VIBRATION_SAMPLES; i++) {
        accelerometer.getEvent(&event);

        float magnitude = sqrt(
            event.acceleration.x * event.acceleration.x +
            event.acceleration.y * event.acceleration.y +
            event.acceleration.z * event.acceleration.z
        );

        float dynamicAcceleration = (magnitude - 9.80665) / 9.80665;

        sumSquares += dynamicAcceleration * dynamicAcceleration;

        delay(10);
    }

    return sqrt(sumSquares / VIBRATION_SAMPLES);
}

float readTemperature() {
    temperatureSensor.requestTemperatures();
    return temperatureSensor.getTempCByIndex(0);
}

float readCurrent() {
    long total = 0;

    for (int i = 0; i < CURRENT_SAMPLES; i++) {
        total += analogReadMilliVolts(CURRENT_PIN);
        delayMicroseconds(500);
    }

    float measuredVoltage = (total / (float)CURRENT_SAMPLES) / 1000.0;
    measuredVoltage *= VOLTAGE_DIVIDER_FACTOR;

    return abs(measuredVoltage - currentOffset) / ACS712_SENSITIVITY;
}

void setup() {
    Serial.begin(115200);

    analogReadResolution(12);
    analogSetPinAttenuation(CURRENT_PIN, ADC_11db);

    Wire.begin(21, 22);

    if (!accelerometer.begin()) {
        while (true) {
            delay(1000);
        }
    }

    accelerometer.setRange(ADXL345_RANGE_16_G);

    temperatureSensor.begin();

    currentOffset = calibrateCurrent();

    Serial.println("vibration_rms,temperature,current");
}

void loop() {
    float vibration = readVibrationRMS();
    float temperature = readTemperature();
    float current = readCurrent();

    if (temperature == DEVICE_DISCONNECTED_C) {
        Serial.println("SENSOR_ERROR");
        delay(1000);
        return;
    }

    Serial.print(vibration, 4);
    Serial.print(",");
    Serial.print(temperature, 2);
    Serial.print(",");
    Serial.println(current, 3);

    delay(1000);
}
