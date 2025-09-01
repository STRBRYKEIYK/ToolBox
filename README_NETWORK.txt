===================================================
    WORKBOX NETWORK CONNECTION INSTRUCTIONS
===================================================

Here's how to make sure you can connect to WorkBox from other devices:

QUICK START:
-----------
1. Run this command from the WorkBox directory:
   
   .\setup.bat connection
   
   This will show your computer's IP address and create a QR code
   that you can scan with your tablet to connect.

FIXING FIREWALL ISSUES:
---------------------
If the connection doesn't work, you may need to allow the application
through your firewall:

1. Right-click on "fix_connection.bat" in Windows Explorer
2. Select "Run as administrator"
3. Follow the prompts to create firewall rules automatically

CONNECTING FROM OTHER DEVICES:
----------------------------
Once the server is running:

1. Make sure both devices are on the same Wi-Fi network
2. On your tablet or other device, open a browser
3. Go to: http://YOUR_COMPUTER_IP:8000/docs
   (Replace YOUR_COMPUTER_IP with the address shown when you run check_connection.bat)

TROUBLESHOOTING:
--------------
If you have connection problems:

1. Try running the server with: .\setup.bat run
2. Check the firewall settings: Right-click fix_connection.bat > Run as administrator
3. Make sure all devices are on the same network
4. If using a work or public network, these may block device-to-device connections

For more detailed help, see NETWORKING.md
