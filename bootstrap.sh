#!/usr/bin/env bash
# CLItutor bootstrap script
# Installs Python (if needed), creates a venv, installs deps, and launches the TUI.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
MIN_PYTHON="3.8"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${CYAN}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[OK]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
err()   { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# --- Find Python 3 ---
find_python() {
    for cmd in python3 python; do
        if command -v "$cmd" &>/dev/null; then
            if "$cmd" -c "import sys; assert sys.version_info >= (3, 8)" 2>/dev/null; then
                echo "$cmd"
                return 0
            fi
        fi
    done
    return 1
}

# --- Install Python if missing ---
install_python() {
    info "Python >= $MIN_PYTHON not found. Attempting to install..."

    if command -v apt-get &>/dev/null; then
        info "Using apt-get..."
        sudo apt-get update -qq && sudo apt-get install -y -qq python3 python3-venv python3-pip
    elif command -v dnf &>/dev/null; then
        info "Using dnf..."
        sudo dnf install -y python3 python3-pip
    elif command -v yum &>/dev/null; then
        info "Using yum..."
        sudo yum install -y python3 python3-pip
    elif command -v pacman &>/dev/null; then
        info "Using pacman..."
        sudo pacman -S --noconfirm python python-pip
    elif command -v brew &>/dev/null; then
        info "Using Homebrew..."
        brew install python@3
    else
        err "Cannot determine package manager. Please install Python >= $MIN_PYTHON manually."
        exit 1
    fi
}

# --- Main ---
echo ""
echo -e "${CYAN}  ╔═══════════════════════════════════════╗${NC}"
echo -e "${CYAN}  ║       CLItutor Bootstrap Script       ║${NC}"
echo -e "${CYAN}  ╚═══════════════════════════════════════╝${NC}"
echo ""

# 1. Find or install Python
PYTHON=$(find_python || true)

if [ -z "$PYTHON" ]; then
    install_python
    PYTHON=$(find_python || true)
    if [ -z "$PYTHON" ]; then
        err "Failed to install Python >= $MIN_PYTHON. Please install manually."
        exit 1
    fi
fi

PYVER=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
ok "Python $PYVER found at $(command -v "$PYTHON")"

# 2. Create virtual environment
if [ ! -d "$VENV_DIR" ]; then
    info "Creating virtual environment..."
    "$PYTHON" -m venv "$VENV_DIR"
    ok "Virtual environment created at $VENV_DIR"
else
    ok "Virtual environment already exists"
fi

# 3. Activate venv and install
info "Installing CLItutor and dependencies..."
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet -e "$SCRIPT_DIR"
ok "CLItutor installed successfully"

# 4. Launch
echo ""
echo -e "${GREEN}  Ready! Launching CLItutor...${NC}"
echo -e "  (You can also run it later with: ${CYAN}$VENV_DIR/bin/clitutor${NC})"
echo ""

exec "$VENV_DIR/bin/python" -m clitutor
