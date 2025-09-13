from base64 import b64decode

# Raw Base64 entity from your device:
PHASE_SENSOR = "sensor.ss_eu15o_m2_phase_a"

def _pub(eid, value, attrs):
    state.set(eid, value, attrs)

def _attrs(name, unit, dclass):
    return {"friendly_name": name, "unit_of_measurement": unit, "device_class": dclass}

def _decode_and_publish(raw: str):
    if not raw or raw in ("unknown", "unavailable", ""):
        return
    try:
        b = b64decode(raw + "==")  # tolerate missing padding
    except Exception as e:
        log.error(f"EVSE decode: base64 error for '{raw}': {e}")
        return

    n = len(b)
    # Accept 7..9 bytes. If 9 bytes, treat the 9th as a checksum and ignore it.
    if n < 2:
        log.error(f"EVSE decode: too few bytes ({n})")
        return
    if n == 9:
        b = b[:8]
        n = 8

    # Voltage: first 2 bytes, big-endian, 0.1 V units
    v = ((b[0] << 8) | b[1]) / 10.0
    _pub("sensor.evse_voltage", round(v, 1), _attrs("EVSE Voltage", "V", "voltage"))

    # Current: next 3 bytes (0.001 A) if present
    i = 0.0
    if n >= 5:
        i_raw = ((b[2] << 16) | (b[3] << 8) | b[4])
        i = i_raw / 1000.0
        # sanity cap (ignore crazy frames)
        if i < 0 or i > 1000:
            i = 0.0
    _pub("sensor.evse_current", round(i, 3), _attrs("EVSE Current", "A", "current"))

    # Power: last 3 bytes (0.001 kW) if present → Watts
    p_w = 0
    if n >= 8:
        p_raw = ((b[5] << 16) | (b[6] << 8) | b[7])   # thousandths of kW
        # Convert thousandths of kW → W (1e-3 kW * 1000 = 1 W)
        p_w = int(round(p_raw))
        # sanity cap
        if p_w < 0 or p_w > 50000:
            p_w = 0
    _pub("sensor.evse_power", p_w, {
        "friendly_name": "EVSE Power",
        "unit_of_measurement": "W",
        "device_class": "power",
        "state_class": "measurement",
    })

    log.info(f"EVSE decode OK (len={n}) → V={v:.1f} V, I={i:.3f} A, P≈{p_w} W, raw={raw}")

@time_trigger("startup")
def init_and_try_once():
    _pub("sensor.evse_voltage", "unknown", _attrs("EVSE Voltage", "V", "voltage"))
    _pub("sensor.evse_current", "unknown", _attrs("EVSE Current", "A", "current"))
    _pub("sensor.evse_power", "unknown", {
        "friendly_name": "EVSE Power", "unit_of_measurement": "W",
        "device_class": "power", "state_class": "measurement",
    })
    _decode_and_publish(state.get(PHASE_SENSOR))

@state_trigger(f"{PHASE_SENSOR}")
def on_phase_update(value=None):
    _decode_and_publish(state.get(PHASE_SENSOR))

@service
def evse_force_decode():
    _decode_and_publish(state.get(PHASE_SENSOR))
