# K10 MCP Server - Quick Start Guide

## ⚡ 5-Step Setup

### Step 1: Connect K10 to WiFi

**Via Thonny IDE** (recommended):
1. Connect K10 via USB
2. Open Thonny → select "MicroPython (ESP32)" in bottom right
3. In REPL window:

```python
from unihiker_k10 import wifi
wifi.connect(ssid='YOUR-WIFI-NAME', psd='YOUR-PASSWORD', timeout=50000)

# Wait (5-10 seconds)
import time
time.sleep(8)

# Check connection
if wifi.status():
    print("✅ Connected!")
    print("IP:", wifi.info())
else:
    print("❌ Failed - check SSID/password")
```

**Note the IP address!** (e.g., 192.168.1.100)

---

### Step 2: Install microdot

In Thonny REPL:

```python
# Try 1: mip (modern)
import mip
mip.install("github:miguelgrinberg/microdot/src/microdot")
```

If that doesn't work:

```python
# Try 2: upip (legacy)
import upip
upip.install('microdot')
```

**Verify:**
```python
import microdot
print("✅ Microdot works!")
```

If both fail → see "Manual Installation" at end of this file.

---

### Step 3: Upload Server Files

Via Thonny:

1. Open **k10_mcp_server_http.py**
2. "File" → "Save as" → "MicroPython device"
3. Save as: **main.py**

Optional (for auto-WiFi):
1. Edit **boot.py**:
   - Line 10: `WIFI_SSID = "YOUR-WIFI"`
   - Line 11: `WIFI_PASSWORD = "YOUR-PASSWORD"`
2. Upload to K10 as **boot.py**

---

### Step 4: Start K10

1. Restart K10 (unplug/replug USB or press reset)
2. Display shows:
   ```
   MCP v0.3
   HTTP Mode
   /mcp
   ```
3. After ~5 seconds, server runs on port 8080

**Test in terminal:**
```bash
curl http://192.168.1.100:8080/
```

Expected response:
```json
{"server":"k10-mcp-server","version":"0.3.0","transport":"streamable-http","status":"running"}
```

---

### Step 5: Configure Claude Desktop

Edit (or create):
- **macOS/Linux:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "k10": {
      "url": "http://192.168.1.100:8080/mcp",
      "transport": "http"
    }
  }
}
```

**Important:** Adjust IP address!

**Restart Claude Desktop.**

---

## ✅ Test with Claude

Try these commands:

```
Turn the left LED red
```

```
What's the current temperature?
```

```
Show "Hello K10" on the display
```

Claude should now control your hardware! 🎉

---

## 🐛 Troubleshooting

### Problem: "no module named 'microdot'"

**Solution: Manual Installation**

1. Download: https://github.com/miguelgrinberg/microdot/archive/refs/heads/main.zip
2. Extract → find folder `microdot-main/src/microdot/`
3. In Thonny:
   - "View" → "Files"
   - Right-click on K10 → "New directory" → Name: `lib`
   - In `lib` → "New directory" → Name: `microdot`
   - Copy all `.py` files from `src/microdot/` to K10's `/lib/microdot/`

Key files:
- `microdot.py`
- `microdot_asyncio.py` (if present)

**Test:**
```python
import microdot
print("✅ Microdot manually installed!")
```

### Problem: "WiFi connection failed"

- **2.4 GHz check:** K10 only supports 2.4 GHz, not 5 GHz
- **Hidden SSID?** K10 can't find hidden networks
- **WPA2:** Make sure router uses WPA2 (not only WPA3)
- **Special characters:** Avoid umlauts in SSID/password

### Problem: "Server not reachable"

```bash
# Ping test
ping 192.168.1.100

# Port test
nc -zv 192.168.1.100 8080

# Or in browser:
http://192.168.1.100:8080/
```

If nothing works:
1. K10 and PC in **same network**?
2. Firewall blocking port 8080?
3. K10 has correct IP? (check via display or REPL)

### Problem: Claude doesn't connect

1. **Check config syntax:**
   ```bash
   # macOS/Linux
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | python -m json.tool
   ```
   
   Should show no errors.

2. **Check Claude logs:**
   - macOS: `~/Library/Logs/Claude/`
   - Windows: `%APPDATA%\Claude\logs\`
   
   Search for errors with "k10" or "mcp"

3. **Restart:**
   - Close Claude Desktop completely
   - Restart K10
   - Start Claude Desktop

---

## 📊 Success Checklist

- [ ] K10 connected to WiFi
- [ ] IP address known
- [ ] microdot installed
- [ ] main.py on K10 (= k10_mcp_server_http.py)
- [ ] Server running (curl test successful)
- [ ] claude_desktop_config.json configured
- [ ] Claude Desktop restarted
- [ ] Test command works

---

## 🎓 Next Steps

**Add more tools:**
- Camera (take photos)
- Speaker (play tones)
- Accelerometer (detect motion)
- Button (process input)

**See examples in source code**

---

## 📞 Help

If you're stuck:

1. **Check logs:**
   - Thonny: "View" → "Shell" (shows errors)
   - K10 display shows error messages

2. **Run test script:**
   ```bash
   python test_k10_mcp.py 192.168.1.100 demo
   ```

3. **Check files:**
   ```python
   # In K10 REPL
   import os
   os.listdir('/')
   # Should show: main.py, boot.py, lib/
   
   os.listdir('/lib')
   # Should show: microdot/
   ```

---

**Good luck! 🚀**
