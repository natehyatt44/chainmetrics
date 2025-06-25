# ChainMetrics Backend

A modern Python backend for the Hedera cryptocurrency metrics dashboard. Built with FastAPI, DuckDB, and comprehensive API integrations.

## Features

- **Real-time HBAR Data**: Fetches current HBAR price, market cap, and trading metrics
- **Historical Data**: Stores and serves historical price data for analysis
- **Robust API**: RESTful endpoints with proper error handling and caching
- **Background Tasks**: Automated data fetching with configurable intervals
- **Database**: DuckDB for efficient data storage and querying
- **Monitoring**: Comprehensive logging and health check endpoints

## Tech Stack

- **Framework**: FastAPI with Uvicorn
- **Database**: DuckDB
- **HTTP Client**: HTTPX with retry logic
- **Scheduling**: APScheduler
- **Logging**: Loguru
- **Configuration**: Pydantic with environment variables
- **Code Quality**: Ruff for linting and formatting

## Quick Start

1. **Create virtual environment**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env file with your API keys
   ```

4. **Run the server**:
   ```bash
   python main.py
   ```

5. **Visit the API docs**: http://localhost:8000/docs

## Environment Configuration

Create a `.env` file based on `.env.example`:

```env
# Required for full functionality
COINGECKO_API_KEY=your_coingecko_api_key
COINMARKETCAP_API_KEY=your_coinmarketcap_api_key

# Optional - uses defaults if not set
DATABASE_PATH=./data/hedera_metrics.db
API_PORT=8000
LOG_LEVEL=INFO
```

## API Endpoints

### Health & Status
- `GET /` - Root endpoint with API information
- `GET /health` - Health check with database status

### HBAR Data
- `GET /api/v1/hbar/current` - Current HBAR market data
- `GET /api/v1/hbar/history?days=7` - Historical price data
- `GET /api/v1/hbar/stats` - HBAR statistics and analytics
- `POST /api/v1/hbar/refresh` - Manually refresh HBAR data

### Metrics
- `GET /api/v1/metrics/summary` - Comprehensive metrics summary

## Project Structure

```
backend/
├── src/
│   ├── api/
│   │   ├── endpoints.py      # API route definitions
│   │   └── middleware.py     # Custom middleware
│   ├── data_fetchers/
│   │   ├── base_fetcher.py   # Base class with retry logic
│   │   ├── coingecko.py      # CoinGecko API integration
│   │   ├── coinmarketcap.py  # CoinMarketCap integration
│   │   └── hedera.py         # Hedera network data
│   ├── database/
│   │   ├── connection.py     # Database connection manager
│   │   └── models.py         # Data models and schemas
│   ├── schedulers/
│   │   └── tasks.py          # Background task scheduling
│   └── config.py             # Configuration management
├── tests/                    # Test files
├── requirements.txt          # Python dependencies
├── pyproject.toml           # Ruff configuration
└── main.py                  # Application entry point
```

## Development

### Code Quality

Format code with Ruff:
```bash
ruff format .
ruff check .
```

### Testing

Run tests:
```bash
pytest
pytest -v  # Verbose output
pytest --cov=src  # With coverage
```

### Adding New Data Sources

1. Create a new fetcher class in `src/data_fetchers/`
2. Inherit from `BaseFetcher` or `RateLimitedFetcher`
3. Implement required methods:
   ```python
   class NewFetcher(BaseFetcher):
       def _get_auth_headers(self) -> Dict[str, str]:
           return {"Authorization": f"Bearer {self.api_key}"}
       
       async def fetch_data(self) -> Dict[str, Any]:
           return await self._make_request("endpoint")
   ```

### Database Schema

The database uses three main tables:

- `hbar_metrics` - HBAR price and market data
- `hedera_network_metrics` - Network performance metrics
- `hedera_tokens` - Token data for Hedera ecosystem

## Monitoring

### Logs

Logs are structured and include:
- Request/response logging
- Database operations
- Scheduled task execution
- Error tracking

### Metrics

- API response times via `X-Process-Time` header
- Database query performance
- Scheduler job status
- Rate limiting statistics

## Production Deployment

### Environment Setup

1. Set production environment variables
2. Configure database path for persistent storage
3. Set up proper logging (JSON format recommended)
4. Configure CORS origins for your frontend domain

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

### Monitoring & Alerting

- Health check endpoint: `/health`
- Structured logging for log aggregation
- API metrics available via headers
- Database connection monitoring

## API Rate Limits

- **CoinGecko**: 25 requests/minute (free tier)
- **CoinMarketCap**: 30 requests/minute (free tier)
- **Internal**: No rate limiting

## Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Check `DATABASE_PATH` in `.env`
   - Ensure write permissions for data directory

2. **API Key Issues**:
   - Verify API keys in `.env` file
   - Check API key permissions and limits

3. **Port Already in Use**:
   - Change `API_PORT` in `.env`
   - Kill existing processes: `lsof -ti:8000 | xargs kill`

### Debug Mode

Enable debug logging:
```env
LOG_LEVEL=DEBUG
```

## Performance

- **Database**: DuckDB provides excellent performance for analytical queries
- **Caching**: HTTP response caching with appropriate TTL
- **Connection Pooling**: HTTPX connection pooling for external APIs
- **Background Tasks**: Non-blocking scheduled data updates

## Contributing

1. Follow the existing code style (Ruff formatting)
2. Add tests for new features
3. Update documentation
4. Ensure all tests pass before submitting

## License

This project is part of the ChainMetrics dashboard suite.