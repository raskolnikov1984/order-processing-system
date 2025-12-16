import os


class Settings:
    POSTGRES_USER = "postgres"
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "SUp3r-pass*DB")
    DATABASE = os.getenv("POSTGRES_PAYMENT_DB", "payment_service")
