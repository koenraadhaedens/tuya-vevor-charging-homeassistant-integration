# EVSE Phase A Decoder for Home Assistant (Pyscript)

This project decodes the raw Base64 value of an EVSE (charging cable) sensor 
(`sensor.ss_eu15o_m2_phase_a`) into **voltage**, **current**, and **power** sensors 
in Home Assistant, using [Pyscript](https://hacs-pyscript.readthedocs.io).

---

## ⚡ Features
- Decodes the **phase A** Base64 stream into:
  - `sensor.evse_voltage` (in V)
  - `sensor.evse_current` (in A)
  - `sensor.evse_power` (in W)
- Works with payloads of 7, 8, or 9 bytes (device sends different lengths depending on state).
- Updates:
  - On every change of the raw `phase_a` sensor
  - Every 30 seconds (polling)
  - On demand via `pyscript.evse_force_decode` service

---

## 📂 Installation Steps

1. **Install Pyscript**  
   - Go to **HACS → Integrations → Explore & download repositories**
   - Search for **Pyscript** and install.
   - Restart Home Assistant.
   - Add Pyscript integration in **Settings → Devices & services**.

2. **Create the Pyscript folder**  
   In your HA config directory (usually `/config`), create a folder if it doesn’t exist:
   ```
   /config/pyscript/
   ```

3. **Add the script**  
   Create a new file:
   ```
   /config/pyscript/evse_phase_decode.py
   ```
   Paste in the code from `evse_phase_decode.py`.

   Make sure the `PHASE_SENSOR` constant matches your raw entity id:
   ```python
   PHASE_SENSOR = "sensor.ss_eu15o_m2_phase_a"
   ```

4. **Reload Pyscript**  
   - Go to **Settings → Devices & services**
   - Find **Pyscript** integration → click **Reload**  
   Or restart HA.

---

## ✅ Usage

- New sensors will appear:
  - `sensor.evse_voltage`
  - `sensor.evse_current`
  - `sensor.evse_power`

- You can view them in **Developer Tools → States** or use templates:
  ```jinja
  {{ states('sensor.evse_voltage') }}
  {{ states('sensor.evse_current') }}
  {{ states('sensor.evse_power') }}
  ```

- Force a decode manually via **Developer Tools → Actions**:
  - Add action → **Call service**
  - Select `pyscript.evse_force_decode`

---

## 🛠 Debugging

- Logs are visible in **Settings → System → Logs**
- Filter for `pyscript` to see decoder messages, e.g.:
  ```
  EVSE decode OK (len=7) → V=233.4 V, I=0.000 A, P≈0 W, raw=CR4AAAAAAA=
  ```

- If you don’t see updates:
  - Confirm `PHASE_SENSOR` is correct.
  - Reload Pyscript or restart HA.
  - Check logs for syntax errors.

---

## 🔄 Adjustments

- Change update interval:
  ```python
  @time_trigger("period(30s)")
  ```
  → change `30s` to `10s`, `1min`, etc.

- You can rename the output sensors by editing:
  ```python
  _pub("sensor.evse_voltage", ...)
  _pub("sensor.evse_current", ...)
  _pub("sensor.evse_power", ...)
  ```

---

## Example Result

When idle:
```
Voltage: 233.4 V
Current: 0.000 A
Power:   0 W
```

When charging:
```
Voltage: 231.8 V
Current: 7.123 A
Power:   1650 W
```

---
