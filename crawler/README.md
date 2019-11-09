# Web Crawler
Async web crawler

## Features
- asynchronous
- search Rest API

## Usage
1. Create venv and install dependencies
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
1. Run docker-compose
    ```bash
    docker-compose up -d
    ```
1. Crawl task
    ```bash
    python main.py -e http://localhost:9200 -c 8 -p 8 docs.python.org
    ```
2. Get result
    ```bash
    curl http://localhost:8080/api/v1/search?q=asyncio&limit=20&offset=5
    ```
