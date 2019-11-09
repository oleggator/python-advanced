# Distributed Web Crawler
High perfomance web crawler

[Task (in russian)](task.md)

## Features
- asynchronous
- search Rest API
- throttling (by domain)
- distributed
- auth

## Usage
1. Start docker-compose
    ```bash
    docker-compose up -d
    ```
2. Signup
    ```bash
    curl -X POST -d "email=oleg@mail.net&name=Oleg&password=qwerty123" http://localhost:8080/api/v1/signup
    ```
3. Login
    ```bash
    curl -X POST -d "email=oleg@mail.net&password=qwerty123" http://localhost:8080/api/v1/login
    ```
4. Add crawl task
    ```bash
    curl -X POST -H "X-Token: <Token ID>" -d "domain=docs.python.org&https=1" http://localhost:8080/api/v1/index
    ```
5. Get result
    ```bash
    curl http://localhost:8080/api/v1/search?q=asyncio&limit=20&offset=5
    ```

## Arhitecture
```
                     +-------------+                      
+---------------+    |             |     +-----------------+
|               |<---|  Rest API   |<--->|                 |
|               |    |             |     |                 |
|               |    +-------------+     |                 |
|               |    +-------------+     |                 |
|               |    |             |     |                 |
|               |--->|   Crawler   |---->|  ElasticSearch  |
|               |    |             |     | (crawled pages) |
|   RabbitMQ    |    +-------------+     |                 |
|               |    +-------------+     |                 |
|               |    |             |     |                 |
|               |--->|   Crawler   |---->|                 |
|               |    |             |     +-----------------+
|               |    +-------------+     +---------------+ 
|               |    +-------------+     |               |
|               |    |             |     |  PostgreSQL   |
|               |<-->|    Auth     |<--->|  (user data)  |
+---------------+    |             |     |               |
                     +-------------+     +---------------+
```
