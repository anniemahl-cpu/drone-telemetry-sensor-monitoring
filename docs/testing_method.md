# Testing Method

## Stage 1: ESP32 Serial Test
Confirmed that code could be uploaded and Serial Monitor could print data.

## Stage 2: I2C Scanner
Used the I2C scanner to confirm sensor addresses.

- MPU6050 detected at `0x68`
- OLED detected at `0x3C`, but display output failed and was postponed

## Stage 3: MPU6050 CSV Output
Recorded acceleration and gyroscope readings, then calculated acceleration magnitude.

## Stage 4: INA240 Analog Output
Read INA240 OUT voltage through ESP32 GPIO34.

## Stage 5: LED Load Circuit
Used an LED and resistor as a low-current load. An initial short-circuit issue was detected and corrected.

## Stage 6: Integrated Telemetry Test
Combined MPU6050 and INA240 in one program and collected a 60-second integrated telemetry dataset.
