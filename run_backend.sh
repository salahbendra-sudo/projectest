#!/bin/bash

# Excel-to-App Backend Launcher
# Securely launches backend services with required API keys

# Configuration - Set these before running!
export OPENROUTER_API_KEY="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"    # Replace with your actual key
export NGROK_AUTH_TOKEN="2T27eEoOZq7QfHh4CEtqeeHY63E_2Aqe8KahGi2PQFEMkj6a4"         # Replace with your actual token
UNIFIED_API_PORT=8000
DEPLOY_API_PORT=8001

# Security check - Verify keys are set
if [ -z "$OPENROUTER_API_KEY" ] || [ "$OPENROUTER_API_KEY" = "your_openrouter_key_here" ]; then
    echo "❌ ERROR: OPENROUTER_API_KEY not properly configured"
    exit 1
fi

if [ -z "$NGROK_AUTH_TOKEN" ] || [ "$NGROK_AUTH_TOKEN" = "your_ngrok_token_here" ]; then
    echo "❌ ERROR: NGROK_AUTH_TOKEN not properly configured"
    exit 1
fi

# Service directories
LOG_DIR="./logs"
PID_DIR="./pids"
mkdir -p "$LOG_DIR" "$PID_DIR"

# Function to start service with environment variables
start_service() {
    local service_name=$1
    local port=$2
    local script=$3
    
    echo "🚀 Starting $service_name on port $port..."
    
    # Run with environment variables and log output
    python "$script" > "$LOG_DIR/${service_name}.log" 2>&1 &
    local pid=$!
    
    echo $pid > "$PID_DIR/${service_name}.pid"
    
    # Verify service started
    sleep 3
    if ! lsof -i :$port > /dev/null; then
        echo "❌ Failed to start $service_name"
        echo "Check logs: $LOG_DIR/${service_name}.log"
        return 1
    fi
    
    echo "✅ $service_name running (PID: $pid)"
    return 0
}

# Cleanup function
cleanup() {
    echo ""
    echo "🔴 Shutting down services..."
    for service in "unified_api" "deploy_streamlit_api"; do
        pid_file="$PID_DIR/${service}.pid"
        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            kill -9 "$pid" 2>/dev/null && rm "$pid_file"
            echo "   Stopped $service (PID: $pid)"
        fi
    done
    exit 0
}

# Trap signals for clean shutdown
trap cleanup SIGINT SIGTERM

# Main execution
echo ""
echo "📡 Excel-to-App Backend System"
echo "   OPENROUTER_API_KEY: ${OPENROUTER_API_KEY:0:4}...${OPENROUTER_API_KEY: -4}"
echo "   NGROK_AUTH_TOKEN: ${NGROK_AUTH_TOKEN:0:4}...${NGROK_AUTH_TOKEN: -4}"
echo ""

# Start services
if ! start_service "unified_api" $UNIFIED_API_PORT "unified_api.py"; then
    cleanup
    exit 1
fi

if ! start_service "deploy_streamlit_api" $DEPLOY_API_PORT "deploy_streamlit_api.py"; then
    cleanup
    exit 1
fi

echo ""
echo "🌐 Services Running:"
echo "   - Unified API: http://localhost:$UNIFIED_API_PORT"
echo "   - Deployment API: http://localhost:$DEPLOY_API_PORT"
echo ""
echo "📋 Logs: tail -f $LOG_DIR/{unified_api,deploy_streamlit_api}.log"
echo "🛑 Press Ctrl+C to shutdown"

# Continuous monitoring
while true; do
    sleep 60
    # Optional: Add health checks here
done
