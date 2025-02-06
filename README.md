# Tetsuo Service Starter Kit 🚀

A scalable service-oriented architecture for building extension APIs for Tetsuo AI Core Services

## Overview

This repository provides a modular FastAPI service framework with support for Redis, WebSockets, and more. The instructions below cover setup on **Ubuntu** and **macOS** environments, as well as using Docker.  
**Note:** Use Python **3.11** (using pyenv on macOS is recommended) because Python 3.12 will fail.

## Architecture 🏗️

```
External World
│
└── FastAPI Service Layer  ←── Central Source of Truth
    │
    ├── Services
    │   ├── Your Service
    │
    └── Clients
        ├── Your Service Clients
```

## Technology Stack 💻

- **FastAPI**: Modern, fast web framework for building APIs
- **Redis**: In-memory data store for caching and real-time data
- **WebSockets**: Real-time bidirectional communication
- **Pydantic**: Data validation using Python type annotations
- **Loguru**: Python logging made simple

## Prerequisites 📋

- **Python 3.11+**  
  _Important: Use Python 3.11; Python 3.12 will fail. (On macOS, consider using [pyenv](https://github.com/pyenv/pyenv) with `pyenv local 3.11`.)_

- **Redis Server**

  - **Ubuntu:** Redis is installed via `apt-get` in the setup script.
  - **macOS:** Install via Homebrew:  
    ```bash
    brew install redis
    ```

## Installation 🛠️

### Ubuntu/WSL Setup

These instructions are for Ubuntu (or a Ubuntu VM) or Ubuntu WSL.[^1]

[^1]: **WSL Note:** If you are using Ubuntu on Windows via WSL, please note that systemd is not enabled by default. As a result, service management commands using `systemctl` (e.g., starting Redis or the Tetsuo service) may not work until systemd is enabled in your WSL installation. For guidance on enabling systemd and other WSL-specific configurations, please consult the [official WSL documentation](https://docs.microsoft.com/en-us/windows/wsl/).

1. Clone the repository:
```bash
git clone https://github.com/tetsuo-ai/tetsuo-service-starter-kit
cd tetsuo-service-starter-kit
```

2. Run the provided Ubuntu setup script:
```bash
chmod +x scripts/ubuntu-setup.sh  
sudo ./scripts/ubuntu-setup.sh
```
This script will:

- Installs Python 3.11, Redis, and other required packages.
- Creates a project directory (default: `/opt/tetsuo-service-starter-kit`).
- Sets up a virtual environment.
- Installs dependencies.
- Creates a default `.env` file (from `.env.example`) – **update this with your settings.**
- Creates a dedicated service user.
- Configures a systemd service for the FastAPI application.
- Generates convenience scripts:  
  - `./start.sh` – to start the service  
  - `./stop.sh` – to stop the service  
  - `./status.sh` – to check service status  
  - `./test.sh` – to run tests

3. Start Redis server:
```bash
sudo systemctl start redis-server
```

4. Test Redis connection:
```bash
./test.sh
```

5. Start the service:
```bash
./start.sh
```

6. Check the status:
```bash
./status.sh
```

7. Test the API:
```bash
curl -v http://127.0.0.1:6502/health
curl -X POST http://127.0.0.1:6502/api/v1/demo/demo -H "Authorization: Bearer your-super-secret-api-token-here" -H "Content-Type: application/json" -d '{"demo": "test"}'
```

8. Stop the service:
```bash
./stop.sh
```

### macOS Setup

These instructions are for macOS.

1. Clone the repository:
```bash
git clone https://github.com/tetsuo-ai/tetsuo-service-starter-kit
cd tetsuo-service-starter-kit
```
2. Install Python 3.11 using pyenv:
```bash
brew install pyenv
pyenv install 3.11
pyenv local 3.11
```

3. Create and activate virtual environment:
```bash
python --version # should return 3.11.x
python -m venv .venv
source .venv/bin/activate
```

4. Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

5. Copy example environment file and configure:
```bash
cp .env.example .env
# Edit .env with your settings
```

6. Install and launch Redis:
```bash
brew install redis
brew services start redis
```

7. Test Redis connection:
```bash
python -m tests.redis_test # should return "✓ Redis connected" or
python tests/redis_test.py # should return "✓ Redis connected"
``` 

8. Start the service:
```bash
python -m app.main
```

9. Test the API:
```bash
curl -v http://127.0.0.1:6502/health
curl -X POST http://127.0.0.1:6502/api/v1/demo/demo -H "Authorization: Bearer your-super-secret-api-token-here" -H "Content-Type: application/json" -d '{"demo": "test"}'
```

10. Stop the service:
```bash
# Send an interrupt signal (SIGINT) by pressing **Ctrl+C** in the terminal running `python -m app.main`. This will gracefully shut down the FastAPI service.

# Stop the Redis service:
brew services stop redis
```

### Docker Setup

1. Clone the repository:
```bash
git clone https://github.com/tetsuo-ai/tetsuo-service-starter-kit
cd tetsuo-service-starter-kit
```

2. Copy the `.env.example` file to `.env` and configure:
```bash
cp .env.example .env
# Edit .env with your settings
# For docker compose setup, be sure to change the REDIS_HOST from `localhost` to `redis`
```

3. Start the docker compose services:

**Important:** If you are already running a Redis service on your host, you must stop it first to avoid port conflicts.

- **Ubuntu/WSL:**  
  ```bash
  sudo systemctl stop redis
  ```

- **macOS:**  
  ```bash
  brew services stop redis
  ```

Once the Redis service is stopped, you can build and start your application using Docker Compose.

```bash
docker compose up --build
```

This configuration is optimized for local development—the `app` directory is volume-mounted into the container, and Uvicorn's built-in file watcher (enabled via the `--reload` flag) makes it easy to see code changes in real time.

> **Note:** If you modify the dependencies in `requirements.txt`, you must stop and rebuild the docker container to incorporate the changes. If docker compose is running in detached mode, stop it using `docker compose down`. If it's running in the foreground, press **Ctrl+C** to stop the process, then restart with `docker compose up --build`.

4. Test the API:
```bash
curl -v http://127.0.0.1:6502/health
curl -X POST http://127.0.0.1:6502/api/v1/demo/demo -H "Authorization: Bearer your-super-secret-api-token-here" -H "Content-Type: application/json" -d '{"demo": "test"}'
```

5. Stop the service:
```bash
docker compose down
```


## Configuration ⚙️

Key environment variables in `.env`:

```ini
# API Settings
API_V1_STR=/api/v1
PROJECT_NAME=Tetsuo AI Extension Service API

# Redis Settings
REDIS_HOST=localhost # or change to redis if using docker compose
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Contract Addresses
TETSUO_POOL_ADDRESS=your_pool_address
TETSUO_TOKEN_ADDRESS=your_token_address

```

## API Documentation 📚

Once running, visit:
- OpenAPI docs: `http://localhost:6502/docs`
- ReDoc: `http://localhost:6502/redoc`

### Key Endpoints

- **Whale Monitoring**:
  - `GET /api/v1/demo/demo`: Demo endpoint

- **WebSocket**:
  - `WSS /ws`: Real-time updates for all services

## Development 🔧

- Run tests: `./test.sh`
- Check Redis: `python redis_test.py`
- API tests: `python app/tests/test_api.py`

## Contributing 🤝

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## License 📄

MIT License - see LICENSE file for details

## Support 🆘

- Create an issue for bug reports or feature requests
- For security issues, please email security@yourdomain.com

## Project Status 📊

Current development status:
- ✅ Foundation Layer (Redis, Config, Logging)
- ✅ Data Models (Pydantic)
- ✅ Redis Data Schemas
- ✅ Core Services
- ✅ API Layer
- ✅ WebSocket Implementation

---

Made with ❤️ by the Tetsuo Core Team
