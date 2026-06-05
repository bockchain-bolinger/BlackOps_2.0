FROM kalilinux/kali-rolling:latest

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    tor \
    aircrack-ng \
    cloudflared \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN python3 -m venv .venv
RUN .venv/bin/pip install --no-cache-dir -r requirements.txt

# Ensure root access for network tools
USER root

CMD ["/bin/bash"]
