"""
K10 MCP Server with Streamable HTTP Transport
Version 0.3.0 - Simplified single-endpoint approach

Much simpler than SSE! Only one endpoint needed.
"""

import ujson as json
import asyncio
from microdot import Microdot, Response
from unihiker_k10 import screen, camera, tf_card
from unihiker_k10 import temp_humi, light, acce
from unihiker_k10 import rgb, button
from unihiker_k10 import mic, speaker
import time

app = Microdot()

# Initialize Hardware
screen.init(dir=2)

# MCP Protocol Version
MCP_VERSION = "2024-11-05"

# Session management (simple in-memory)
sessions = {}

# Tool Definitions (same as before)
TOOLS = [
    {
        "name": "set_rgb_led",
        "description": "Control K10 RGB LEDs (0, 1, 2, or ALL)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "led_num": {"type": "integer", "minimum": -1, "maximum": 2},
                "r": {"type": "integer", "minimum": 0, "maximum": 255},
                "g": {"type": "integer", "minimum": 0, "maximum": 255},
                "b": {"type": "integer", "minimum": 0, "maximum": 255}
            },
            "required": ["r", "g", "b"]
        }
    },
    {
        "name": "clear_rgb_leds",
        "description": "Turn off all RGB LEDs",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "set_rgb_brightness",
        "description": "Set RGB LED brightness (0-9)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brightness": {"type": "integer", "minimum": 0, "maximum": 9}
            },
            "required": ["brightness"]
        }
    },
    {
        "name": "get_temperature",
        "description": "Read temperature in Celsius",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_temperature_f",
        "description": "Read temperature in Fahrenheit",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_humidity",
        "description": "Read humidity percentage",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_light_level",
        "description": "Read ambient light level (0-4095)",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_acceleration",
        "description": "Read acceleration (x, y, z axes)",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "display_text",
        "description": "Show text on K10 display",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "x": {"type": "integer"},
                "y": {"type": "integer"},
                "line": {"type": "integer"},
                "font_size": {"type": "integer", "default": 16},
                "color": {"type": "integer", "default": 16777215},
                "clear": {"type": "boolean", "default": False}
            },
            "required": ["text"]
        }
    },
    {
        "name": "clear_display",
        "description": "Clear the K10 display",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "set_display_background",
        "description": "Set display background color",
        "inputSchema": {
            "type": "object",
            "properties": {
                "color": {"type": "integer"}
            },
            "required": ["color"]
        }
    },
    {
        "name": "draw_line",
        "description": "Draw a line on display",
        "inputSchema": {
            "type": "object",
            "properties": {
                "x0": {"type": "integer"}, "y0": {"type": "integer"},
                "x1": {"type": "integer"}, "y1": {"type": "integer"},
                "color": {"type": "integer", "default": 16777215}
            },
            "required": ["x0", "y0", "x1", "y1"]
        }
    },
    {
        "name": "draw_rectangle",
        "description": "Draw a rectangle on display",
        "inputSchema": {
            "type": "object",
            "properties": {
                "x": {"type": "integer"}, "y": {"type": "integer"},
                "w": {"type": "integer"}, "h": {"type": "integer"},
                "bcolor": {"type": "integer"},
                "fcolor": {"type": "integer"}
            },
            "required": ["x", "y", "w", "h", "bcolor"]
        }
    },
    {
        "name": "draw_circle",
        "description": "Draw a circle on display",
        "inputSchema": {
            "type": "object",
            "properties": {
                "x": {"type": "integer"}, "y": {"type": "integer"},
                "r": {"type": "integer"},
                "bcolor": {"type": "integer"},
                "fcolor": {"type": "integer"}
            },
            "required": ["x", "y", "r", "bcolor"]
        }
    }
]

