release: python3 -c "from DB.setup import init_db, seed_default_brackets; init_db(); seed_default_brackets()"
web: uvicorn api.main:app --host 0.0.0.0 --port $PORT
