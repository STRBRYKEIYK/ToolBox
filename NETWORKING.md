# WorkBox Network Configuration Guide

This guide provides detailed information on configuring WorkBox for multi-device access across your network.

## Basic Network Setup

WorkBox is designed to be accessible from any device on your local network. Follow these steps to properly configure it:

### 1. Server Configuration

By default, the WorkBox server listens on all network interfaces (`0.0.0.0`), making it accessible from other devices:

```python
# Configuration in main.py
uvicorn.run(
    "WorkBox.api.server:app",
    host="0.0.0.0",  # Listen on all network interfaces
    port=8000,
    reload=True,
    log_level="info",
)
```

### 2. Finding Your Server's IP Address

To connect from other devices, you need to know your server's IP address. Use the network test tool:

```bash
# Windows
.\setup.bat network

# Alternative methods
ipconfig                  # Windows
ip addr                   # Linux
ifconfig                  # macOS/Linux
```

Look for the IPv4 address on your active network connection (like 192.168.1.x or 10.0.0.x).

### 3. Accessing the Application

From any device on the same network:

- API Documentation: `http://YOUR_SERVER_IP:8000/docs`
- WebSocket Endpoint: `ws://YOUR_SERVER_IP:8000/ws`

## Troubleshooting Connection Issues

### Check Network Connectivity

1. **Ping Test**: From the client device, test basic connectivity:

   ```bash
   ping YOUR_SERVER_IP
   ```

2. **Ensure Same Network**: Both devices must be on the same network (same Wi-Fi or connected to the same router)

3. **Check Network Isolation**: Some public or corporate Wi-Fi networks prevent device-to-device communication

### Firewall Configuration

Windows Firewall often blocks incoming connections:

#### Temporarily Disable Firewall (for testing only)

1. Open Windows Security
2. Select "Firewall & Network Protection"
3. Turn off the firewall for your network profile

#### Create a Firewall Exception (recommended)

```powershell
# Run as Administrator
New-NetFirewallRule -DisplayName "WorkBox API" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

Or use the GUI method:

1. Open "Windows Defender Firewall with Advanced Security"
2. Select "Inbound Rules" > "New Rule..."
3. Choose "Port" > "TCP" > Specific port: "8000"
4. Choose "Allow the connection"
5. Apply to all profiles
6. Name it "WorkBox API"

### Using HTTPS for Secure Connections

For secure connections, use HTTPS:

```bash
# Generate certificates
.\setup.bat setup_https

# Start with HTTPS
.\setup.bat run_secure
```

Then connect using:

```URL
https://YOUR_SERVER_IP:8000
```

Note: You will need to accept the self-signed certificate warning.

## Network Connectivity Test Tool

WorkBox includes a network test tool to diagnose connection issues:

```bash
.\setup.bat network
```

This displays:

- Your server's IP address
- Server running status
- Firewall status
- Connection instructions

## Common Problems and Solutions

### "Connection refused" Error

**Possible causes:**

- Server not running
- Wrong IP address or port
- Firewall blocking connection

**Solutions:**

1. Verify server is running with `.\setup.bat run`
2. Confirm correct IP address with `.\setup.bat network`
3. Temporarily disable firewall to test

### Client Can't Connect Despite Server Running

**Possible causes:**

- Network isolation
- IP address changed
- Wrong network interface

**Solutions:**

1. Check if both devices are on the same network
2. Run `.\setup.bat network` to verify current IP
3. Try connecting to localhost from the server machine

### Database Connection Issues

If API works locally but database connections fail:

1. Verify MySQL server allows remote connections
2. Check firewall for port 3306 (MySQL)
3. Verify database credentials in .env file

## Advanced Configuration

### Running on a Different Port

Edit `main.py` and change the port number:

```python
port=8080,  # Changed from default 8000
```

Remember to update firewall rules for the new port.

### CORS Configuration

If you're developing a separate frontend, modify CORS settings in `server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://example.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
