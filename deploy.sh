#!/bin/bash
set -e

echo "🚀 Niksmind Production Deployment"
echo "=================================="

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed."
    exit 1
fi

# Check for .env.production
if [ ! -f .env.production ]; then
    echo "❌ .env.production not found."
    echo "   Copy .env.production.example to .env.production and configure it."
    exit 1
fi

# Load environment
export $(cat .env.production | grep -v '^#' | xargs)

echo ""
echo "📋 Configuration:"
echo "   Database: ${DB_PASSWORD:0:4}****"
echo "   Secret: ${SECRET_KEY:0:4}****"
echo "   Frontend URL: ${FRONTEND_URL:-not set}"
echo ""

# Build and start
echo "🔨 Building images..."
docker-compose -f docker-compose.prod.yml build

echo ""
echo "🗄️  Running database migrations..."
docker-compose -f docker-compose.prod.yml run --rm backend /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"

echo ""
echo "🌱 Seeding database..."
docker-compose -f docker-compose.prod.yml run --rm backend python3 seed.py

echo ""
echo "🚀 Starting services..."
docker-compose -f docker-compose.prod.yml up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Health check
if curl -sf http://localhost/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "⚠️  Backend health check failed - it may still be starting"
fi

echo ""
echo "=================================="
echo "✅ Deployment complete!"
echo ""
echo "🌐 Frontend: ${FRONTEND_URL:-http://localhost}"
echo "📋 API Docs: ${NEXT_PUBLIC_API_URL:-http://localhost}/docs"
echo ""
echo "📊 To check status: docker-compose -f docker-compose.prod.yml ps"
echo "📝 To view logs:    docker-compose -f docker-compose.prod.yml logs -f"
echo "🛑 To stop:         docker-compose -f docker-compose.prod.yml down"
echo "=================================="
