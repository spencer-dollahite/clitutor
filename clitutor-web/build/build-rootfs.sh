#!/usr/bin/env bash
#
# Build Alpine Linux rootfs for v86 using the official 9p filesystem approach.
#
# Produces:
#   public/v86/alpine-fs.json           (filesystem manifest)
#   public/v86/alpine-rootfs-flat/      (content-addressed files)
#   public/v86/seabios.bin              (BIOS)
#   public/v86/vgabios.bin              (VGA BIOS)
#
# Requirements: Docker, Python 3
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CLITUTOR_ROOT="$(dirname "$PROJECT_DIR")"
OUTPUT_DIR="$PROJECT_DIR/public/v86"
LESSONS_SRC="$CLITUTOR_ROOT/src/clitutor/lessons"

echo "==> CLItutor: Building Alpine rootfs for v86"
mkdir -p "$OUTPUT_DIR/alpine-rootfs-flat"

# ── Step 0: Clone v86 tools if needed ────────────────────────────
V86_TOOLS="$PROJECT_DIR/.v86-tools"
if [ ! -d "$V86_TOOLS" ]; then
    echo "==> Cloning v86 tools (fs2json, copy-to-sha256)..."
    git clone --depth 1 --filter=blob:none --sparse \
        https://github.com/copy/v86.git "$V86_TOOLS"
    cd "$V86_TOOLS"
    git sparse-checkout set tools bios
    cd "$PROJECT_DIR"
fi

# ── Step 1: Build i386 Alpine rootfs in Docker ───────────────────
echo "==> Building Alpine rootfs Docker image..."

