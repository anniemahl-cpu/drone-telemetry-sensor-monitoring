# Wiring Overview

## MPU6050 to ESP32

| MPU6050 | ESP32 |
|---|---|
| VCC | 3V3 |
| GND | GND |
| SDA | GPIO21 |
| SCL | GPIO22 |

## INA240 to ESP32

| INA240 | ESP32 |
|---|---|
| VCC | 3V3 |
| GND | GND |
| OUT | GPIO34 |

## LED Load Test Concept

The LED load circuit was used only as a safe low-current test load:

```text
Battery + -> INA240 +IN -> INA240 -IN -> resistor -> LED -> Battery -
```

The external battery circuit was not connected directly to ESP32 power pins.
