#!/bin/bash
echo "🛑 Stopping Niksmind..."

# Stop production services
docker-compose -f docker-compose.prod.yml down 2>/dev/null

# Stop development services
docker-compose down 2>/dev/null

# Stop launchctl services
launchctl unload /tmp/com.niksmind.frontend.plist 2>/dev/null
launchctl unload /tmp/com.niksmind.backend.plist 2>/dev/null

# Kill any remaining processes
pkill -f "uvicorn app.main" 2>/dev/null
pkill -f "next dev" 2>/dev/null
pkill -f "next start" 2>/dev/null

# Stop PostgreSQL container
docker stop niksmind-db 2>/dev/null

echo "✅ All services stopped"
