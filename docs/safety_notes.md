# Safety Notes

This prototype was tested with low-voltage components only.

## Safety Decisions

- No real drone battery was used.
- No motor or propeller was connected.
- Testing was performed with an AA battery holder, LED, and resistor.
- When a wire heated up during an early breadboard test, the battery was disconnected immediately and the circuit was rebuilt.

## Rules for Future Testing

- Do not connect a LiPo drone battery until the circuit is fully reviewed.
- Do not connect propellers during electronics testing.
- Do not connect external battery voltage directly to ESP32 3V3, 5V, or GPIO pins.
- Always use a resistor with an LED load.
- Disconnect power immediately if any wire, battery, or component becomes hot.