# Tool Implementations (same as before)
def execute_tool(name, arguments):
    """Execute a tool and return result"""
    try:
        if name == "set_rgb_led":
            led_num = arguments.get("led_num", -1)
            r = arguments["r"]
            g = arguments["g"]
            b = arguments["b"]
            rgb.write(num=led_num, R=r, G=g, B=b)
            msg = f"All LEDs set to RGB({r}, {g}, {b})" if led_num == -1 else f"LED {led_num} set to RGB({r}, {g}, {b})"
            return {"content": [{"type": "text", "text": msg}]}
        
        elif name == "clear_rgb_leds":
            rgb.clear()
            return {"content": [{"type": "text", "text": "All LEDs cleared"}]}
        
        elif name == "set_rgb_brightness":
            brightness = arguments["brightness"]
            rgb.brightness(brightness)
            return {"content": [{"type": "text", "text": f"Brightness set to {brightness}"}]}
        
        elif name == "get_temperature":
            temp = temp_humi.read_temp()
            return {"content": [{"type": "text", "text": f"Temperature: {temp}°C"}]}
        
        elif name == "get_temperature_f":
            temp = temp_humi.read_temp_f()
            return {"content": [{"type": "text", "text": f"Temperature: {temp}°F"}]}
        
        elif name == "get_humidity":
            humidity = temp_humi.read_humi()
            return {"content": [{"type": "text", "text": f"Humidity: {humidity}%"}]}
        
        elif name == "get_light_level":
            light_level = light.read()
            return {"content": [{"type": "text", "text": f"Light level: {light_level}"}]}
        
        elif name == "get_acceleration":
            ax = acce.read_x()
            ay = acce.read_y()
            az = acce.read_z()
            return {"content": [{"type": "text", "text": f"Acceleration - X: {ax}, Y: {ay}, Z: {az}"}]}
        
        elif name == "display_text":
            text = arguments["text"]
            font_size = arguments.get("font_size", 16)
            color = arguments.get("color", 0xFFFFFF)
            clear = arguments.get("clear", False)
            
            if clear:
                screen.clear()
            
            if "line" in arguments:
                line = arguments["line"]
                screen.draw_text(text=text, line=line, font_size=font_size, color=color)
            else:
                x = arguments.get("x", 10)
                y = arguments.get("y", 10)
                screen.draw_text(text=text, x=x, y=y, font_size=font_size, color=color)
            
            screen.show_draw()
            return {"content": [{"type": "text", "text": f"Displayed: '{text}'"}]}
        
        elif name == "clear_display":
            screen.clear()
            screen.show_draw()
            return {"content": [{"type": "text", "text": "Display cleared"}]}
        
        elif name == "set_display_background":
            color = arguments["color"]
            screen.show_bg(color=color)
            return {"content": [{"type": "text", "text": f"Background set to 0x{color:06X}"}]}
        
        elif name == "draw_line":
            x0, y0 = arguments["x0"], arguments["y0"]
            x1, y1 = arguments["x1"], arguments["y1"]
            color = arguments.get("color", 0xFFFFFF)
            screen.draw_line(x0=x0, y0=y0, x1=x1, y1=y1, color=color)
            screen.show_draw()
            return {"content": [{"type": "text", "text": f"Line drawn from ({x0},{y0}) to ({x1},{y1})"}]}
        
        elif name == "draw_rectangle":
            x, y = arguments["x"], arguments["y"]
            w, h = arguments["w"], arguments["h"]
            bcolor = arguments["bcolor"]
            fcolor = arguments.get("fcolor")
            
            if fcolor is not None:
                screen.draw_rect(x=x, y=y, w=w, h=h, bcolor=bcolor, fcolor=fcolor)
            else:
                screen.draw_rect(x=x, y=y, w=w, h=h, bcolor=bcolor)
            
            screen.show_draw()
            return {"content": [{"type": "text", "text": f"Rectangle drawn at ({x},{y}) size {w}x{h}"}]}
        
        elif name == "draw_circle":
            x, y, r = arguments["x"], arguments["y"], arguments["r"]
            bcolor = arguments["bcolor"]
            fcolor = arguments.get("fcolor")
            
            if fcolor is not None:
                screen.draw_circle(x=x, y=y, r=r, bcolor=bcolor, fcolor=fcolor)
            else:
                screen.draw_circle(x=x, y=y, r=r, bcolor=bcolor)
            
            screen.show_draw()
            return {"content": [{"type": "text", "text": f"Circle drawn at ({x},{y}) radius {r}"}]}
        
        else:
            return {
                "content": [{"type": "text", "text": f"Unknown tool: {name}"}],
                "isError": True
            }
    
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error executing {name}: {str(e)}"}],
            "isError": True
        }

