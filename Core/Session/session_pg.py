from contextlib import contextmanager
from sqlalchemy.orm import Session
from Core.DataBase.PostgresDB import engine
from Features.Auth.Data.Models.AuthModelPostgres import Base
import pytest


@contextmanager
def get_pg_rollback_session():
    """
    Context manager يُنشئ Session مع Nested Transaction (Savepoint)،
    وعند الانتهاء يقوم بعمل rollback تلقائي لإلغاء كافة العمليات التي حدثت على PostgreSQL،
    سواء نجح الاختبار أو فشل.

    الاستخدام مع with:
        with get_pg_rollback_session() as session:
            repo = AuthRepositoryPostgresSQl(db=session)
            ...
    """
    # 1. التأكد من إنشاء الجداول في قاعدة بيانات Postgres
    Base.metadata.create_all(bind=engine)

    # 2. فتح Connection وبدء Transaction رئيسية
    connection = engine.connect()
    transaction = connection.begin()

    # 3. إنشاء Session مع create_savepoint لاعتراض أي commit داخلي
    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    try:
        yield session
    finally:
        # 4. ينفذ دائماً عند انتهاء الاختبار للتراجع عن كافة العمليات
        session.close()
        transaction.rollback()
        connection.close()



@pytest.fixture
def db_session():
    """
    Pytest Fixture جاهز للاستخدام المباشر لعمل Rollback تلقائي:
    
    from Core.Session.session_pg import db_session
    """
    with get_pg_rollback_session() as session:
        yield session