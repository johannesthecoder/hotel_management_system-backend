from os import environ
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.write_concern import WriteConcern
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference


load_dotenv()

client = AsyncIOMotorClient(environ.get("MONGODB_URL"))
db = client["hms_db"]

default_find_limit = 25


async def mongodb_transaction_core(operations: list[dict]):
    result = []
    async with client.start_session() as session:
        async with session.start_transaction():
            for operation in operations:
                if operation.get("action").lower() == "update_one":
                    result.append(
                        await db[operation["db_name"]].update_one(
                            filter=operation["filter"],
                            update=operation["update"],
                            session=session,
                        )
                    )
                elif operation.get("action").lower() == "update_many":
                    result.append(
                        await db[operation["db_name"]].update_many(
                            filter=operation["filter"],
                            update=operation["update"],
                            session=session,
                        )
                    )
                elif operation.get("action").lower() == "insert_one":
                    result.append(
                        await db[operation["db_name"]].insert_one(
                            operation["insert"], session=session
                        )
                    )
                elif operation.get("action").lower() == "insert_many":
                    result.append(
                        await db[operation["db_name"]].insert_many(
                            operation["insert"], session=session
                        )
                    )
                elif operation.get("action").lower() == "read_one":
                    result.append(
                        dict(
                            await db[operation["db_name"]].find_one(
                                filter=operation["filter"], session=session
                            )
                        )
                    )
                elif operation.get("action").lower() == "read_many":
                    result.append(
                        list(
                            await db[operation["db_name"]].find(
                                filter=operation["filter"], session=session
                            )
                        )
                    )

    return result
