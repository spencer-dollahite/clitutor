FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    # Core
    bash coreutils findutils grep sed gawk \
    # Networking
    curl wget net-tools iputils-ping dnsutils iproute2 \
    # Dev tools
    git vim nano tmux build-essential python3 jq \
    # Other
    openssh-client tree file less man-db sudo tar gzip zip unzip \
    && rm -rf /var/lib/apt/lists/*

# Create non-root student user with passwordless sudo
RUN useradd -m -s /bin/bash student \
    && echo "student ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set up working directory
RUN mkdir -p /home/student/sandbox && chown student:student /home/student/sandbox

USER student
WORKDIR /home/student/sandbox

CMD ["sleep", "infinity"]
