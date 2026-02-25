#!/usr/bin/env bash
#
# deploy.sh — Build clitutor-web and deploy to /var/www/html/clitutor
#
# Usage (on VPS):
#   ./deploy.sh                        # build + copy to default path
#   ./deploy.sh /custom/path/clitutor  # custom deploy path
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEPLOY_DIR="${1:-/var/www/html/clitutor}"

echo "==> Building clitutor-web..."
cd "$SCRIPT_DIR/clitutor-web"
npm ci --prefer-offline
npm run build

echo "==> Deploying to $DEPLOY_DIR"
sudo mkdir -p "$DEPLOY_DIR"
sudo rsync -a --delete dist/ "$DEPLOY_DIR/"

echo "==> Done. Site deployed to $DEPLOY_DIR"
