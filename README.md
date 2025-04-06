# Archelon Genesis

A cryptocurrency market data simulator for testing and training algorithmic trading models.

## Overview

Archelon Genesis provides a realistic market data simulation environment for developing and testing algorithmic trading strategies. It offers historical data access and price simulation capabilities that mimic real market behavior while providing a controlled, repeatable environment for strategy development.

## Features

- **Historical Data Access**: Retrieve historical OHLCV (Open, High, Low, Close, Volume) data for various cryptocurrencies
- **Price Simulation**: Generate realistic price movements that respect candle constraints (open, high, low, close)
- **API Interface**: Access all functionality through a RESTful API
- **Stateful Simulation**: Maintain simulation state between requests for realistic progression
- **Reset Capability**: Reset simulations to test strategies with the same data multiple times

## Installation

You can install and run Archelon Genesis either directly on your system or using Docker.

### Option 1: Direct Installation

#### Prerequisites

- Python 3.11+
- Git

#### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/archelon-genesis.git
   cd archelon-genesis
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Download historical data:
   ```bash
   python record_data.py AVAXUSDT 1h
   ```
   This will download hourly data for AVAXUSDT. You can specify other symbols and intervals as needed.

### Option 2: Using Docker

#### Prerequisites

- Docker
- Git

#### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/archelon-genesis.git
   cd archelon-genesis
   ```

2. Download historical data (before building the Docker image):
   ```bash
   # If you have Python installed locally
   pip install python-binance pandas
   python record_data.py AVAXUSDT 1h
   ```

3. Build the Docker image:
   ```bash
   # Using the provided script
   ./docker-build.sh

   # Or manually
   docker build -t archelon-genesis:latest .
   ```

4. Run the Docker container:
   ```bash
   # Using the provided script
   ./docker-run.sh

   # Or manually
   docker run -d --name archelon-genesis -p 8000:8000 -v "$(pwd)/data:/app/data" -v "$(pwd)/log_files:/app/log_files" archelon-genesis:latest
   ```

5. Alternatively, use Docker Compose:
   ```bash
   docker-compose up -d
   ```

## Usage

### Starting the API Server

```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python run_api.py
```

The API server will start on http://localhost:8000.

### API Documentation

Once the server is running, you can access the interactive API documentation at:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

### Key Endpoints

#### Health Check
```
GET /health
```
Verifies that the API is running correctly.

#### Get Historical Candle Data
```
GET /market/candles?symbol=AVAXUSDT&interval=1h&limit=100
```
Returns historical OHLCV data for the specified symbol and interval.

#### Get Simulated Price
```
GET /market/price?symbol=AVAXUSDT&interval=1h
```
Returns the current simulated price. Each request advances the simulation to the next price point.

#### Reset Simulation
```
POST /market/reset-simulation?symbol=AVAXUSDT&interval=1h
```
Resets the price simulation to the beginning.

### Example: Simulating Price Movement

1. Reset the simulation:
   ```bash
   curl -X POST "http://localhost:8000/market/reset-simulation?symbol=AVAXUSDT&interval=1h"
   ```

2. Get price updates (run multiple times to see price progression):
   ```bash
   curl "http://localhost:8000/market/price?symbol=AVAXUSDT&interval=1h"
   ```

3. Observe how the price moves from the open price, touches both high and low at least once, and eventually reaches the close price.

## Downloading Additional Data

To download data for multiple symbols:

```bash
python download_multiple.py
```

You can edit the `SYMBOLS` and `INTERVALS` lists in `download_multiple.py` to customize which data is downloaded.

## For Developers

### Project Structure

```
├── api/                  # FastAPI application
│   ├── main.py           # Main application entry point
│   └── routers/          # API route definitions
├── common/               # Shared utilities
│   └── static_logger.py  # Logging configuration
├── data/                 # Historical market data (CSV files)
├── data_recorder/        # Scripts for downloading historical data
├── log_files/            # Application logs
├── services/             # Core services
│   ├── binance_service.py  # Binance API integration
│   ├── exchange_base.py    # Abstract exchange interface
│   ├── simulation/         # Simulation services
│   └── utils/              # Utility functions and decorators
├── .venv/                # Virtual environment (created during setup)
├── config.py             # Application configuration
├── docker-build.sh       # Script to build Docker image
├── docker-compose.yml    # Docker Compose configuration
├── docker-run.sh         # Script to run Docker container
├── Dockerfile            # Docker image definition
├── download_multiple.py  # Script to download data for multiple symbols
├── main.py               # CLI application entry point
├── record_data.py        # Script to record historical data
├── requirements.txt      # Python dependencies
└── run_api.py            # Script to run the API server
```

### Adding New Features

#### Supporting New Exchanges

To add support for a new exchange:

1. Create a new class that extends `ExchangeBase` in `services/`
2. Implement the required methods for fetching market data
3. Update the API to use the new exchange class

#### Enhancing the Simulation

The price simulation logic is in `services/simulation/price_simulator.py`. You can modify this to:

- Add more sophisticated price movement patterns
- Implement different market conditions (trending, ranging, volatile)
- Add support for simulating order execution

### Docker Development

#### Building and Testing Docker Images

The project includes Docker support for development and deployment:

1. **Building the image**:
   ```bash
   ./docker-build.sh
   ```

2. **Running the container**:
   ```bash
   ./docker-run.sh
   ```

3. **Using Docker Compose**:
   ```bash
   # Start services
   docker-compose up -d

   # View logs
   docker-compose logs -f

   # Stop services
   docker-compose down
   ```

4. **Rebuilding after changes**:
   ```bash
   docker-compose up -d --build
   ```

#### Docker Image Customization

You can customize the Docker image by editing the `Dockerfile`. For example:

- Adding additional packages
- Changing the base image
- Modifying environment variables

### Running Tests

```bash
# Running tests locally
python -m pytest

# Running tests in Docker
docker run --rm archelon-genesis:latest python -m pytest
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
