# Tetsuo Service Starter Kit 🚀

A scalable service-oriented architecture for building extension APIs for Tetsuo AI Core Services

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

- Python 3.11+
- Redis Server

## Installation 🛠️

1. Clone the repository:
```bash
git clone https://github.com/tetsuo-ai/tetsuo-service-starter-kit
cd tetsuo-service-starter-kit
```

2. Create and activate virtual environment:
```bash
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy example environment file and configure:
```bash
cp .env.example .env
# Edit .env with your settings
```

## Configuration ⚙️

Key environment variables in `.env`:

```ini
# API Settings
API_V1_STR=/api/v1
PROJECT_NAME=Tetsuo AI Extension Service API

# Redis Settings
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Contract Addresses
TETSUO_POOL_ADDRESS=your_pool_address
TETSUO_TOKEN_ADDRESS=your_token_address

```

## Running the Service 🚀

1. Start Redis server:
```bash
# macOS
brew services start redis

# Linux
sudo systemctl start redis-server
```

2. Test Redis connection:
```bash
./test.sh
```

3. Start the service:
```bash
./start.sh
```

The API will be available at `http://localhost:8000`

## API Documentation 📚

Once running, visit:
- OpenAPI docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

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