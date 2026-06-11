# Project Summary

## Drone Telemetry and Sensor Monitoring Prototype

### Motivation

This project was inspired by a drone competition in Singapore. The drone had to fly inside a net-covered arena, and the pilot position was far from the take-off point. This made it difficult to observe the drone’s position and real-time flight state. The drone also ran out of battery unexpectedly, which made me think about how telemetry could help pilots monitor system status when direct visibility is limited.

### Aim

The aim was to build a low-cost ESP32-based telemetry prototype that could collect motion data and analog sensor-output data in one CSV stream. The project focuses on building and testing a first working MVP rather than producing a finished commercial drone system.

### Hardware and Software

- ESP32-WROOM-32
- MPU6050 accelerometer and gyroscope module
- INA240 analog current sensor
- Breadboard, jumper wires, LED, resistor, and 4×AA battery holder
- Arduino IDE and Serial Monitor
- Excel for data analysis and graphing

### Method

The project was developed in stages. I first confirmed ESP32 serial communication, then tested I2C scanning and MPU6050 data output. After that, I tested INA240 analog output through ESP32 GPIO34. I then built a low-voltage LED load circuit and debugged an initial short-circuit issue. Finally, I combined MPU6050 motion sensing and INA240 analog-output monitoring into one integrated ESP32 telemetry program.

The final data stream included:

```csv
time_ms,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,accel_magnitude,ina240_adc,ina240_out_voltage
```

### Results

The integrated 60-second telemetry test showed that the MPU6050 could distinguish stationary and movement phases. During stationary periods, acceleration magnitude stayed close to 9.5 m s^-2. During movement, it fluctuated from approximately 5.1 to 15.6 m s^-2.

The INA240 output voltage stayed between approximately 1.508 V and 1.530 V, showing stable analog signal acquisition by the ESP32 ADC while the IMU was also being read.

### Engineering Learning

This project helped me understand embedded-system development as an iterative engineering process. I had to test individual modules, identify wiring and display issues, debug a short circuit, collect data, and then integrate the modules into one system. The project strengthened my interest in Electrical and Electronic Engineering because it combined circuits, sensors, programming, data acquisition, and real-world troubleshooting.

### Limitations

The INA240 was not calibrated using a known current load, so the output cannot yet be converted into accurate current values. The system was also tested using a safe LED load instead of a real drone battery. Movement was generated manually, so the motion test was not perfectly repeatable.

### Future Work

Future work will focus on INA240 calibration, battery voltage monitoring, warning logic, wireless telemetry, and a real-time dashboard. A later version could be tested on a safe drone platform without propellers.
