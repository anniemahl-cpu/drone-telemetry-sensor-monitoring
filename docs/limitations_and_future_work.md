# Limitations and Future Work

## Limitations

- INA240 output was not calibrated against a known current.
- INA240 readings are treated as analog voltage monitoring, not precise current measurement.
- Manual movement means the motion profile is not perfectly repeatable.
- The prototype was tested with a safe low-voltage LED load, not a real drone battery.
- OLED display output was postponed after I2C detection succeeded but screen display failed.
- Telemetry output currently uses Serial Monitor rather than wireless transmission.

## Future Work

- Calibrate INA240 using known resistive loads.
- Add battery voltage measurement.
- Add low-battery warning logic.
- Add abnormal-motion warning logic.
- Add Wi-Fi or Bluetooth telemetry.
- Build a dashboard for real-time data display.
- Test on a safe drone platform without propellers.
