const int currentSensorPin = 34;

void setup() {
  Serial.begin(115200);
  delay(1000);

  analogReadResolution(12); // ESP32 ADC: 0-4095

  Serial.println("INA240 analog output test");
  Serial.println("time_ms,adc_raw,out_voltage_V");
}

void loop() {
  int adcRaw = analogRead(currentSensorPin);

  float outVoltage = adcRaw * 3.3 / 4095.0;

  Serial.print(millis());
  Serial.print(",");
  Serial.print(adcRaw);
  Serial.print(",");
  Serial.println(outVoltage, 3);

  delay(500);
}
