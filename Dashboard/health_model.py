"""
Rule-Based Actuator Health Calculator
Output: Health percentage (0-100%)
"""

def calculate_health(
    current,
    voltage,
    vibration,
    baseline_current=5.0,
    baseline_voltage=220.0,
    baseline_vibration=0.5,
    current_trend=0.0,
    vibration_trend=0.0
):
    health = 100.0

    # Rule 1: Current increase penalty
    current_increase = max(0, current - baseline_current)
    health -= current_increase * 3.0

    # Rule 2: Voltage deviation penalty
    voltage_deviation = abs(voltage - baseline_voltage)
    health -= (voltage_deviation / baseline_voltage) * 20.0

    # Rule 3: Vibration increase penalty
    vibration_increase = max(0, vibration - baseline_vibration)
    health -= vibration_increase * 8.0

    # Rule 4: Trend penalties
    if current_trend > 0.05:
        health -= 5.0
    if vibration_trend > 0.02:
        health -= 5.0

    # Rule 5: Cross-sensor correlation
    current_severe = (current - baseline_current) > (0.2 * baseline_current)
    vibration_severe = (vibration - baseline_vibration) > (0.5 * baseline_vibration)
    if current_severe and vibration_severe:
        health -= 15.0

    # Rule 6: Power efficiency
    power = voltage * current
    expected_power = baseline_voltage * baseline_current
    if power > expected_power * 1.2:
        health -= 8.0

    # Clamp
    return max(0.0, min(100.0, health))
