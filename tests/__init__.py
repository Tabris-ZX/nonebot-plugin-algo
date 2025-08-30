from tests.data_source import DataSource
from tests.config import AlgoConfig
import asyncio

if __name__ == "__main__":
        msg=asyncio.run(DataSource.ans_today())
        print(msg)