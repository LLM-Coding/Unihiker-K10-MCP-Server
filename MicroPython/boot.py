# boot.py - K10 Auto-Connect WiFi & Display IP
# Save this file as boot.py on the K10

from unihiker_k10 import wifi, screen
import time

# WiFi Configuration
WIFI_SSID = "Your-WiFi-Name"      # CHANGE THIS!
WIFI_PASSWORD = "Your-Password"   # CHANGE THIS!

def connect_wifi():
    """Connect to WiFi and display status"""
    screen.init(dir=2)
    
    # Display: Connecting
    screen.clear()
    screen.draw_text(text="WiFi...", line=3, font_size=30, color=0x0000FF)
    screen.draw_text(text="Connecting", line=5, font_size=20, color=0x808080)
    screen.show_draw()
    
    print(f'Connecting to {WIFI_SSID}...')
    
    # Connect with timeout (50 seconds)
    wifi.connect(ssid=WIFI_SSID, psd=WIFI_PASSWORD, timeout=50000)
    
    # Check status
    screen.clear()
    
    if wifi.status():
        # Get connection info
        info = wifi.info()
        print('✅ WiFi connected!')
        print(f'Info: {info}')
        
        # Parse IP from info string (format: "192.168.1.100, 255.255.255.0, ...")
        try:
            ip = info.split(',')[0].strip()
        except:
            ip = "Check REPL"
        
        # Display IP address
        screen.draw_text(text="WiFi OK", line=2, font_size=25, color=0x00FF00)
        screen.draw_text(text="IP:", line=4, font_size=20, color=0xFFFFFF)
        screen.draw_text(text=ip, line=5, font_size=16, color=0x00FFFF)
        screen.draw_text(text="MCP Server", line=7, font_size=18, color=0x808080)
        screen.draw_text(text="Starting...", line=8, font_size=16, color=0xFFA500)
        screen.show_draw()
        
        time.sleep(3)  # Show IP for 3 seconds
        
        return ip
    else:
        print('❌ WiFi connection failed')
        
        # Display error
        screen.draw_text(text="WiFi", line=3, font_size=30, color=0xFF0000)
        screen.draw_text(text="Failed!", line=5, font_size=25, color=0xFF0000)
        screen.draw_text(text="Check SSID", line=7, font_size=16, color=0x808080)
        screen.show_draw()
        
        return None

# Execute on boot
print("\n" + "="*40)
print("K10 MCP Server - Boot")
print("="*40)

ip = connect_wifi()

if ip:
    print(f"Server will start on http://{ip}:8080")
else:
    print("Please check WiFi configuration in boot.py")

print("="*40 + "\n")
