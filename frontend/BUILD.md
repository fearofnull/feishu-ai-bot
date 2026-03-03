# Frontend Build Guide

This document explains how to build the frontend for production and integrate it with the Flask backend.

## Build Configuration

The frontend is configured to build to `../feishu_bot/web_admin/static/` directory, which is where the Flask server expects to find the static files.

### Build Settings (vite.config.js)

- **Output Directory**: `../feishu_bot/web_admin/static/`
- **Clean Build**: The output directory is cleaned before each build
- **Code Splitting**: Vendor code is split into separate chunks for better caching
  - `vue-vendor`: Vue.js, Vue Router, Pinia
  - `element-plus`: Element Plus UI library
- **Minification**: Using esbuild for fast minification

## Building for Production

### Prerequisites

Make sure you have Node.js and npm installed:

```bash
node --version  # Should be v18 or higher
npm --version
```

### Install Dependencies

```bash
cd frontend
npm install
```

### Build

```bash
npm run build
```

This will:
1. Clean the output directory (`feishu_bot/web_admin/static/`)
2. Build the Vue.js application
3. Generate optimized and minified assets
4. Output all files to the static directory

### Build Output

After building, you should see:

```
feishu_bot/web_admin/static/
├── index.html
├── assets/
│   ├── index-[hash].css
│   ├── index-[hash].js
│   ├── vue-vendor-[hash].js
│   └── element-plus-[hash].js
└── vite.svg
```

## Backend Integration

The Flask server is configured to serve the static files automatically.

### Static File Serving

The `WebAdminServer` class in `feishu_bot/web_admin/server.py`:

1. **Default Static Folder**: If no static folder is specified, it defaults to `feishu_bot/web_admin/static/`
2. **SPA Routing**: All non-API routes fall back to `index.html` to support client-side routing
3. **API Routes**: API routes (`/api/*`) are handled separately and not affected by static file serving

### Starting the Server

```bash
# With built frontend
python -m feishu_bot.web_admin.server

# Or specify custom static folder
python -m feishu_bot.web_admin.server --static-folder /path/to/static
```

### SPA Routing

The server implements SPA (Single Page Application) routing fallback:

- **Static Files**: Files that exist in the static folder are served directly
  - Example: `/assets/index-abc123.js` → serves the JS file
- **SPA Routes**: Non-existent paths return `index.html` for client-side routing
  - Example: `/configs` → returns `index.html` (Vue Router handles the route)
  - Example: `/configs/session-123` → returns `index.html`
- **API Routes**: API routes are handled by Flask and not affected
  - Example: `/api/configs` → handled by Flask API

## Development vs Production

### Development Mode

In development, run frontend and backend separately:

```bash
# Terminal 1: Backend
python -m feishu_bot.web_admin.server

# Terminal 2: Frontend
cd frontend
npm run dev
```

The Vite dev server proxies API requests to the Flask backend.

### Production Mode

In production, build the frontend and run only the Flask server:

```bash
# Build frontend
cd frontend
npm run build

# Run Flask server (serves both API and static files)
cd ..
python -m feishu_bot.web_admin.server
```

## Deployment Checklist

Before deploying to production:

1. ✅ Build the frontend: `npm run build`
2. ✅ Verify static files exist in `feishu_bot/web_admin/static/`
3. ✅ Set environment variables:
   - `WEB_ADMIN_PASSWORD`: Admin password
   - `JWT_SECRET_KEY`: Secret key for JWT tokens
4. ✅ Test the server: `python -m feishu_bot.web_admin.server`
5. ✅ Access the web interface: `http://localhost:5000`

## Troubleshooting

### Build Fails

- Check Node.js version (should be v18+)
- Delete `node_modules` and `package-lock.json`, then run `npm install`
- Check for syntax errors in Vue components

### Static Files Not Found

- Verify the build completed successfully
- Check that files exist in `feishu_bot/web_admin/static/`
- Check Flask server logs for static folder path

### SPA Routes Return 404

- Verify the server is configured with the static folder
- Check that `index.html` exists in the static folder
- Ensure API routes don't conflict with SPA routes

### Assets Not Loading

- Check browser console for 404 errors
- Verify asset paths in `index.html` are correct
- Check that the `assets/` directory exists in the static folder

## Performance Optimization

The build is already optimized with:

- **Code Splitting**: Vendor code separated for better caching
- **Minification**: JavaScript and CSS are minified
- **Tree Shaking**: Unused code is removed
- **Asset Optimization**: Images and other assets are optimized

For further optimization:

- Enable gzip compression in your web server (Nginx, Apache)
- Set appropriate cache headers for static assets
- Use a CDN for static assets in production
- Enable HTTP/2 for better performance

## CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: Build Frontend
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - name: Install dependencies
        run: cd frontend && npm install
      - name: Build
        run: cd frontend && npm run build
      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: static-files
          path: feishu_bot/web_admin/static/
```
