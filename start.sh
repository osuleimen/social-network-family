#!/bin/bash

# Social Network Startup Script
# This script sets up and starts the social network application

set -e

echo "🚀 Starting Social Network Application..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists, if not generate it
if [ ! -f .env ]; then
    echo "📝 .env file not found. Generating secure secrets..."
    if command -v python3 &> /dev/null; then
        python3 generate_secrets.py
    else
        echo "❌ Python3 not found. Please install Python3 or copy env.example to .env and update values."
        exit 1
    fi
fi

# Load environment variables
source .env

# Check if domain is set
if [ -z "$DOMAIN" ]; then
    echo "⚠️  DOMAIN not set in .env file. Using localhost..."
    export DOMAIN=localhost
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p certbot/conf
mkdir -p certbot/www
mkdir -p ssl

# Build and start services
echo "🔨 Building and starting services..."
docker-compose build

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check if SSL setup is needed
if [ "$DOMAIN" != "localhost" ]; then
    echo "🔒 Checking SSL certificate..."
    if [ ! -f "certbot/conf/live/$DOMAIN/fullchain.pem" ]; then
        echo "🔐 SSL certificate not found. Setting up SSL..."
        chmod +x setup_ssl.sh
        ./setup_ssl.sh
    else
        echo "✅ SSL certificate already exists."
    fi
fi

# Show status
echo "📊 Service status:"
docker-compose ps

echo ""
echo "🎉 Social Network is now running!"
echo ""
echo "🌐 Frontend: http://$DOMAIN"
echo "🔗 API: http://$DOMAIN/api"
echo ""
echo "📋 Useful commands:"
echo "  View logs: docker-compose logs -f"
echo "  Stop services: docker-compose down"
echo "  Restart services: docker-compose restart"
echo "  Update services: docker-compose pull && docker-compose up -d"
echo ""
echo "🔒 SSL certificate will be automatically renewed every 12 hours"
echo "📧 Make sure to update email settings in .env file!"
