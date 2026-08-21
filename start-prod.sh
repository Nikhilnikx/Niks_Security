#!/bin/bash
set -e

echo "🚀 Starting Niksmind in Production Mode..."

# Build frontend for production
echo "🔨 Building frontend..."
cd frontend
npm run build
cd ..

# Start with docker-compose.prod.yml
echo "🐳 Starting Docker services..."
docker-compose -f docker-compose.prod.yml up -d --build

echo "⏳ Waiting for services..."
sleep 10

echo ""
echo "✅ Niksmind is running!"
echo "   Frontend: http://localhost"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "   Logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "   Stop: docker-compose -f docker-compose.prod.yml down"
