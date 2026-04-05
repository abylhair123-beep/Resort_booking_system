# Uyaly_Booking

Desktop resort booking management system with a FastAPI backend and PySide6 desktop client.

## Project structure

```
Uyaly_Booking/
├── backend/
│   ├── .env.example
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── core/
│       ├── models/
│       ├── routers/
│       ├── schemas/
│       └── services/
└── desktop_client/
    ├── requirements.txt
    ├── main.py
    ├── api/
    └── ui/
```

## Ubuntu setup

### 1) PostgreSQL

```bash
sudo apt update
sudo apt install -y postgresql postgresql-contrib
sudo -u postgres psql -c "CREATE DATABASE uyaly_booking;"
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres';"
```

### 2) Backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### 3) Desktop client

```bash
cd desktop_client
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## API docs

With backend running, open:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