# MCP JSON-RPC Handler
def handle_mcp_request(request_data, session_id=None):
    """Handle MCP JSON-RPC request"""
    method = request_data.get("method")
    request_id = request_data.get("id")
    params = request_data.get("params", {})
    
    print(f"MCP Request: {method}")
    
    if method == "initialize":
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": MCP_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "k10-mcp-server",
                    "version": "0.3.0"
                }
            }
        }
        return response
    
    elif method == "tools/list":
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": TOOLS}
        }
        return response
    
    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        result = execute_tool(tool_name, arguments)
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
        return response
    
    else:
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }
        return response

# Single MCP Endpoint (Streamable HTTP)
@app.route('/mcp', methods=['POST'])
async def mcp_endpoint(request):
    """
    Single MCP endpoint for Streamable HTTP transport
    Handles all MCP JSON-RPC messages
    """
    try:
        # Parse request
        if isinstance(request.body, bytes):
            request_data = json.loads(request.body.decode('utf-8'))
        else:
            request_data = json.loads(request.body)
        
        # Get or create session ID
        session_id = request.headers.get('Mcp-Session-Id')
        
        # Handle request
        response_data = handle_mcp_request(request_data, session_id)
        
        # Return JSON response (no streaming for now, simpler)
        response_json = json.dumps(response_data).encode('utf-8')
        
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
        
        # Add session ID if this is initialize
        if request_data.get("method") == "initialize" and not session_id:
            import os
            session_id = str(os.urandom(8).hex())
            sessions[session_id] = {"created": time.time()}
            headers['Mcp-Session-Id'] = session_id
            print(f"Created session: {session_id}")
        
        return Response(response_json, headers=headers)
    
    except Exception as e:
        print(f"Error in mcp_endpoint: {e}")
        error_response = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }
        return Response(
            json.dumps(error_response).encode('utf-8'),
            status_code=500,
            headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        )

# CORS Support
@app.route('/mcp', methods=['OPTIONS'])
async def options_mcp(request):
    return Response(
        b'',
        headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Mcp-Session-Id',
            'Access-Control-Expose-Headers': 'Mcp-Session-Id'
        }
    )

# Health Check
@app.route('/')
async def index(request):
    """Health check endpoint"""
    print("Health check request")
    response_data = {
        "server": "k10-mcp-server",
        "version": "0.3.0",
        "transport": "streamable-http",
        "status": "running",
        "mcp_version": MCP_VERSION,
        "endpoint": "/mcp"
    }
    return Response(
        json.dumps(response_data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )

# Main
if __name__ == '__main__':
    print("="*50)
    print("K10 MCP Server v0.3.0")
    print("Transport: Streamable HTTP (single endpoint)")
    print("="*50)
    print("MCP endpoint: http://[K10-IP]:8080/mcp")
    print("Health check: http://[K10-IP]:8080/")
    print("="*50)
    
    # Display startup on K10
    screen.clear()
    screen.draw_text(text="MCP v0.3", line=3, font_size=28, color=0x00FFFF)
    screen.draw_text(text="HTTP Mode", line=5, font_size=20, color=0x00FF00)
    screen.draw_text(text="/mcp", line=7, font_size=18, color=0xFFFFFF)
    screen.show_draw()
    
    # Start server
    app.run(host='0.0.0.0', port=8080, debug=True)
