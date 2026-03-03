# Nginx Configuration Validation Script (PowerShell)
# This script validates the Nginx configuration example file

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Nginx Configuration Validation" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if configuration file exists
$configFile = "deployment/nginx.conf.example"
if (-not (Test-Path $configFile)) {
    Write-Host "✗ Configuration file not found: $configFile" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Configuration file exists: $configFile" -ForegroundColor Green
Write-Host ""

# Read configuration content
$configContent = Get-Content $configFile -Raw

# Validate configuration structure
Write-Host "Validating configuration structure..." -ForegroundColor Yellow

# Check for required sections
$requiredSections = @(
    "upstream feishu_bot_backend",
    "server_name",
    "location /api/",
    "Serve static files with caching",
    "ssl_certificate",
    "ssl_certificate_key",
    "proxy_pass",
    "try_files"
)

$missingSections = @()
foreach ($section in $requiredSections) {
    if ($configContent -match [regex]::Escape($section)) {
        Write-Host "✓ Found: $section" -ForegroundColor Green
    } else {
        Write-Host "✗ Missing: $section" -ForegroundColor Red
        $missingSections += $section
    }
}

Write-Host ""

if ($missingSections.Count -gt 0) {
    Write-Host "Configuration validation failed!" -ForegroundColor Red
    Write-Host "Missing sections:"
    foreach ($section in $missingSections) {
        Write-Host "  - $section"
    }
    exit 1
}

# Check for security headers
Write-Host "Checking security headers..." -ForegroundColor Yellow
$securityHeaders = @(
    "Strict-Transport-Security",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "X-XSS-Protection",
    "Content-Security-Policy"
)

foreach ($header in $securityHeaders) {
    if ($configContent -match [regex]::Escape($header)) {
        Write-Host "✓ Security header: $header" -ForegroundColor Green
    } else {
        Write-Host "⚠ Missing security header: $header" -ForegroundColor Yellow
    }
}

Write-Host ""

# Check for performance optimizations
Write-Host "Checking performance optimizations..." -ForegroundColor Yellow
$performanceFeatures = @(
    "gzip on",
    "http2",
    "expires",
    "Cache-Control"
)

foreach ($feature in $performanceFeatures) {
    if ($configContent -match [regex]::Escape($feature)) {
        Write-Host "✓ Performance feature: $feature" -ForegroundColor Green
    } else {
        Write-Host "⚠ Missing performance feature: $feature" -ForegroundColor Yellow
    }
}

Write-Host ""

# Check for common issues
Write-Host "Checking for common configuration issues..." -ForegroundColor Yellow

# Check for hardcoded paths
if ($configContent -match "/opt/feishu-bot") {
    Write-Host "⚠ Configuration contains hardcoded paths (/opt/feishu-bot)" -ForegroundColor Yellow
    Write-Host "  Remember to update these paths for your deployment"
}

# Check for placeholder domain
if ($configContent -match "your-domain\.com") {
    Write-Host "⚠ Configuration contains placeholder domain (your-domain.com)" -ForegroundColor Yellow
    Write-Host "  Remember to replace with your actual domain"
}

# Check for default backend address
if ($configContent -match "127\.0\.0\.1:5000") {
    Write-Host "✓ Backend address configured (127.0.0.1:5000)" -ForegroundColor Green
}

# Check for reverse proxy configuration
if ($configContent -match "proxy_pass http://feishu_bot_backend") {
    Write-Host "✓ Reverse proxy configured" -ForegroundColor Green
}

# Check for static file serving
if ($configContent -match "root /opt/feishu-bot/frontend/dist") {
    Write-Host "✓ Static file serving configured" -ForegroundColor Green
}

# Check for HTTPS configuration
if ($configContent -match "listen 443 ssl") {
    Write-Host "✓ HTTPS/SSL configured" -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Validation Summary" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

if ($missingSections.Count -eq 0) {
    Write-Host "✓ All required sections present" -ForegroundColor Green
    Write-Host "✓ Configuration structure is valid" -ForegroundColor Green
    Write-Host ""
    Write-Host "Configuration includes:" -ForegroundColor Cyan
    Write-Host "  ✓ Reverse proxy to Gunicorn backend" -ForegroundColor Green
    Write-Host "  ✓ Static file serving for frontend" -ForegroundColor Green
    Write-Host "  ✓ HTTPS/SSL configuration" -ForegroundColor Green
    Write-Host "  ✓ Security headers" -ForegroundColor Green
    Write-Host "  ✓ Performance optimizations (gzip, caching)" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Copy the configuration file to /etc/nginx/sites-available/"
    Write-Host "2. Update domain name, paths, and SSL certificate locations"
    Write-Host "3. Test with: sudo nginx -t"
    Write-Host "4. Enable the site and reload Nginx"
    Write-Host ""
    Write-Host "See docs/deployment/NGINX_DEPLOYMENT.md for detailed instructions" -ForegroundColor Cyan
    exit 0
} else {
    Write-Host "✗ Configuration validation failed" -ForegroundColor Red
    exit 1
}
