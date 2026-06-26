#!/bin/bash
# Streamlit Service Manager
# Manages starting, stopping, and restarting the Excel Master Exporter

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_NAME="Excel Master Exporter"
APP_FILE="$SCRIPT_DIR/app.py"
PORT=${PORT:-8501}
HOST=${HOST:-0.0.0.0}
LOG_FILE="$SCRIPT_DIR/streamlit.log"
PID_FILE="$SCRIPT_DIR/streamlit.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

echo_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

echo_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if app file exists
check_app() {
    if [ ! -f "$APP_FILE" ]; then
        echo_error "App file not found: $APP_FILE"
        exit 1
    fi
}

# Start Streamlit
start_service() {
    check_app
    
    if [ -f "$PID_FILE" ]; then
        pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo_warning "$APP_NAME is already running (PID: $pid)"
            return 0
        fi
    fi
    
    echo_info "Starting $APP_NAME..."
    
    # Start Streamlit in background with logging
    nohup streamlit run "$APP_FILE" \
        --server.port="$PORT" \
        --server.address="$HOST" \
        --server.headless=true \
        --logger.level=info \
        > "$LOG_FILE" 2>&1 &
    
    echo $! > "$PID_FILE"
    
    sleep 2
    
    if [ -f "$PID_FILE" ]; then
        pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo_success "$APP_NAME started successfully (PID: $pid)"
            echo_info "Running on http://$HOST:$PORT"
            echo_info "Logs: $LOG_FILE"
            return 0
        fi
    fi
    
    echo_error "Failed to start $APP_NAME"
    return 1
}

# Stop Streamlit
stop_service() {
    if [ ! -f "$PID_FILE" ]; then
        echo_warning "$APP_NAME is not running"
        return 0
    fi
    
    pid=$(cat "$PID_FILE")
    
    if ! kill -0 "$pid" 2>/dev/null; then
        echo_warning "Process $pid not found"
        rm -f "$PID_FILE"
        return 0
    fi
    
    echo_info "Stopping $APP_NAME (PID: $pid)..."
    
    # Try graceful shutdown first
    kill -TERM "$pid" 2>/dev/null || true
    
    # Wait up to 10 seconds
    count=0
    while [ $count -lt 10 ]; do
        if ! kill -0 "$pid" 2>/dev/null; then
            break
        fi
        sleep 1
        count=$((count + 1))
    done
    
    # Force kill if necessary
    if kill -0 "$pid" 2>/dev/null; then
        echo_warning "Force killing process..."
        kill -9 "$pid" 2>/dev/null || true
    fi
    
    rm -f "$PID_FILE"
    echo_success "$APP_NAME stopped"
    return 0
}

# Restart Streamlit
restart_service() {
    echo_info "Restarting $APP_NAME..."
    stop_service
    sleep 2
    start_service
}

# Get status
status_service() {
    if [ ! -f "$PID_FILE" ]; then
        echo_warning "$APP_NAME is not running"
        return 1
    fi
    
    pid=$(cat "$PID_FILE")
    
    if kill -0 "$pid" 2>/dev/null; then
        echo_success "$APP_NAME is running (PID: $pid)"
        echo_info "Port: $PORT"
        echo_info "URL: http://$HOST:$PORT"
        return 0
    else
        echo_error "$APP_NAME is not running (stale PID: $pid)"
        rm -f "$PID_FILE"
        return 1
    fi
}

# View logs
view_logs() {
    if [ ! -f "$LOG_FILE" ]; then
        echo_warning "Log file not found: $LOG_FILE"
        return 1
    fi
    
    echo_info "Displaying logs (last 50 lines)..."
    tail -50 "$LOG_FILE"
}

# Follow logs
follow_logs() {
    if [ ! -f "$LOG_FILE" ]; then
        echo_warning "Log file not found: $LOG_FILE"
        return 1
    fi
    
    echo_info "Following logs (Ctrl+C to exit)..."
    tail -f "$LOG_FILE"
}

# Main command handler
case "${1:-status}" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        status_service
        ;;
    logs)
        view_logs
        ;;
    follow)
        follow_logs
        ;;
    *)
        echo_info "$APP_NAME Service Manager"
        echo ""
        echo "Usage: $0 {start|stop|restart|status|logs|follow}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the service"
        echo "  stop    - Stop the service"
        echo "  restart - Restart the service"
        echo "  status  - Show service status"
        echo "  logs    - View service logs (last 50 lines)"
        echo "  follow  - Follow service logs in real-time"
        echo ""
        exit 1
        ;;
esac

exit $?
