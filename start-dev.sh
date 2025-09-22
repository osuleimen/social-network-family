#!/bin/bash

# Social Network Family - Development Startup Script

echo "🚀 Starting Social Network Family in development mode..."

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install it first."
    exit 1
fi

# Check if .env file exists
if [ ! -f "docker.env" ]; then
    echo "⚠️  docker.env file not found. Creating from example..."
    if [ -f "docker.env.example" ]; then
        cp docker.env.example docker.env
        echo "✅ Created docker.env from example. Please edit it with your settings."
    else
        echo "❌ docker.env.example not found. Please create docker.env manually."
        exit 1
    fi
fi

# Create uploads directory
mkdir -p backend/uploads

# Start services
echo "🐳 Starting Docker containers..."
docker-compose -f docker-compose.dev.yml up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
docker-compose -f docker-compose.dev.yml ps

echo ""
echo "✅ Social Network Family is starting up!"
echo ""
echo "📱 Frontend: http://localhost:3001"
echo "🔧 Backend API: http://localhost:5001"
echo "🗄️  PostgreSQL: localhost:5433"
echo "📦 Redis: localhost:6380"
echo ""
echo "📋 Useful commands:"
echo "  View logs: docker-compose -f docker-compose.dev.yml logs -f"
echo "  Stop services: docker-compose -f docker-compose.dev.yml down"
echo "  Restart: docker-compose -f docker-compose.dev.yml restart"
echo ""
echo "🌐 Open http://localhost:3001 in your browser to start using the app!"
