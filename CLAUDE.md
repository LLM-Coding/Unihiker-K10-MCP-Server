# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **embedded MCP (Model Context Protocol) server** that runs directly on the UNIHIKER K10, a comprehensive K12 STEM education board designed for teaching AI, IoT, and physical computing to students in grades 3-12. The K10 features:

- **ESP32-S3N16R8** dual-core Tensilica LX7 @ 240 MHz
- **Memory:** 512KB SRAM + 8MB PSRAM + 16MB Flash
- **Integrated components:** 2.8" ILI9341 TFT display (240x320), 2MP camera, 2-microphone array, speaker, RGB LEDs
- **Sensors:** Temperature/humidity, light, accelerometer
- **AI capabilities:** 4 pre-installed TinyML models (Face Detection, Pet Recognition, QR Code, Motion Detection), offline speech recognition
- **Connectivity:** WiFi 2.4GHz, Bluetooth 5.0, Micro:bit-compatible edge connector
- **Ecosystem:** DFRobot Gravity port system for easy sensor/actuator expansion
- **Programming:** Mind+ (block-based) and MicroPython

The MCP server enables AI assistants like Claude to control this physical hardware over HTTP without requiring a gateway computer.

**Current Version:** 0.3.0
**Language:** MicroPython (1.20+)
**Protocol:** MCP JSON-RPC 2.0 over HTTP

## Repository Structure

```
/
├── MicroPython/
│   ├── k10-mcp-server.py    # Main MCP server (upload as main.py to K10)
│   ├── boot.py              # WiFi auto-connect (configure SSID/password)
│   ├── README.md            # User-facing documentation
│   ├── quickstart.md        # Setup guide
│   └── docs/arc42/          # Architecture documentation (AsciiDoc)
├── README.adoc              # Project overview
└── CLAUDE.md                # This file
```

## Development Commands

### Testing the MCP Server

Since this runs on embedded hardware, testing requires the K10 board:

1. **Deploy to K10:**
   - Use Thonny IDE connected to K10 via USB
   - Upload `MicroPython/k10-mcp-server.py` as `main.py`
   - Upload `MicroPython/boot.py` after editing WiFi credentials (lines 8-9)

2. **Test server health:**
   ```bash
   curl http://[K10-IP]:8080/
   ```
   Expected: JSON response with server info

3. **Test MCP endpoint:**
   ```bash
   curl -X POST http://[K10-IP]:8080/mcp \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'
   ```

4. **Full integration test:**
   ```bash
   # From MicroPython/ directory
   python test_k10_mcp.py [K10-IP] demo
   ```

### Documentation

**View AsciiDoc with Kroki diagrams:**
- VSCode extension: "AsciiDoc" by asciidoctor
- Settings already configured in `.vscode/settings.json` for Kroki diagram rendering

**Architecture docs:**
- `MicroPython/docs/arc42/` contains comprehensive arc42 documentation
- Key files: `01-introduction.adoc`, `04-solution-strategy.adoc`

## Architecture Essentials

### Core Design Decisions

1. **Single HTTP Endpoint (`/mcp`):**
   - All MCP JSON-RPC methods handled by one route
   - Method dispatch via `method` field in request body
   - See: `docs/arc42/09-decisions/ADR-002-single-endpoint.adoc`

2. **Synchronous Tool Execution:**
   - No async/await for hardware operations
   - Tools execute sequentially (prevent race conditions on I2C bus)
   - Hardware operations complete in <100ms

3. **In-Memory Session Management:**
   - `sessions = {}` dict in RAM
   - No persistence (sessions reset on reboot)
   - Acceptable for development/educational use

4. **Tool Definitions Hardcoded:**
   - `TOOLS = [...]` list in `k10-mcp-server.py`
   - Schema + implementation co-located
   - No external JSON files (faster, fewer dependencies)

### MCP Request Flow

```
Client → POST /mcp → handle_mcp_request()
                         ↓
                    [method dispatch]
                         ↓
         ┌──────────────┼──────────────┐
         ↓              ↓              ↓
    initialize    tools/list    tools/call
                                     ↓
                               execute_tool()
                                     ↓
                              [hardware access]
                                     ↓
                              JSON response
```

### Hardware Abstraction

The server uses the `unihiker_k10` MicroPython module for hardware access:

- **RGB LEDs:** `rgb.write()`, `rgb.clear()`, `rgb.brightness()`
- **Sensors:** `temp_humi.read_temp()`, `light.read()`, `acce.read_x()`
- **Display (ILI9341):** `screen.draw_text()`, `screen.draw_line()`, `screen.show_draw()`
- **Audio:** `mic.start()`, `speaker.play_sound()` (2-mic array + speaker for offline speech recognition)
- **Camera/AI:** Hardware available (2MP camera + 4 TinyML models) but **cannot run simultaneously with WiFi** in MicroPython due to memory constraints. Planned Arduino version will support ML features.

