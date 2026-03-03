#!/bin/bash
#
# Start Web Admin Interface with Gunicorn
#
# Usage:
#   ./scripts/start_web_admin.sh [development|production]
#
# Environment:
#   Mode can be set via MODE environment variable or first argument
#   Default: development

set -e

# Determine mode
MODE="${1:-${MODE:-development}}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo -e "${GREEN}Starting Web Admin Interface in ${MODE} mode...${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please create .env file from .env.example"
    exit 1
fi

# Load environment variables
set -a
source .env
set +a

# Check required environment variables
if [ -z "$WEB_ADMIN_PASSWORD" ]; then
    echo -e "${YELLOW}Warning: WEB_ADMIN_PASSWORD not set, using default${NC}"
fi

if [ -z "$JWT_SECRET_KEY" ]; then
    echo -e "${YELLOW}Warning: JWT_SECRET_KEY not set, using default${NC}"
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Start based on mode
case "$MODE" in
    development|dev)
        echo -e "${GREEN}Starting in development mode with Flask dev server...${NC}"
        python -m feishu_bot.web_admin.server \
            --host "${WEB_ADMIN_HOST:-0.0.0.0}" \
            --port "${WEB_ADMIN_PORT:-5000}" \
            --debug \
            --log-level DEBUG
        ;;
    
    production|prod)
        echo -e "${GREEN}Starting in production mode with Gunicorn...${NC}"
        
        # Check if gunicorn is installed
        if ! command -v gunicorn &> /dev/null; then
            echo -e "${RED}Error: Gunicorn not installed${NC}"
            echo "Install with: pip install gunicorn"
            exit 1
        fi
        
        # Start with Gunicorn
        exec gunicorn -c gunicorn.conf.py wsgi:app
        ;;
    
    *)
        echo -e "${RED}Error: Invalid mode '$MODE'${NC}"
        echo "Usage: $0 [development|production]"
        exit 1
        ;;
esac
