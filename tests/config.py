import os
ENV = os.getenv("TEST_ENV", "local")

BASE_URLS = {
    "local":"http://127.0.0.1:8000",
    "qa": "http://qa.example.com:8000",
}

BASE_URL = BASE_URLS[ENV]
TIMEOUT = int(os.getenv("TEST_TIMEOUT","30"))