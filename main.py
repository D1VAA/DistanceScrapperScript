from api.api import run_api
import asyncio


if __name__ == "__main__":
    asyncio.run(run_api(3000, False))