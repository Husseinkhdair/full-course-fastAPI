from Core.DataBase.MongoDb import get_mongo_client
import pytest



@pytest.mark.asyncio
async def test_mongodb_connection():
    client = get_mongo_client()

    result = await client.admin.command("ping")

    assert result["ok"] == 1