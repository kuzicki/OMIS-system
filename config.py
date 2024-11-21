import os


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY", "default-secret-key"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = (
        False
    )
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://localhost/mydatabase"
    )


class DevConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:123@localhost/OMIS"
