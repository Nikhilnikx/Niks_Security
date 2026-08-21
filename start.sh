#!/bin/bash
echo "🚀 Starting Niksmind..."

# Start PostgreSQL (if not running)
if ! docker ps | grep -q niksmind-db; then
  echo "📦 Starting PostgreSQL..."
  docker start niksmind-db 2>/dev/null || docker run -d --name niksmind-db \
    -e POSTGRES_DB=niksmind -e POSTGRES_USER=niksmind -e POSTGRES_PASSWORD=niksmind \
    -p 5432:5432 pgvector/pgvector:pg16
  sleep 3
fi
echo "✅ PostgreSQL running"

# Start Backend
if ! lsof -i :8000 >/dev/null 2>&1; then
  echo "🔧 Starting Backend..."
  cd "$(dirname "$0")/backend"
  /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
  sleep 3
fi
echo "✅ Backend running at http://localhost:8000"

# Start Frontend
if ! lsof -i :3000 >/dev/null 2>&1; then
  echo "🎨 Starting Frontend..."
  cd "$(dirname "$0")/frontend"
  npx next dev --port 3000 &
  sleep 5
fi
echo "✅ Frontend running at http://localhost:3000"

echo ""
echo "🌐 Open http://localhost:3000 in your browser"
echo "📋 API Docs: http://localhost:8000/docs"
echo "👤 Demo: demo@niksmind.com / demo123"
echo ""
echo "Press Ctrl+C to stop all services"

# Keep script running
wait
