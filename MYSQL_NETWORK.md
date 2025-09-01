# MySQL Network Connectivity Guide

If you're having trouble connecting to MySQL from other devices on the network, follow these steps to resolve the issue.

## Configuring MySQL for Network Access

MySQL by default only listens for connections from the local machine (127.0.0.1). To allow connections from other devices, you need to:

1. **Run the MySQL Network Configuration Helper**:

   ``` INFO
   .\setup.bat mysql_network
   ```

   This will:
   - Locate your MySQL configuration file (my.ini)
   - Change the bind-address setting to 0.0.0.0
   - Restart the MySQL service
   - Check user permissions

2. **Update the Database Connection Settings**:

   ``` INFO
   .\setup.bat db_connection
   ```

   This will:
   - Update your .env file with the proper IP address
   - Test the connection to verify it works

## Manual Configuration Steps

If the automatic tools don't work, you can manually configure MySQL:

1. **Find your MySQL configuration file**:
   - Typically at `C:\ProgramData\MySQL\MySQL Server 8.0\my.ini`

2. **Edit the bind-address setting**:
   - Find the line with `bind-address=127.0.0.1`
   - Change it to `bind-address=0.0.0.0`
   - Save the file

3. **Restart MySQL**:
   - Open Services (services.msc)
   - Find the MySQL service
   - Right-click and select Restart

4. **Configure Windows Firewall**:
   - Open Windows Defender Firewall with Advanced Security
   - Click "Inbound Rules" and create a new rule
   - Allow TCP port 3306

## Checking MySQL User Permissions

Your database user needs permission to connect from remote hosts:

1. **Log into MySQL**:

   ```sql
   mysql -u root -p
   ```

2. **Check user permissions**:

   ```sql
   SELECT user, host FROM mysql.user;
   ```

3. **Create a user with network access**:

   ```sql
   CREATE USER 'workbox_user'@'%' IDENTIFIED BY 'password';
   GRANT ALL PRIVILEGES ON workbox_db.* TO 'workbox_user'@'%';
   FLUSH PRIVILEGES;
   ```

   (The '%' means "from any host")

## Common MySQL Connection Issues

| Problem | Possible Solution |
|---------|-------------------|
| "Host is not allowed to connect" | User doesn't have permission from that IP |
| "Access denied for user" | Incorrect username or password |
| "Connection refused" | MySQL not running or not listening on that address |
| "Can't connect to MySQL server" | Firewall blocking port 3306 |

## Testing MySQL Connectivity

From another device, you can test the connection:

```CMD
mysql -h YOUR_SERVER_IP -u workbox_user -p workbox_db
```

Replace `YOUR_SERVER_IP` with your server's actual IP address.

## Updating Your Application

After configuring MySQL, make sure your application's connection string in the `.env` file uses the server's IP address instead of "localhost".
