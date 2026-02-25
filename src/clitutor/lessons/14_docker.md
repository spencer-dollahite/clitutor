# Docker Basics

**Docker** packages applications and their dependencies into standardized units
called **containers**. Containers are lightweight, portable, and isolated --
they run the same way on any machine with Docker installed. This is the
foundation of modern DevOps and cloud-native development.

## Containers vs Virtual Machines

| Feature | Container | Virtual Machine |
|---------|-----------|----------------|
| Boot time | Seconds | Minutes |
| Size | Megabytes | Gigabytes |
| Isolation | Process-level | Hardware-level |
| OS | Shares host kernel | Full OS per VM |
| Performance | Near-native | Overhead from hypervisor |

Containers share the host OS kernel, making them much lighter than VMs.

## Core Concepts

- **Image** -- a read-only template with your app and its dependencies
- **Container** -- a running instance of an image
- **Dockerfile** -- instructions to build an image
- **Registry** -- a repository of images (Docker Hub is the default)

---

## Basic Docker Commands

```bash
docker --version                 # verify Docker is installed
docker pull ubuntu               # download an image
docker images                    # list downloaded images
docker run ubuntu echo "hello"   # run a command in a container
docker ps                        # list running containers
docker ps -a                     # list ALL containers (including stopped)
docker stop <container_id>       # stop a running container
docker rm <container_id>         # remove a stopped container
docker rmi <image_id>            # remove an image
```

<!-- exercise
id: ex01
title: Check Docker version
xp: 10
difficulty: 2
sandbox_setup: null
validation_type: output_contains
expected: Docker
hints:
  - "Use the docker command with a version flag."
  - "The flag is --version."
  - "Type: `docker --version 2>/dev/null || echo 'Docker not installed'`"
-->
### Exercise 1: Check Docker version
Check if Docker is installed and display its version.

---

## Running Containers

```bash
# Run interactively with a shell
docker run -it ubuntu /bin/bash

# Run in the background (detached)
docker run -d nginx

# Run with a name
docker run -d --name my-nginx nginx

# Run with port mapping (host:container)
docker run -d -p 8080:80 nginx

# Run with environment variables
docker run -d -e MYSQL_ROOT_PASSWORD=secret mysql

# Run with a volume mount
docker run -d -v /host/path:/container/path nginx
```

### Important Flags

| Flag | Purpose |
|------|---------|
| `-it` | Interactive terminal (for shells) |
| `-d` | Detached (background) |
| `--name` | Give the container a name |
| `-p` | Port mapping (host:container) |
| `-e` | Set environment variable |
| `-v` | Mount a volume (host:container) |
| `--rm` | Remove container when it stops |

<!-- exercise
id: ex02
title: Write a docker run command
xp: 15
difficulty: 3
sandbox_setup: null
validation_type: file_contains
expected: docker_commands.txt::docker run -d -p 8080:80
hints:
  - "Write a docker run command to a file for reference."
  - "Include detached mode and port mapping."
  - "Type: `echo 'docker run -d -p 8080:80 --name webserver nginx' > docker_commands.txt`"
-->
### Exercise 2: Write a docker run command
Write a docker run command to `docker_commands.txt` that runs nginx in detached mode with port 8080 mapped to container port 80.

---

## Dockerfiles

A **Dockerfile** contains instructions to build a custom image:

```dockerfile
# Use an official base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port
EXPOSE 5000

# Default command
CMD ["python", "app.py"]
```

### Building an Image

```bash
docker build -t myapp:1.0 .           # build from current directory
docker build -t myapp:latest -f Dockerfile.dev .  # specify Dockerfile
```

### Common Dockerfile Instructions

| Instruction | Purpose |
|------------|---------|
| `FROM` | Base image |
| `RUN` | Execute a command during build |
| `COPY` | Copy files from host to image |
| `ADD` | Copy files (supports URLs and tar extraction) |
| `WORKDIR` | Set the working directory |
| `ENV` | Set environment variables |
| `EXPOSE` | Document the port the app uses |
| `CMD` | Default command when container starts |
| `ENTRYPOINT` | Command that always runs (CMD becomes arguments) |

