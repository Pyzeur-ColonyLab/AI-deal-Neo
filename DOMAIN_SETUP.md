# Domain Setup Guide - cryptomaltese.com

## 🎯 **Overview**

This guide shows you how to make your Aid-al-Neo API accessible at `cryptomaltese.com` instead of localhost.

## 🌐 **Option 1: Direct Public Access (Quick Setup)**

### **Step 1: Update Server Configuration**
```bash
# Make the script executable
chmod +x run_server_public.py

# Edit the API keys for security
nano run_server_public.py
# Change these lines:
# os.environ.setdefault("API_KEY", "your_secure_api_key_here")
# os.environ.setdefault("ADMIN_TOKEN", "your_secure_admin_token_here")
```

### **Step 2: Start Public Server**
```bash
# Start server on all interfaces
python3 run_server_public.py
```

### **Step 3: Configure Firewall**
```bash
# Allow port 8000 through firewall
sudo ufw allow 8000

# Check firewall status
sudo ufw status
```

### **Step 4: Test Public Access**
```bash
# Test from another machine
curl https://cryptomaltese.com:8000/health
```

**⚠️ WARNING**: This approach exposes your server directly to the internet. Only use with proper security measures!

---

## 🌐 **Option 2: Nginx Reverse Proxy (Recommended)**

### **Step 1: Install Nginx**
```bash
# Install Nginx
sudo apt update
sudo apt install nginx

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### **Step 2: Configure SSL Certificates**

#### **Option A: Let's Encrypt (Free)**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d cryptomaltese.com -d www.cryptomaltese.com

# Auto-renewal
sudo crontab -e
# Add this line:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

#### **Option B: Manual SSL Setup**
```bash
# Create SSL directory
sudo mkdir -p /etc/ssl/{certs,private}

# Place your SSL certificates
sudo cp your_certificate.crt /etc/ssl/certs/cryptomaltese.com.crt
sudo cp your_private_key.key /etc/ssl/private/cryptomaltese.com.key

# Set proper permissions
sudo chmod 644 /etc/ssl/certs/cryptomaltese.com.crt
sudo chmod 600 /etc/ssl/private/cryptomaltese.com.key
```

### **Step 3: Configure Nginx**
```bash
# Copy the Nginx configuration
sudo cp nginx_cryptomaltese.conf /etc/nginx/sites-available/cryptomaltese.com

# Enable the site
sudo ln -s /etc/nginx/sites-available/cryptomaltese.com /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### **Step 4: Start Your API Server**
```bash
# Start your API server (locally)
python3 run_server.py
```

### **Step 5: Test Domain Access**
```bash
# Test health endpoint
curl https://cryptomaltese.com/health

# Test API endpoint
curl -X POST https://cryptomaltese.com/api/v1/chat \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "channel": "test", "user_id": "test"}'

# Test documentation
curl https://cryptomaltese.com/docs
```

---

## 🔧 **DNS Configuration**

### **Step 1: Configure DNS Records**
In your domain registrar's DNS settings, add:

```
Type: A
Name: @ (or cryptomaltese.com)
Value: YOUR_SERVER_IP_ADDRESS
TTL: 300

Type: A
Name: www
Value: YOUR_SERVER_IP_ADDRESS
TTL: 300
```

### **Step 2: Find Your Server IP**
```bash
# Get your server's public IP
curl ifconfig.me
# or
curl ipinfo.io/ip
```

---

## 🔒 **Security Checklist**

### **Before Going Live:**
- [ ] Change default API keys
- [ ] Set up SSL certificates
- [ ] Configure firewall rules
- [ ] Set up monitoring
- [ ] Enable rate limiting
- [ ] Set up logging
- [ ] Test all endpoints

### **Firewall Configuration**
```bash
# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow SSH (if needed)
sudo ufw allow ssh

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

---

## 📊 **Testing Your Setup**

### **Health Check**
```bash
curl https://cryptomaltese.com/health
```

### **API Test**
```bash
curl -X POST https://cryptomaltese.com/api/v1/chat \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Bonjour, expliquez-moi les règles de licenciement en France",
    "channel": "web",
    "user_id": "test_user"
  }'
```

### **Documentation Access**
```bash
# Open in browser
https://cryptomaltese.com/docs
```

---

## 🚀 **Production Deployment**

### **Option A: Direct Python with Systemd**
```bash
# Create systemd service
sudo tee /etc/systemd/system/aidalneo.service << EOF
[Unit]
Description=Aid-al-Neo API Server
After=network.target

[Service]
Type=simple
User=debian
WorkingDirectory=/home/debian/AI-deal-Neo
Environment=ENV=production
Environment=API_KEY=your_production_api_key
Environment=ADMIN_TOKEN=your_production_admin_token
ExecStart=/usr/bin/python3 run_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl enable aidalneo
sudo systemctl start aidalneo
```

### **Option B: Docker with Nginx**
```bash
# Use the production Docker setup
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🔍 **Troubleshooting**

### **Common Issues:**

#### **1. DNS Not Resolving**
```bash
# Check DNS propagation
nslookup cryptomaltese.com
dig cryptomaltese.com
```

#### **2. SSL Certificate Issues**
```bash
# Test SSL
openssl s_client -connect cryptomaltese.com:443 -servername cryptomaltese.com
```

#### **3. Nginx Not Working**
```bash
# Check Nginx status
sudo systemctl status nginx

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
```

#### **4. API Server Not Responding**
```bash
# Check if server is running
ps aux | grep python3

# Check server logs
tail -f ./logs/api.log
```

---

## 📈 **Monitoring**

### **Set Up Monitoring**
```bash
# Monitor Nginx logs
sudo tail -f /var/log/nginx/cryptomaltese_access.log

# Monitor API logs
tail -f ./logs/api.log

# Monitor system resources
htop
```

### **Health Monitoring**
```bash
# Create a monitoring script
cat > monitor_api.sh << 'EOF'
#!/bin/bash
response=$(curl -s -o /dev/null -w "%{http_code}" https://cryptomaltese.com/health)
if [ $response -eq 200 ]; then
    echo "API is healthy"
else
    echo "API is down (HTTP $response)"
    # Add alerting here
fi
EOF

chmod +x monitor_api.sh

# Add to crontab for regular monitoring
crontab -e
# Add: */5 * * * * /path/to/monitor_api.sh
```

---

## 🎯 **Final Steps**

1. **Test Everything**: Verify all endpoints work
2. **Monitor Performance**: Watch logs and metrics
3. **Set Up Alerts**: Configure monitoring alerts
4. **Backup Configuration**: Save your setup
5. **Document**: Keep notes of your configuration

Your API will now be accessible at `https://cryptomaltese.com`! 🎉 