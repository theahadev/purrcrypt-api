# purrcrypt-api 🐱

A worse version of [purrcrypt](https://github.com/vxfemboy/purrcrypt) with an API and a WebUI, made for personal use in Python. **Not cryptographically secure for any real use.**

Encodes messages into cat sounds (`meow`, `purr`, `nya`, etc.), with optional password-based XOR encryption derived from SHA-256.

## Features

- Encode any text into cat sounds
- Optional password protection (XOR cipher with SHA-256 key derivation)
- REST API built with Flask
- Static WebUI served via [dufs](https://github.com/sigoden/dufs)
- Docker Compose setup for easy self-hosting

## API Endpoints

All endpoints are prefixed with `/purrcrypt`.

| Method | Endpoint   | Description                          |
|--------|------------|--------------------------------------|
| GET    | `/`        | API info                             |
| POST   | `/encrypt` | Encrypt text into cat sounds         |
| POST   | `/decrypt` | Decrypt cat sounds back into text    |
| GET    | `/health`  | Health check                         |

### Encrypt

```http
POST /purrcrypt/encrypt
Content-Type: application/json

{
  "text": "Hello, World!",
  "password": "optional"
}
```

**Response:**
```json
{
  "success": true,
  "meow": "meow purr nya ...",
  "encrypted": true,
  "password_protected": false
}
```

### Decrypt

```http
POST /purrcrypt/decrypt
Content-Type: application/json

{
  "meow": "meow purr nya ...",
  "password": "optional"
}
```

**Response:**
```json
{
  "success": true,
  "text": "Hello, World!",
  "decrypted": true,
  "password_protected": false
}
```

## Running with Docker Compose

```bash
docker compose up -d
```

This starts two services:
- **`purrcrypt-api`** — Flask API on port 5000 (internal)
- **`purrcrypt-webui`** — Static WebUI served by dufs (internal)

Both services join an external Docker network named `proxy`. Create it first if it doesn't exist:

```bash
docker network create proxy
```

### Environment Variables

| Variable          | Default                              | Description                        |
|-------------------|--------------------------------------|------------------------------------|
| `HOST`            | `0.0.0.0`                            | Bind address                       |
| `PORT`            | `5000`                               | Port to listen on                  |
| `API_URL`         | `http://localhost:5000`              | Public API URL (used by health check) |
| `DEBUG`           | `false`                              | Enable debug logging               |
| `PYTHONUNBUFFERED`| `1`                                  | Unbuffered Python output           |

## Running Locally

```bash
pip install -r requirements.txt
python app.py
```

The API will be available at `http://localhost:5000/purrcrypt`.

## CLI Usage

```bash
python3 purrcrypt.py encrypt "Hello, World!"
python3 purrcrypt.py decrypt "meow purr nya"
```

## Project Structure

```
purrcrypt-api/
├── app.py              # Flask app entry point
├── purrcrypt.py        # CLI entry point
├── api/
│   ├── cipher.py       # High-level CatCipher class
│   ├── crypto.py       # XOR + SHA-256 key derivation
│   ├── encoder.py      # Cat sound encoder/decoder
│   ├── main.py         # CLI logic
│   └── utils.py        # Utilities
├── webui/              # Static WebUI files
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## ⚠️ Security Warning

This project uses XOR encryption with a SHA-256-derived key. **It is not cryptographically secure** and should not be used to protect sensitive data. It's a fun toy, not a real cipher.
