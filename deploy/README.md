# Max Level Priest Website - VPS Deployment Guide

This guide covers deploying the book reading website to your VPS with nginx and Cloudflare.

## Prerequisites

- VPS with Ubuntu/Debian
- Domain pointed to VPS via Cloudflare
- nginx installed (`sudo apt install nginx`)

## Deployment Steps

### 1. Upload Website Files

```bash
# Create website directory
sudo mkdir -p /var/www/maxlevelpriest

# Upload the website folder contents to /var/www/maxlevelpriest
# Using SCP from your local machine:
scp -r website/* user@your-vps-ip:/var/www/maxlevelpriest/

# Set proper ownership
sudo chown -R www-data:www-data /var/www/maxlevelpriest
```

### 2. Configure nginx

Create nginx site configuration:

```bash
sudo nano /etc/nginx/sites-available/maxlevelpriest
```

Paste this configuration:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name your-domain.com www.your-domain.com;
    
    root /var/www/maxlevelpriest;
    index index.html;
    
    # Main location
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Cache static assets
    location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # Cache JSON data
    location ~* \.json$ {
        expires 1h;
        add_header Cache-Control "public";
    }
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_types
        text/plain
        text/css
        text/javascript
        application/javascript
        application/json
        application/xml;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/maxlevelpriest /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. Cloudflare Setup

Since you're using Cloudflare:

1. **SSL/TLS**: Set to "Flexible" or "Full" in Cloudflare dashboard
2. **Page Rules** (optional):
   - Cache Level: Cache Everything for static assets
   - Browser Cache TTL: 1 year for CSS/JS

With Cloudflare's proxy enabled, HTTPS is handled automatically.

### 4. Update Chapters

When you have new chapters:

1. Add new `.vn.txt` files to `Chapters/` directory
2. Run: `python scripts/parse_chapters.py`
3. Upload updated `website/js/chapters.js` to VPS:
   ```bash
   scp website/js/chapters.js user@your-vps-ip:/var/www/maxlevelpriest/js/
   ```

## File Structure on VPS

```
/var/www/maxlevelpriest/
├── index.html
├── reader.html
├── css/
│   └── main.css
├── js/
│   ├── app.js
│   ├── reader.js
│   └── chapters.js
└── data/
    └── chapters.json
```

## Testing

After deployment, verify:

1. ✓ Homepage loads with chapter list
2. ✓ Click chapter to open reader
3. ✓ Theme switching works (dark/light/sepia)
4. ✓ Font size slider works
5. ✓ Chapter navigation (prev/next) works
6. ✓ Mobile responsive design
7. ✓ Reading progress saves

---

## Backend API Deployment (Optional)

To enable the Admin Panel for running scripts from the web:

### 1. Install Backend Dependencies

```bash
# On VPS, install Python dependencies
cd /var/www/maxlevelpriest-backend
pip install -r requirements.txt
```

### 2. Create Systemd Service

```bash
sudo nano /etc/systemd/system/maxlevelpriest-api.service
```

```ini
[Unit]
Description=Max Level Priest API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/maxlevelpriest-backend
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable maxlevelpriest-api
sudo systemctl start maxlevelpriest-api
```

### 3. Update nginx Config

Add API proxy to your nginx config:

```nginx
# Add inside server block
location /api/ {
    proxy_pass http://127.0.0.1:8000/api/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_buffering off;  # Important for SSE
}
```

Reload nginx:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

### 4. Access Admin Panel

Navigate to `https://your-domain.com/admin.html`
