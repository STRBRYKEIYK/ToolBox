"""
WorkBox Network Connectivity Tester
==================================

This script helps diagnose network connectivity issues when accessing
the WorkBox server from other devices on the network.
"""

import socket
import subprocess

# Try to import colorama, but provide fallbacks if not available
try:
    from colorama import init, Fore, Style
    init()
    HAS_COLORS = True
except ImportError:
    # Define color constants for when colorama is not available
    class DummyColors:
        def __getattr__(self, name: str) -> str:
            return ""
    
    # Create dummy objects with the same type annotation as colorama's objects
    Fore = DummyColors()  # type: ignore
    Style = DummyColors()  # type: ignore
    HAS_COLORS = False

def print_header(text):
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{text}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'-' * len(text)}{Style.RESET_ALL}")

def print_success(text):
    print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")

def print_warning(text):
    print(f"{Fore.YELLOW}⚠ {text}{Style.RESET_ALL}")

def print_error(text):
    print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")

def print_info(text):
    print(f"{Fore.BLUE}ℹ {text}{Style.RESET_ALL}")

def get_local_ip():
    """Get the local IP address of this machine"""
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    return ip

def check_port_open(port):
    """Check if a port is open on this machine"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            s.listen(1)
            s.close()
            return False
        except OSError:
            return True

def check_firewall_status():
    """Check the status of Windows Firewall"""
    try:
        result = subprocess.run(
            ['netsh', 'advfirewall', 'show', 'currentprofile', 'state'], 
            capture_output=True, 
            text=True
        )
        return "ON" in result.stdout
    except Exception:
        return None

def main():
    print(f"{Fore.CYAN}{Style.BRIGHT}===================================={Style.RESET_ALL}")
    print(f"{Fore.CYAN}{Style.BRIGHT} WorkBox Network Connectivity Test {Style.RESET_ALL}")
    print(f"{Fore.CYAN}{Style.BRIGHT}===================================={Style.RESET_ALL}")
    
    # Get local IP
    local_ip = get_local_ip()
    print_header("Network Information")
    print(f"Computer Name: {socket.gethostname()}")
    print(f"IP Address: {local_ip}")
    
    # Check if server is running
    print_header("Server Status")
    server_port = 8000
    if check_port_open(server_port):
        print_success(f"Server appears to be running on port {server_port}")
    else:
        print_error(f"Server does not appear to be running on port {server_port}")
        print_info("Start the server first with: python main.py")
    
    # Check firewall status
    print_header("Firewall Status")
    firewall_status = check_firewall_status()
    if firewall_status is True:
        print_warning("Windows Firewall is ON")
        print_info("This might block incoming connections unless you've added an exception")
        print_info("You can temporarily disable it with: netsh advfirewall set currentprofile state off")
    elif firewall_status is False:
        print_success("Windows Firewall is OFF")
        print_warning("This allows all connections but reduces security")
    else:
        print_info("Could not determine firewall status")
    
    # Connection instructions
    print_header("Connection Instructions")
    print_info("1. From your tablet or another device, connect to:")
    print(f"   http://{local_ip}:8000")
    print(f"   http://{local_ip}:8000/docs  (for API documentation)")
    
    print_header("Troubleshooting Tips")
    print_info("1. Make sure both devices are on the same network/WiFi")
    print_info("2. Try pinging this computer from your tablet")
    print_info("3. Check if any antivirus is blocking connections")
    print_info("4. If using secure mode (HTTPS), accept the certificate warning")
    
    print()
    print_info("To create a firewall rule allowing connections:")
    print("netsh advfirewall firewall add rule name=\"WorkBox API\" dir=in action=allow protocol=TCP localport=8000")
    
    print()
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
