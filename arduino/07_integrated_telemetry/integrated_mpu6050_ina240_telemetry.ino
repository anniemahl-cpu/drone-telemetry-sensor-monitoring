#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <math.h>

Adafruit_MPU6050 mpu;

const int ina240Pin = 34;

void setup() {
  Serial.begin(115200);
  delay(1000);

  // ESP32 ADC setting
  analogReadResolution(12); // 0-4095

  // I2C for MPU6050
  Wire.begin(21, 22); // SDA = GPIO21, SCL = GPIO22

  if (!mpu.begin()) {
    Serial.println("MPU6050 not found");

    while (1) {
      delay(10);
    }
  }

  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  Serial.println("Integrated telemetry system ready");
  Serial.println("time_ms,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,accel_magnitude,ina240_adc,ina240_out_voltage");
}

void loop() {
  sensors_event_t accel, gyro, temp;
  mpu.getEvent(&accel, &gyro, &temp);

  float ax = accel.acceleration.x;
  float ay = accel.acceleration.y;
  float az = accel.acceleration.z;

  float gx = gyro.gyro.x;
  float gy = gyro.gyro.y;
  float gz = gyro.gyro.z;

  float accelMagnitude = sqrt(ax * ax + ay * ay + az * az);

  int inaAdc = analogRead(ina240Pin);
  float inaVoltage = inaAdc * 3.3 / 4095.0;

  Serial.print(millis());
  Serial.print(",");

  Serial.print(ax, 3);
  Serial.print(",");
  Serial.print(ay, 3);
  Serial.print(",");
  Serial.print(az, 3);
  Serial.print(",");

  Serial.print(gx, 3);
  Serial.print(",");
  Serial.print(gy, 3);
  Serial.print(",");
  Serial.print(gz, 3);
  Serial.print(",");

  Serial.print(accelMagnitude, 3);
  Serial.print(",");
  Serial.print(inaAdc);
  Serial.print(",");
  Serial.println(inaVoltage, 3);

  delay(500);
}
