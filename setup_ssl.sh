#!/bin/bash

# SSL Setup Script for Social Network
# This script sets up SSL certificates using Let's Encrypt

set -e

echo "🔒 Setting up SSL certificates for my.ozimiz.org..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found! Please run generate_secrets.py first."
    exit 1
fi

# Load environment variables
source .env

# Check if domain is set
if [ -z "$DOMAIN" ]; then
    echo "❌ DOMAIN not set in .env file!"
    exit 1
fi

if [ -z "$CERTBOT_EMAIL" ]; then
    echo "❌ CERTBOT_EMAIL not set in .env file!"
    exit 1
fi

# Create directories for certbot
echo "📁 Creating certbot directories..."
mkdir -p certbot/conf
mkdir -p certbot/www
mkdir -p ssl

# Stop nginx if running
echo "🛑 Stopping nginx..."
docker-compose stop nginx || true

# Start nginx with HTTP only for initial certificate
echo "🚀 Starting nginx for certificate validation..."
docker-compose up -d nginx

# Wait for nginx to start
echo "⏳ Waiting for nginx to start..."
sleep 10

# Get initial certificate
echo "🔐 Getting initial SSL certificate..."
docker-compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email "$CERTBOT_EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN"

# Restart nginx with SSL
echo "🔄 Restarting nginx with SSL..."
docker-compose restart nginx

# Create renewal script
echo "📝 Creating certificate renewal script..."
cat > renew_ssl.sh << 'EOF'
#!/bin/bash
# Certificate renewal script

set -e

echo "🔄 Renewing SSL certificates..."

# Stop nginx
docker-compose stop nginx

# Renew certificates
docker-compose run --rm certbot renew

# Start nginx
docker-compose up -d nginx

echo "✅ SSL certificates renewed successfully!"
EOF

chmod +x renew_ssl.sh

# Add to crontab for automatic renewal
echo "⏰ Setting up automatic renewal (every 12 hours)..."
(crontab -l 2>/dev/null; echo "0 */12 * * * cd $(pwd) && ./renew_ssl.sh >> /var/log/ssl-renewal.log 2>&1") | crontab -

echo "✅ SSL setup completed!"
echo "🌐 Your site should now be available at: https://$DOMAIN"
echo "🔄 Certificates will be automatically renewed every 12 hours"
echo "📋 To manually renew certificates, run: ./renew_ssl.sh"