# Stage lesson files into a build context directory
BUILD_CTX=$(mktemp -d)
mkdir -p "$BUILD_CTX/lessons"
cp "$LESSONS_SRC"/*.md "$BUILD_CTX/lessons/" 2>/dev/null || true
cp "$LESSONS_SRC"/metadata.json "$BUILD_CTX/lessons/" 2>/dev/null || true

# Stage rootfs overlay (realistic filesystem content)
if [ -d "$SCRIPT_DIR/rootfs-overlay" ]; then
    cp -r "$SCRIPT_DIR/rootfs-overlay" "$BUILD_CTX/rootfs-overlay"
fi

cat > "$BUILD_CTX/Dockerfile" <<'DOCKERFILE'
FROM docker.io/i386/alpine:3.21

ENV KERNEL=virt

# Core CLI tutorial tools
RUN apk add --no-cache \
    bash coreutils grep sed gawk findutils diffutils \
    less file tree curl wget \
    git vim tmux \
    openssh openssh-keygen \
    net-tools iproute2 iputils bind-tools \
    nginx nmap nmap-scripts tcpdump iptables jq sqlite \
    procps util-linux shadow \
    tar gzip bzip2 xz \
    man-pages mandoc \
    ncurses readline bash-completion \
    openrc alpine-base agetty alpine-conf \
    linux-$KERNEL linux-firmware-none

# Auto-login on serial console (ttyS0) and delete root password
RUN sed -i 's/getty 38400 tty1/agetty --autologin root tty1 linux/' /etc/inittab && \
    echo 'ttyS0::respawn:/sbin/agetty --autologin root -s ttyS0 115200 vt100' >> /etc/inittab && \
    passwd -d root

# Hostname
RUN setup-hostname clitutor

# ── Student user for SSH exercises ────────────────────────────
RUN adduser -D -s /bin/bash student && echo "student:student" | chpasswd

# ── Network interfaces (needed for OpenRC networking → nginx) ──
RUN printf 'auto lo\niface lo inet loopback\n' > /etc/network/interfaces

# ── SSH server config ─────────────────────────────────────────
RUN ssh-keygen -A && \
    echo "StrictModes no" >> /etc/ssh/sshd_config
# StrictModes off because main session runs as root in /home/student;
# ownership won't match the student user. This is a sandbox, not production.

# Minimal OpenRC services for fast boot
RUN for i in devfs dmesg mdev hwdrivers; do rc-update add $i sysinit; done && \
    for i in hwclock modules sysctl hostname syslog bootmisc networking; do rc-update add $i boot; done && \
    rc-update add killprocs shutdown && \
    rc-update add sshd default && \
    rc-update add nginx default

# Set bash as default shell (must happen before initramfs generation)
# Alpine 3.21 uses /bin/sh; older versions use /bin/ash — replace both
RUN sed -i '/^root:/s|/bin/sh$|/bin/bash|' /etc/passwd && \
    sed -i '/^root:/s|/bin/ash$|/bin/bash|' /etc/passwd

# Generate initramfs with 9p + virtio support
RUN mkinitfs -F "base virtio 9p" $(cat /usr/share/kernel/$KERNEL/kernel.release)

# Copy lesson files into the rootfs
COPY lessons/ /root/lessons/

# Copy realistic filesystem content (logs, projects, data, scripts)
COPY rootfs-overlay/ /

# Fix ownership and permissions for overlay content
RUN chown -R 1000:1000 /home/student && \
    chmod 700 /home/student/.ssh && \
    chmod +x /usr/local/bin/*.sh && \
    chmod +x /home/student/projects/scripts/*.sh && \
    chmod +x /home/student/projects/fleet-monitor/monitor.py && \
    chmod +x /home/student/projects/fleet-monitor/parse_logs.py && \
    mkdir -p /home/student/data/.raw && \
    head -c 256 /dev/urandom > /home/student/data/.raw/sample.bin && \
    chown -R 1000:1000 /home/student/data/.raw

# Clean up
RUN rm -rf /var/cache/apk/* /tmp/* /var/tmp/*
DOCKERFILE

docker build --platform linux/386 -t clitutor-v86-rootfs "$BUILD_CTX"
rm -rf "$BUILD_CTX"

# ── Step 2: Export rootfs as tar ─────────────────────────────────
echo "==> Exporting rootfs..."
CONTAINER_ID=$(docker create --platform linux/386 clitutor-v86-rootfs)
docker export "$CONTAINER_ID" -o /tmp/clitutor-rootfs.tar
docker rm "$CONTAINER_ID" > /dev/null

# Remove Docker artifact
tar -f /tmp/clitutor-rootfs.tar --delete ".dockerenv" 2>/dev/null || true

# Inject /etc/resolv.conf (can't write during Docker build — bind-mounted)
RESOLV_TMP=$(mktemp -d)
mkdir -p "$RESOLV_TMP/etc"
printf 'nameserver 8.8.8.8\nnameserver 8.8.4.4\n' > "$RESOLV_TMP/etc/resolv.conf"
tar -f /tmp/clitutor-rootfs.tar --delete "etc/resolv.conf" 2>/dev/null || true
tar -rf /tmp/clitutor-rootfs.tar -C "$RESOLV_TMP" etc/resolv.conf
rm -rf "$RESOLV_TMP"

# ── Step 3: Generate fs.json manifest ────────────────────────────
echo "==> Generating fs.json manifest..."
python3 "$V86_TOOLS/tools/fs2json.py" \
    --out "$OUTPUT_DIR/alpine-fs.json" \
    /tmp/clitutor-rootfs.tar

# ── Step 4: Create flat content-addressed file directory ─────────
echo "==> Creating flat file directory..."
python3 "$V86_TOOLS/tools/copy-to-sha256.py" \
    /tmp/clitutor-rootfs.tar \
    "$OUTPUT_DIR/alpine-rootfs-flat"

# ── Step 5: Copy BIOS files ─────────────────────────────────────
echo "==> Copying BIOS files..."
for bios in seabios.bin vgabios.bin; do
    if [ -f "$V86_TOOLS/bios/$bios" ]; then
        cp "$V86_TOOLS/bios/$bios" "$OUTPUT_DIR/$bios"
    else
        echo "  WARNING: $bios not found in v86 tools"
    fi
done

# ── Step 6: Copy v86 WASM + JS from node_modules ────────────────
echo "==> Copying v86 runtime..."
for f in v86.wasm libv86.js; do
    src="$PROJECT_DIR/node_modules/v86/build/$f"
    if [ -f "$src" ]; then
        cp "$src" "$OUTPUT_DIR/$f"
        echo "  Copied $f"
    fi
done

# ── Cleanup ──────────────────────────────────────────────────────
rm -f /tmp/clitutor-rootfs.tar

echo ""
echo "==> Build complete!"
echo "    Files in $OUTPUT_DIR:"
ls -lh "$OUTPUT_DIR/" 2>/dev/null || true
echo ""
echo "    Flat files: $(ls "$OUTPUT_DIR/alpine-rootfs-flat/" 2>/dev/null | wc -l) content-addressed files"
echo ""
echo "Next steps:"
echo "  1. npm run dev       — Start dev server"
echo "  2. Open browser      — VM boots, you get a shell"
echo "  3. (Optional) npm run build-state — Generate state snapshot for instant boot"
