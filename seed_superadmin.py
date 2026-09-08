import asyncio
import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from Core.DataBase.PostgresDB import SessionLocal
from Core.DataBase.MongoDb import get_db
from Core.security.Password import hash_password
from Features.Auth.Data.Models.AuthModelPostgres import AuthPostgresModel
from Features.Auth.Data.Models.AuthModelMongos import AuthMongosModel
from Features.Auth.Domain.Entities.UserEntity import Role, Status

SUPERADMIN_EMAIL = "superadmin@admin.com"
SUPERADMIN_PASSWORD = "superadmin123"
SUPERADMIN_NAME = "Super Administrator"


def seed_postgres():
    db = SessionLocal()
    try:
        existing = db.execute(
            select(AuthPostgresModel).where(AuthPostgresModel.email == SUPERADMIN_EMAIL)
        ).scalars().first()

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        hashed_pwd = hash_password(SUPERADMIN_PASSWORD)

        if not existing:
            user = AuthPostgresModel(
                id=str(uuid.uuid4()),
                name=SUPERADMIN_NAME,
                email=SUPERADMIN_EMAIL,
                password=hashed_pwd,
                role=Role.SUPERADMIN.value,
                status=Status.ACTIVE.value,
                created_at=now_str,
                updated_at=now_str,
            )
            db.add(user)
            db.commit()
            print(f"[PostgreSQL] Created SuperAdmin account: {SUPERADMIN_EMAIL}")
        else:
            # تحديث الرتبة وكلمة المرور للتأكد من صلاحياتها
            existing.role = Role.SUPERADMIN.value
            existing.password = hashed_pwd
            existing.status = Status.ACTIVE.value
            existing.updated_at = now_str
            db.commit()
            print(f"[PostgreSQL] SuperAdmin account already exists and updated: {SUPERADMIN_EMAIL}")
    except Exception as e:
        db.rollback()
        print(f"[PostgreSQL] Error seeding SuperAdmin: {e}")
    finally:
        db.close()


async def seed_mongo():
    try:
        db = get_db()
        users_collection = db["Users"]

        existing = await users_collection.find_one({"email": SUPERADMIN_EMAIL})
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        hashed_pwd = hash_password(SUPERADMIN_PASSWORD)

        if not existing:
            user = AuthMongosModel(
                id=str(uuid.uuid4()),
                name=SUPERADMIN_NAME,
                email=SUPERADMIN_EMAIL,
                password=hashed_pwd,
                role=Role.SUPERADMIN.value,
                status=Status.ACTIVE.value,
                created_at=now_str,
                updated_at=now_str,
            )
            await users_collection.insert_one(user.to_dict())
            print(f"[MongoDB] Created SuperAdmin account: {SUPERADMIN_EMAIL}")
        else:
            await users_collection.update_one(
                {"email": SUPERADMIN_EMAIL},
                {
                    "$set": {
                        "role": Role.SUPERADMIN.value,
                        "password": hashed_pwd,
                        "status": Status.ACTIVE.value,
                        "updated_at": now_str,
                    }
                }
            )
            print(f"[MongoDB] SuperAdmin account already exists and updated: {SUPERADMIN_EMAIL}")
    except Exception as e:
        print(f"[MongoDB] Error seeding SuperAdmin: {e}")


async def main():
    print("Seeding SuperAdmin account...")
    seed_postgres()
    await seed_mongo()
    print("Done seeding SuperAdmin!")


if __name__ == "__main__":
    asyncio.run(main())