## Version Management

**CRITICAL:** Always update version number in THREE places when changing functionality:

1. `k10-mcp-server.py` line 3: Docstring version comment
2. `k10-mcp-server.py` line 300: `"version": "X.Y.Z"` in serverInfo
3. `k10-mcp-server.py` line 414: `"version": "X.Y.Z"` in health check
4. Display text in startup (line 436): `"MCP vX.Y"`

Use semantic versioning: MAJOR.MINOR.PATCH

## Constraints and Limitations

### Hardware
- **Memory:** 512KB SRAM + 8MB PSRAM (~100KB SRAM available after OS; PSRAM used for ML operations)
- **ESP32-S3N16R8** dual-core Tensilica LX7 @ 240 MHz (MicroPython uses single core effectively)
- **No TLS support** (MicroPython asyncio limitation)
- **WiFi + ML conflict:** Cannot use camera/TinyML and WiFi simultaneously in MicroPython (driver/memory conflict)
- **Education-focused design:** Optimized for learning and prototyping, not production deployments

### MicroPython Specifics
- Use `ujson` instead of `json` (smaller memory footprint)
- Avoid large string concatenations (use list + join)
- No decorators with arguments in some MicroPython versions
- File I/O slower than CPython (SD card access)

### MCP Protocol
- **No streaming resources** (memory constraints)
- **No server-initiated notifications** (HTTP is request/response only)
- **Poll-based sensor reading** (no push updates)

## Adding New Tools

To add a hardware control tool:

1. **Define schema in `TOOLS` list** (around line 29):
   ```python
   {
       "name": "tool_name",
       "description": "What it does",
       "inputSchema": {
           "type": "object",
           "properties": {
               "param": {"type": "integer"}
           },
           "required": ["param"]
       }
   }
   ```

2. **Add handler in `execute_tool()`** (around line 162):
   ```python
   elif name == "tool_name":
       param = arguments["param"]
       # ... hardware interaction ...
       return {"content": [{"type": "text", "text": "Success message"}]}
   ```

3. **Test with curl** before deploying to Claude Desktop

## Common Issues

### Server Won't Start
- Check WiFi credentials in `boot.py`
- Verify `microdot` installed: `import microdot` in REPL
- K10 only supports 2.4 GHz WiFi (not 5 GHz)

### Memory Errors
- Each tool call uses ~5-10KB RAM
- Keep tool responses under 200 characters
- Clear display buffer after drawing: `screen.show_draw()`

### Import Errors
- MicroPython path: libraries go in `/lib/` on K10
- `ujson` vs `json`: prefer `ujson` (line 8 import)
- Hardware module must be `unihiker_k10` (not `k10` or `unihiker`)

## Future Roadmap (from arc42 docs)

### Planned Features (v0.4+)
- Camera control tools (capture with 2MP camera)
- Pre-installed AI model tools (Face Detection, Pet Recognition, QR Code, Motion Detection)
- Microphone/Speaker tools (offline speech recognition, audio playback)
- MCP resources (sensor data streams)
- WebSocket transport (bidirectional communication)
- Arduino/C++ version (enables WiFi + ML simultaneously, bypassing MicroPython limitation)

### Deprecated/Will Be Removed
- SSE transport (removed in v0.5)
- Multi-endpoint design (removed in v0.5)

## Testing Guidelines

- **No unit tests** (MicroPython mocking complex)
- **Integration testing:** Use curl or `test_k10_mcp.py`
- **Hardware-in-loop:** Always test on actual K10 before release
- **Display feedback:** Use `screen.draw_text()` for status messages during development

## Security Notes

⚠️ **No authentication by default** - intended for local network/educational use

For production use, implement:
- API key authentication (check header in `mcp_endpoint()`)
- Rate limiting (track requests per session)
- Input validation (sanitize tool arguments)
- HTTPS via reverse proxy (MicroPython doesn't support TLS)

## Documentation Philosophy

This project uses **arc42** architecture documentation:
- Human-readable context over auto-generated API docs
- Focus on "why" decisions were made (ADRs in `09-decisions/`)
- Stakeholder-oriented (hobbyists, educators, researchers)
- AsciiDoc with Kroki diagrams for visual architecture

When updating architecture docs, regenerate SVGs:
```bash
# Diagrams auto-generated from AsciiDoc via Kroki
# VSCode preview updates them automatically
```
