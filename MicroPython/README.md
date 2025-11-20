# K10 MCP Server

**MCP Server directly on UNIHIKER K10** - Control hardware with Claude!

## 🎯 What is this?

A complete **Model Context Protocol (MCP) Server** running directly on the K10 board, enabling Claude to control hardware - no additional gateway computer needed!

```
Claude Desktop ←→ HTTP ←→ K10 (ESP32-S3)
                           ├─ RGB LEDs
                           ├─ Sensors (Temp/Humidity/Light)
                           ├─ 2.8" Display
                           └─ Camera + AI
```

## 📦 Files

| File | Purpose |
|------|---------|
| `k10_mcp_server_http.py` | **Main server v0.3.0** (→ upload as main.py) ⭐ |
| `boot.py` | Auto-WiFi connect (optional) |
| `test_k10_mcp.py` | Test client for PC |
| **`HTTP_VS_SSE.md`** | **Why HTTP is better than SSE** |
| `claude_desktop_config_HTTP.json` | Example config |

## ⚡ Quick Start (3 Steps)

### 1. Upload to K10
- Upload `k10_mcp_server_http.py` as `main.py`
- Edit and upload `boot.py` (set WiFi credentials)
- Restart K10

### 2. Configure Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "k10": {
      "url": "http://192.168.178.112:8080/mcp",
      "transport": "http"
    }
  }
}
```

Replace IP with your K10's IP address!

### 3. Restart Claude Desktop

Done! Try: "Turn the left LED red"

## 🛠️ What the Server Can Do

Claude can now:

| Tool | Example Command |
|------|-----------------|
| `set_rgb_led` | "Turn both LEDs blue" |
| `get_temperature` | "What's the temperature?" |
| `get_humidity` | "Check the humidity level" |
| `get_light_level` | "How bright is it?" |
| `display_text` | "Show 'Hello' on the screen" |
| `draw_circle` | "Draw a red circle" |
| `clear_display` | "Clear the display" |

**Example session:**
```
User: Turn the left LED green and show the temperature on the display

Claude: [calls set_rgb_led(0, 0, 255, 0)]
        [calls get_temperature()]
        [calls display_text("Temp: 23.5°C")]
        
        I've set the left LED to green and displayed the current 
        temperature (23.5°C) on the screen.
```

## 🚀 Quick Test (without Claude)

```bash
# Install
pip install requests

# Run demo
python test_k10_mcp.py 192.168.178.112 demo

# Result:
✅ Server is running
✅ Initialized successfully
✅ Found 14 tools
💡 Setting LED 0 to RGB(255, 0, 0)...
🌡️ Reading temperature...
[... more tests ...]
🌈 LED Rainbow Demo...
✅ All tests completed successfully!
```

## 📊 Technical Details

| Spec | Value |
|------|------|
| **Hardware** | UNIHIKER K10 (ESP32-S3) |
| **Protocol** | MCP JSON-RPC 2.0 |
| **Transport** | HTTP (Streamable HTTP) |
| **HTTP Server** | microdot (MicroPython) |
| **Port** | 8080 |
| **Latency** | ~100-300ms per tool call |
| **Language** | MicroPython |

## 🎨 Example Prompts

### Simple
```
Turn both LEDs red
Show "Hi" on the display
What's the humidity?
```

### Complex
```
Monitor the room: read all sensors and 
show the values on the display. If temperature is above 25°C, 
turn LEDs red, otherwise green.
```

```
Create a rainbow animation on the LEDs, then display the 
current temperature and light level.
```

## 🆚 Why HTTP instead of SSE?

**Short answer:** HTTP is much simpler and SSE is deprecated in MCP!

| Feature | SSE (deprecated) | HTTP (modern) |
|---------|------------------|---------------|
| **Endpoints** | 2 (/sse + /message) | 1 (/mcp) |
| **Complexity** | High | Low |
| **MicroPython** | ⚠️ Generator bug | ✅ Works perfectly |
| **Code** | ~600 lines | ~400 lines |
| **Status** | ⚠️ Deprecated | ✅ Recommended |

See [HTTP_VS_SSE.md](HTTP_VS_SSE.md) for details.

## 🔧 Extensions

The server is easily extensible:

**Add more tools:**
- 📷 Camera (take photos)
- 🔊 Speaker (play tones)
- 📐 Accelerometer (motion)
- 🤖 AI Models (Face Detection, QR)

See example in code comments.

## 📚 Documentation

| Document | Content |
|----------|---------|
| [HTTP_VS_SSE.md](HTTP_VS_SSE.md) | Why HTTP is better |
| [test_k10_mcp.py](test_k10_mcp.py) | Test tool |

## 🔐 Security

⚠️ **Important:** No authentication in default setup!

**For production:**
- Add API key authentication
- Use HTTPS via reverse proxy
- Implement rate limiting
- Add input validation

## ❤️ Credits

- **UNIHIKER K10** by DFRobot
- **MCP Protocol** by Anthropic
- **microdot** by Miguel Grinberg
- **implementation** by Claude Sonnet

---

## 📞 Support

**Problem?** Check the logs:

```python
# K10 REPL
import os
os.listdir('/')        # Check files
os.listdir('/lib')     # Check microdot
```

---

**Have fun with your AI-controlled K10!** 🤖✨

**Status:** ✅ v0.3.0 - HTTP Transport - Tested & Working
**License:** MIT
**Version:** 0.3.0 (November 2024)
