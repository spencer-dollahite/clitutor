#!/usr/bin/env bash
#
# deploy.sh — Build clitutor-web and deploy to /var/www/clitutor
#
# Usage (on VPS):
#   ./deploy.sh              # build + copy to web root
#   ./deploy.sh /srv/web     # custom web root (deploys to /srv/web/clitutor/)
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WEB_ROOT="${1:-/var/www}"
DEPLOY_DIR="$WEB_ROOT/clitutor"

echo "==> Building clitutor-web..."
cd "$SCRIPT_DIR/clitutor-web"
npm ci --prefer-offline
npm run build

echo "==> Deploying to $DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR"
rsync -a --delete dist/ "$DEPLOY_DIR/"

echo "==> Done. Site deployed to $DEPLOY_DIR"
echo ""
echo "Nginx config needed (add to your server block):"
echo ""
cat <<'NGINX'
    # ── CLItutor ──────────────────────────────────────────────
    location /clitutor/ {
        alias /var/www/clitutor/;
        try_files $uri $uri/ /clitutor/index.html;

        # Required for SharedArrayBuffer (v86 WASM threads)
        add_header Cross-Origin-Opener-Policy  "same-origin" always;
        add_header Cross-Origin-Embedder-Policy "require-corp" always;
    }
NGINX
