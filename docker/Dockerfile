FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV HOSTNAME=clitutor

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

USER student
WORKDIR /home/student

CMD ["sleep", "infinity"]
