import logging
import os
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import create_engine
from api.utils.aws import get_secret

# ENV_SECRET_ARN = os.getenv("RDS_SECRET_ARN")
ENV_SECRET_ARN = "arn:aws:secretsmanager:eu-west-1:435772683141:secret:orchestrator-ai-api-env-qiCMIU"

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        # self.secret = get_secret(os.getenv("RDS_SECRET_ARN"))
        self.host = "" #self.secret["host"]
        # Check if the environment is set to "local"
        if os.getenv("ENV") == "local":
            self.host = "127.0.0.1"
        self.username = "" #self.secret["username"]
        self.password = "" #self.secret["password"]
        self.db = "" #self.secret["dbname"]
        self.db_port = "" #self.secret["port"]
        self.engine = "" #self.get_async_engine()

    def get_async_engine(self):
        database_url = f"mysql+aiomysql://{self.username}:{self.password}@{self.host}:{self.db_port}/{self.db}"
        return create_async_engine(database_url,
        pool_size=5,
        pool_timeout=30,
        pool_recycle=3600,
        pool_pre_ping=True
    )

    def get_engine(self):
        database_url = f"mysql://{self.username}:{self.password}@{self.host}:{self.db_port}/{self.db}"
        return create_engine(database_url)

    def get_session(self) -> AsyncSession:
        return AsyncSession(bind=self.engine, expire_on_commit=False)


database = Database()

async def get_database_session():
    async with database.get_session() as session:
            yield session