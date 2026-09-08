from contextlib import asynccontextmanager
from typing import Optional
from Core.DataBase.MongoDb import get_mongo_client, get_db
from Core.Settings import SettingsApp

settings = SettingsApp()


@asynccontextmanager
async def get_mongo_rollback_session():
    """
    Async Context Manager لإنشاء ClientSession والتراجع عن العمليات (Rollback).
    - إذا كانت قاعدة بيانات MongoDB تعمل كـ Replica Set: يتم استخدام start_transaction و abort_transaction.
    - إذا كانت Standalone (بدون Replica Set): يتم إنهاء الجلسة بأمان.
    """
    client = get_mongo_client()
    # في PyMongo AsyncMongoClient، start_session() غير متزامنة وتُستخدم مع async with
    async with client.start_session() as session:
        has_transaction = False

        try:
            try:
                await session.start_transaction()
                has_transaction = True
            except Exception:
                # Standalone MongoDB لا يدعم Multi-Document Transactions
                has_transaction = False

            yield session

            # التراجع التلقائي عن المعاملة (Rollback)
            if has_transaction and session.in_transaction:
                await session.abort_transaction()
        except Exception:
            if has_transaction and session.in_transaction:
                await session.abort_transaction()
            raise


@asynccontextmanager
async def get_clean_mongo_collection(collection_name: Optional[str] = None):
    """
    Async Context Manager يضمن عزل الاختبارات وإلغاء العمليات (Rollback)
    عن طريق تفريغ الـ Collection تلقائياً بعد انتهاء الاختبار،
    وهو الخيار الأمثل والأنسب لبيئات التطوير المحلية (Local MongoDB Standalone).

    الاستخدام:
        async with get_clean_mongo_collection() as collection:
            repo = AuthRepositoryMongoDB(collection=collection)
    """
    db = get_db()
    name = collection_name or f"test_{settings.collection_users}"
    collection = db[name]

    try:
        yield collection
    finally:
        # حذف جميع البيانات المدخلة أثناء الاختبار لضمان بيئة نظيفة تماماً (Rollback)
        await collection.delete_many({})


async def mongo_db_session():
    """
    Async Generator جاهز للاستخدام مباشرة في Pytest Fixtures:

    @pytest.fixture
    async def db_session():
        async with get_mongo_rollback_session() as session:
            yield session
    """
    async with get_mongo_rollback_session() as session:
        yield session
