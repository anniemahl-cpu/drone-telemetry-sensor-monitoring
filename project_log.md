# Engineering Development Log

## 6.3 — ESP32 and MPU6050 Initial Test

**Completed**

- Confirmed ESP32 serial upload and Serial Monitor output.
- Detected the MPU6050 at I2C address `0x68`.
- Successfully read acceleration and gyroscope values.
- Reformatted MPU6050 output as CSV data.
- Saved an initial stationary baseline dataset.

**Issue**

- OLED was detected at I2C address `0x3C`, but the display did not show output. This was recorded as a display-module issue and postponed so that the core telemetry system could continue.

## 6.7 — MPU6050 Baseline Graph

**Completed**

- Created the first graph for the MPU6050 stationary baseline test.
- The acceleration magnitude remained around `9.50–9.57 m s^-2`, close to the expected gravitational acceleration.

**Reflection**

This confirmed that the IMU could provide stable baseline motion-state data.

## 6.11 — INA240 Analog Output Test

**Completed**

- Connected INA240 `VCC` to ESP32 `3V3`.
- Connected INA240 `GND` to ESP32 `GND`.
- Connected INA240 `OUT` to ESP32 `GPIO34`.
- Read INA240 output using ESP32 ADC.

**Result**

- With no current passing through the sensing path, INA240 output remained around `1.52–1.54 V`.
- This was recorded as the zero-current / low-current baseline.

## 6.11 — LED Load Test and Circuit Debugging

**Issue**

- An early breadboard connection caused the battery-holder wire to heat up. This indicated a likely short circuit or incorrect connection.

**Action**

- The battery was immediately disconnected.
- The circuit was checked and rebuilt.
- The LED and resistor were connected correctly in series.

**Result**

- The LED load circuit worked after rebuilding.
- INA240 output during the LED load test stayed around `1.51–1.53 V`.
- The voltage variation was small because the LED-resistor load produced only a small current.

**Reflection**

This was one of the most important learning points in the project. It showed that hardware debugging requires careful checking of current paths, not just code.

## 6.11 — Integrated Telemetry Test

**Completed**

- Integrated MPU6050 and INA240 into one ESP32 program.
- MPU6050 was connected through I2C using `SDA = GPIO21` and `SCL = GPIO22`.
- INA240 OUT was connected to `GPIO34` as an analog input.
- The system output one CSV telemetry stream containing timestamp, acceleration, gyroscope readings, acceleration magnitude, INA240 ADC value, and INA240 output voltage.

**Result**

- The final integrated dataset covered about 60 seconds.
- Acceleration magnitude showed clear stationary and movement phases.
- The movement phase ranged from approximately `5.1–15.6 m s^-2`.
- INA240 output remained approximately between `1.508–1.530 V`.

**Significance**

This confirmed that the ESP32 could collect both motion-state data and analog current-sensor output at the same time.

## Current MVP Status

The MVP is complete. The system now demonstrates:

- IMU motion sensing
- analog sensor-output monitoring
- serial CSV telemetry output
- data analysis and visualization
- engineering debugging and reflection

Further work will focus on calibration, wireless telemetry, and dashboard/display improvements.
