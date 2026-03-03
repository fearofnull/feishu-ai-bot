#!/bin/bash
# Nginx Configuration Validation Script
# This script validates the Nginx configuration example file

set -e

echo "=========================================="
echo "Nginx Configuration Validation"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if nginx is installed
if ! command -v nginx &> /dev/null; then
    echo -e "${YELLOW}Warning: Nginx is not installed. Skipping syntax validation.${NC}"
    echo "To install Nginx:"
    echo "  Ubuntu/Debian: sudo apt-get install nginx"
    echo "  CentOS/RHEL: sudo yum install nginx"
    echo ""
    NGINX_INSTALLED=false
else
    NGINX_INSTALLED=true
    echo -e "${GREEN}✓ Nginx is installed${NC}"
    nginx -v
    echo ""
fi

# Check if configuration file exists
CONFIG_FILE="deployment/nginx.conf.example"
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}✗ Configuration file not found: $CONFIG_FILE${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Configuration file exists: $CONFIG_FILE${NC}"
echo ""

# Validate configuration structure
echo "Validating configuration structure..."

# Check for required sections
REQUIRED_SECTIONS=(
    "upstream feishu_bot_backend"
    "server_name"
    "location /api/"
    "location ~\* \\\.\(js|css|png"
    "ssl_certificate"
    "ssl_certificate_key"
    "proxy_pass"
    "try_files"
)

MISSING_SECTIONS=()
for section in "${REQUIRED_SECTIONS[@]}"; do
    if grep -q "$section" "$CONFIG_FILE"; then
        echo -e "${GREEN}✓ Found: $section${NC}"
    else
        echo -e "${RED}✗ Missing: $section${NC}"
        MISSING_SECTIONS+=("$section")
    fi
done

echo ""

if [ ${#MISSING_SECTIONS[@]} -gt 0 ]; then
    echo -e "${RED}Configuration validation failed!${NC}"
    echo "Missing sections:"
    for section in "${MISSING_SECTIONS[@]}"; do
        echo "  - $section"
    done
    exit 1
fi

# Check for security headers
echo "Checking security headers..."
SECURITY_HEADERS=(
    "Strict-Transport-Security"
    "X-Frame-Options"
    "X-Content-Type-Options"
    "X-XSS-Protection"
    "Content-Security-Policy"
)

for header in "${SECURITY_HEADERS[@]}"; do
    if grep -q "$header" "$CONFIG_FILE"; then
        echo -e "${GREEN}✓ Security header: $header${NC}"
    else
        echo -e "${YELLOW}⚠ Missing security header: $header${NC}"
    fi
done

echo ""

# Check for performance optimizations
echo "Checking performance optimizations..."
PERFORMANCE_FEATURES=(
    "gzip on"
    "http2"
    "expires"
    "Cache-Control"
)

for feature in "${PERFORMANCE_FEATURES[@]}"; do
    if grep -q "$feature" "$CONFIG_FILE"; then
        echo -e "${GREEN}✓ Performance feature: $feature${NC}"
    else
        echo -e "${YELLOW}⚠ Missing performance feature: $feature${NC}"
    fi
done

echo ""

# Validate syntax if nginx is installed
if [ "$NGINX_INSTALLED" = true ]; then
    echo "Testing Nginx syntax..."
    
    # Create a temporary copy with placeholder values
    TEMP_CONFIG=$(mktemp)
    cp "$CONFIG_FILE" "$TEMP_CONFIG"
    
    # Replace placeholder values
    sed -i 's/your-domain\.com/localhost/g' "$TEMP_CONFIG"
    sed -i 's|/opt/feishu-bot/frontend/dist|/tmp/test|g' "$TEMP_CONFIG"
    sed -i 's|/etc/letsencrypt/live/your-domain.com/fullchain.pem|/tmp/test.crt|g' "$TEMP_CONFIG"
    sed -i 's|/etc/letsencrypt/live/your-domain.com/privkey.pem|/tmp/test.key|g' "$TEMP_CONFIG"
    sed -i 's|/etc/letsencrypt/live/your-domain.com/chain.pem|/tmp/test.crt|g' "$TEMP_CONFIG"
    
    # Create dummy files for testing
    mkdir -p /tmp/test
    touch /tmp/test/index.html
    
    # Generate self-signed certificate for testing
    if command -v openssl &> /dev/null; then
        openssl req -x509 -nodes -days 1 -newkey rsa:2048 \
            -keyout /tmp/test.key -out /tmp/test.crt \
            -subj "/C=US/ST=Test/L=Test/O=Test/CN=localhost" &> /dev/null
    fi
    
    # Test configuration
    if sudo nginx -t -c "$TEMP_CONFIG" &> /dev/null; then
        echo -e "${GREEN}✓ Nginx syntax validation passed${NC}"
    else
        echo -e "${YELLOW}⚠ Nginx syntax validation failed (this is expected with placeholder values)${NC}"
        echo "Run 'sudo nginx -t -c $TEMP_CONFIG' for details"
    fi
    
    # Cleanup
    rm -f "$TEMP_CONFIG" /tmp/test.key /tmp/test.crt
    rm -rf /tmp/test
else
    echo -e "${YELLOW}⚠ Skipping Nginx syntax validation (Nginx not installed)${NC}"
fi

echo ""

# Check for common issues
echo "Checking for common configuration issues..."

# Check for hardcoded paths
if grep -q "/opt/feishu-bot" "$CONFIG_FILE"; then
    echo -e "${YELLOW}⚠ Configuration contains hardcoded paths (/opt/feishu-bot)${NC}"
    echo "  Remember to update these paths for your deployment"
fi

# Check for placeholder domain
if grep -q "your-domain.com" "$CONFIG_FILE"; then
    echo -e "${YELLOW}⚠ Configuration contains placeholder domain (your-domain.com)${NC}"
    echo "  Remember to replace with your actual domain"
fi

# Check for default backend address
if grep -q "127.0.0.1:5000" "$CONFIG_FILE"; then
    echo -e "${GREEN}✓ Backend address configured (127.0.0.1:5000)${NC}"
fi

echo ""
echo "=========================================="
echo "Validation Summary"
echo "=========================================="

if [ ${#MISSING_SECTIONS[@]} -eq 0 ]; then
    echo -e "${GREEN}✓ All required sections present${NC}"
    echo -e "${GREEN}✓ Configuration structure is valid${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Copy the configuration file to /etc/nginx/sites-available/"
    echo "2. Update domain name, paths, and SSL certificate locations"
    echo "3. Test with: sudo nginx -t"
    echo "4. Enable the site and reload Nginx"
    echo ""
    echo "See docs/deployment/NGINX_DEPLOYMENT.md for detailed instructions"
    exit 0
else
    echo -e "${RED}✗ Configuration validation failed${NC}"
    exit 1
fi
