# BioAmp EXG Pill Hardware Setup Guide

## Components Required

### Per Headset
1. **Brain BioAmp Band (6 Channel)** - ₹667
2. **BioAmp EXG Pill (Assembled)** - ₹2,599
3. **Arduino Uno R3 Clone** - ₹350
4. **USB Cable** - ₹100
5. **9V Battery** (optional for portable) - ₹100

**Total: ₹3,816 per headset**

---

## Hardware Connections

### BioAmp EXG Pill → Arduino Uno

```
BioAmp Pin → Arduino Pin
├── VCC (Red)    → 5V
├── GND (Black)  → GND
└── OUT (Yellow) → A0 (Analog Input)
```

### Electrode Placement (10-20 System)

**For LEFT hand motor imagery:**
```
Signal:    C3 (Left Motor Cortex)
Reference: A1 (Left Mastoid - behind left ear)
Ground:    Fpz (Forehead center)
```

**For RIGHT hand motor imagery:**
```
Signal:    C4 (Right Motor Cortex)
Reference: A2 (Right Mastoid - behind right ear)
Ground:    Fpz (Forehead center)
```

---

## Step-by-Step Assembly

### 1. Prepare BioAmp Band

1. Attach snap electrodes to band at positions:
   - C3 (left of center, above ear)
   - C4 (right of center, above ear)
   - Fpz (forehead center)

2. Measure electrode positions using 10-20 system:
   - Nasion to Inion distance
   - Mark C3: 20% left of Cz
   - Mark C4: 20% right of Cz

### 2. Connect Electrodes to BioAmp

1. Use BioAmp Cable v3 (included):
   ```
   Red cable    → Signal electrode (C3 or C4)
   Black cable  → Reference electrode (A1 or A2)
   White cable  → Ground electrode (Fpz)
   ```

2. Apply electrode gel (optional but recommended)

### 3. Connect BioAmp to Arduino

1. Use jumper cables (included):
   ```
   BioAmp VCC → Arduino 5V (red wire)
   BioAmp GND → Arduino GND (black wire)
   BioAmp OUT → Arduino A0 (yellow wire)
   ```

2. Power Arduino via USB (laptop)

### 4. Upload Firmware

```bash
# Using Arduino IDE
1. Open arduino/bioamp_stream.ino
2. Select Board: Arduino Uno
3. Select Port: /dev/ttyUSB0 (or COM3 on Windows)
4. Click Upload

# Using arduino-cli
arduino-cli compile --fqbn arduino:avr:uno arduino/bioamp_stream.ino
arduino-cli upload -p /dev/ttyUSB0 --fqbn arduino:avr:uno arduino/bioamp_stream.ino
```

### 5. Test Connection

```bash
python scripts/1_test_bioamp.py
```

Expected output:
- Sampling rate: ~500 Hz
- Signal quality: <150 μV amplitude
- Visible alpha rhythm when eyes closed

---

## Troubleshooting

### No Signal / All Zeros
**Problem:** No data from BioAmp  
**Solutions:**
- Check Arduino power (LED should be on)
- Verify BioAmp OUT → Arduino A0 connection
- Check electrode contact (should be <50 kΩ impedance)
- Re-upload firmware

### High Noise (>200 μV)
**Problem:** Signal too noisy  
**Solutions:**
- Apply electrode gel
- Improve electrode contact
- Move away from power lines
- Use shielded cables
- Ground Arduino properly

### Low Sampling Rate (<400 Hz)
**Problem:** Dropped samples  
**Solutions:**
- Close other serial programs
- Use higher baud rate (115200)
- Check USB cable quality
- Try different USB port

### Electrode Impedance Too High
**Problem:** Poor contact  
**Solutions:**
- Clean skin with alcohol wipe
- Apply electrode gel
- Adjust band tightness
- Check electrode wear

---

## Maintenance

### Daily (Event Day)
- [ ] Check battery levels
- [ ] Clean electrodes with alcohol
- [ ] Verify all connections
- [ ] Test sampling rate

### After Each Session
- [ ] Wipe electrodes clean
- [ ] Wash BioAmp Band (hand wash)
- [ ] Check for worn electrodes
- [ ] Store in dry place

### Weekly
- [ ] Replace electrode gel
- [ ] Check cable connections
- [ ] Verify Arduino firmware
- [ ] Calibrate baseline

---

## Safety Notes

⚠️ **Important:**
- BioAmp is NOT a medical device
- For research/education only
- Do not use on people with pacemakers
- Keep away from water
- Use fresh batteries only
- Adult supervision required

---

## Performance Expectations

### With BioAmp EXG Pill (1-Channel)

| Metric | Expected | Achieved |
|--------|----------|----------|
| Sampling Rate | 500 Hz | __ Hz |
| Signal SNR | >3 dB | __ dB |
| Latency (p95) | <400 ms | __ ms |
| Accuracy (binary) | 60-65% | __ % |
| Electrode Impedance | <50 kΩ | __ kΩ |

---

## Cost Breakdown (5 Headsets)

| Item | Unit Price | Qty | Total |
|------|-----------|-----|-------|
| Brain BioAmp Band | ₹667 | 5 | ₹3,335 |
| BioAmp EXG Pill | ₹2,599 | 5 | ₹12,995 |
| Arduino Uno Clone | ₹350 | 5 | ₹1,750 |
| USB Cables | ₹100 | 5 | ₹500 |
| 9V Batteries | ₹100 | 5 | ₹500 |
| **TOTAL** | | | **₹19,080** |

**Per headset: ₹3,816**

---

## Upgrade Path

Want better performance? Consider:

1. **Multi-channel:** Add 2 more BioAmp Pills for C3+Cz+C4 (₹5,198 more)
2. **ADS1299:** Upgrade to 8-channel professional (₹6,167 total, saves money!)
3. **Better electrodes:** Gold-plated dry electrodes (₹2,000)
4. **Arduino Mega:** More channels (₹1,800)

**Recommendation:** If budget allows, go straight to ADS1299 setup (₹30,835 for 5 headsets) - better value!