<!-- exercise
id: ex03
title: Write a Dockerfile
xp: 25
difficulty: 3
sandbox_setup: null
validation_type: file_contains
expected: Dockerfile::FROM
hints:
  - "Create a Dockerfile with at least FROM, WORKDIR, and CMD instructions."
  - "Start with a base image like alpine or ubuntu."
  - "Type: `printf 'FROM alpine:latest\\nWORKDIR /app\\nCOPY . .\\nCMD [\"echo\", \"Hello from Docker\"]\\n' > Dockerfile`"
-->
### Exercise 3: Write a Dockerfile
Create a Dockerfile that uses `alpine:latest` as a base, sets `/app` as the working directory, copies files, and runs an echo command.

---

## Docker Compose

**Docker Compose** lets you define multi-container applications in a YAML file:

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    image: nginx
    ports:
      - "8080:80"
    volumes:
      - ./html:/usr/share/nginx/html

  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: myapp
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

```bash
docker compose up -d           # start all services
docker compose down            # stop and remove
docker compose ps              # list running services
docker compose logs            # view logs
docker compose exec web bash   # shell into a running service
```

<!-- exercise
id: ex04
title: Write a docker-compose file
xp: 25
difficulty: 4
sandbox_setup: null
validation_type: file_contains
expected: "docker-compose.yml::services:"
hints:
  - "Create a docker-compose.yml with a service definition."
  - "Use YAML format with version and services sections."
  - "Type: `printf 'version: \"3.8\"\\nservices:\\n  web:\\n    image: nginx\\n    ports:\\n      - \"8080:80\"\\n' > docker-compose.yml`"
-->
### Exercise 4: Write a docker-compose file
Create a `docker-compose.yml` with a web service running nginx on port 8080.

---

## Volumes and Data Persistence

Containers are **ephemeral** -- when removed, their data is lost. Volumes
persist data:

```bash
# Named volume
docker volume create mydata
docker run -v mydata:/app/data myapp

# Bind mount (host directory)
docker run -v /host/path:/container/path myapp

# List volumes
docker volume ls

# Remove a volume
docker volume rm mydata
```

<!-- exercise
id: ex05
title: Document volume usage
xp: 15
difficulty: 3
sandbox_setup: null
validation_type: file_contains
expected: volume_notes.txt::docker volume
hints:
  - "Write docker volume commands to a reference file."
  - "Include volume create and volume ls commands."
  - "Type: `printf 'docker volume create mydata\\ndocker volume ls\\ndocker run -v mydata:/data alpine\\n' > volume_notes.txt`"
-->
### Exercise 5: Document volume usage
Create `volume_notes.txt` with example docker volume commands.

---

## Useful Docker Commands

```bash
# View container logs
docker logs <container_id>
docker logs -f <container_id>     # follow (tail -f style)

# Execute a command in a running container
docker exec -it <container> bash

# Copy files to/from container
docker cp file.txt container:/path/
docker cp container:/path/file.txt ./

# Inspect container details
docker inspect <container>

# Resource usage
docker stats

# Clean up everything
docker system prune               # remove stopped containers, unused images
docker system prune -a            # remove ALL unused images
```

<!-- exercise
id: ex06
title: Create a .dockerignore
xp: 15
difficulty: 3
sandbox_setup: null
validation_type: file_contains
expected: .dockerignore::node_modules
hints:
  - "Create a .dockerignore file listing patterns to exclude from builds."
  - "Similar to .gitignore, list directories and files to exclude."
  - "Type: `printf 'node_modules\\n.git\\n*.log\\n.env\\n__pycache__\\n' > .dockerignore`"
-->
### Exercise 6: Create a .dockerignore
Create a `.dockerignore` file that excludes `node_modules`, `.git`, `*.log`, `.env`, and `__pycache__`.

---

## What You Learned

- **Docker basics** -- images, containers, registries
- **`docker run`** -- flags for interactive, detached, ports, volumes, env vars
- **Dockerfiles** -- building custom images with FROM, RUN, COPY, CMD
- **Docker Compose** -- multi-container apps with YAML configuration
- **Volumes** -- persisting data beyond container lifecycle
- **Maintenance** -- logs, exec, inspect, prune
