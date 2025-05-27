#!/bin/bash

AUTH_USER="kaled"
AUTH_PASS="pass"
SECURE_DIR="/var/www/html/secure"
HTPASSWD_FILE="/etc/apache2/.htpasswd"
APACHE_CONF="/etc/apache2/sites-available/000-default.conf"

echo "[+] Installing apache2-utils if needed..."
#sudo apt-get update -qq
#sudo apt-get install -y apache2 apache2-utils

echo "[+] Creating secure directory: $SECURE_DIR"
sudo mkdir -p "$SECURE_DIR"
sudo chown www-data:www-data "$SECURE_DIR"
echo "Secret Zone - Authorized Access Only" | sudo tee "$SECURE_DIR/index.html" > /dev/null

echo "[+] Creating .htpasswd with user '$AUTH_USER'"
sudo htpasswd -cb "$HTPASSWD_FILE" "$AUTH_USER" "$AUTH_PASS"

echo "[+] Updating Apache configuration to enable Basic Auth..."
if ! grep -q "$SECURE_DIR" "$APACHE_CONF"; then
    sudo tee -a "$APACHE_CONF" > /dev/null <<EOF

<Directory "$SECURE_DIR">
    AuthType Basic
    AuthName "Restricted Area"
    AuthUserFile $HTPASSWD_FILE
    Require valid-user
</Directory>
EOF
else
    echo "[i] Auth block already exists in Apache config."
fi

echo "[+] Restarting Apache server..."
sudo systemctl restart apache2

echo "[✔] Done! You can now access:"
echo "    http://localhost/secure"
echo
echo "[i] Username: $AUTH_USER"
echo "[i] Password: $AUTH_PASS"
