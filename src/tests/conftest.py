import pytest
import asyncio
import pytest_asyncio
import aioboto3
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from botocore.exceptions import ClientError, EndpointConnectionError
from sqlalchemy.dialects.postgresql import insert as pg_insert

from config import get_settings, get_accounts_email_notificator, get_s3_storage_client
from database import (
    reset_database,
    get_db_contextmanager,
    UserGroupEnum,
    UserGroupModel
)
from database.populate import CSVDatabaseSeeder
from main import app
from security.interfaces import JWTAuthManagerInterface
from security.token_manager import JWTAuthManager
from storages import S3StorageClient
from tests.doubles.fakes.storage import FakeS3Storage
from tests.doubles.fakes.activity import FakeUserActivityRepo
from tests.doubles.stubs.emails import StubEmailSender
from user_activity.dependencies import get_user_activity_repository


def pytest_configure(config):
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "order: Specify the order of test execution")
    config.addinivalue_line("markers", "unit: Unit tests")


async def _full_db_reset() -> None:
    await reset_database()

    async with get_db_contextmanager() as session:
        if session.get_bind().dialect.name != "postgresql":
            return

        result = await session.execute(
            text(
                "SELECT tablename FROM pg_tables "
                "WHERE schemaname = 'public' AND tablename <> 'alembic_version'"
            )
        )
        tables = [row[0] for row in result.fetchall()]
        if tables:
            quoted = ", ".join(f'"{name}"' for name in tables)
            await session.execute(text(f"TRUNCATE TABLE {quoted} RESTART IDENTITY CASCADE"))
            await session.commit()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def _app_lifespan():
    """
    Run the app's lifespan (startup/shutdown) for every test.

    The AsyncMongoClient created in the lifespan is bound to the event loop it
    was first used in. pytest-asyncio gives each test its own loop (scope=function),
    so the lifespan must live in the same loop as the test: otherwise you get
    "Cannot use AsyncMongoClient in different event loop".
    """
    async with app.router.lifespan_context(app):
        yield



@pytest_asyncio.fixture(scope="function", autouse=True)
async def reset_db(request):
    """
    Reset the database before each test function, except for tests marked 'e2e'.

    E2E tests intentionally share state between steps (see @pytest.mark.order),
    so they reset the DB explicitly via `reset_db_once_for_e2e`.
    """
    if request.node.get_closest_marker("e2e"):
        yield
        return

    await _full_db_reset()
    yield


@pytest_asyncio.fixture(scope="function")
async def reset_db_once_for_e2e(request):
    """
    Explicit database reset for end-to-end tests (request it in the first test
    of a chain, or in every independent e2e test).
    """
    await _full_db_reset()


@pytest.fixture(scope="session")
def settings():
    # Plain sync fixture: no event loop involved.
    return get_settings()


@pytest_asyncio.fixture(scope="function")
async def email_sender_stub():
    return StubEmailSender()


@pytest_asyncio.fixture(scope="function")
async def s3_storage_fake():
    return FakeS3Storage()


@pytest_asyncio.fixture(scope="function")
async def user_activity_repo_fake():
    return FakeUserActivityRepo()


@pytest_asyncio.fixture(scope="function")
async def ensure_s3_bucket(settings):
    """Create the S3 bucket if it does not exist (replaces the minio_mc service)."""
    session = aioboto3.Session(
        aws_access_key_id=settings.S3_STORAGE_ACCESS_KEY,
        aws_secret_access_key=settings.S3_STORAGE_SECRET_KEY,
    )
    last_exc = None
    for _ in range(30):
        try:
            async with session.client("s3", endpoint_url=settings.S3_STORAGE_ENDPOINT) as s3:
                try:
                    await s3.head_bucket(Bucket=settings.S3_BUCKET_NAME)
                except ClientError:
                    await s3.create_bucket(Bucket=settings.S3_BUCKET_NAME)
            return
        except (EndpointConnectionError, ConnectionError, OSError) as exc:
            last_exc = exc
            await asyncio.sleep(2)
    raise last_exc


@pytest_asyncio.fixture(scope="function")
async def s3_client(settings, ensure_s3_bucket):
    return S3StorageClient(
        endpoint_url=settings.S3_STORAGE_ENDPOINT,
        access_key=settings.S3_STORAGE_ACCESS_KEY,
        secret_key=settings.S3_STORAGE_SECRET_KEY,
        bucket_name=settings.S3_BUCKET_NAME
    )


@pytest_asyncio.fixture(scope="function")
async def client(email_sender_stub, s3_storage_fake, user_activity_repo_fake):
    """
    Async HTTP client with fakes injected (isolated per function ).
    """
    app.dependency_overrides[get_accounts_email_notificator] = lambda: email_sender_stub
    app.dependency_overrides[get_s3_storage_client] = lambda: s3_storage_fake
    app.dependency_overrides[get_user_activity_repository] = lambda: user_activity_repo_fake

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as async_client:
        yield async_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def e2e_client():
    """
    Async HTTP client for end-to-end tests (real dependencies, no overrides).
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as async_client:
        yield async_client


# ---------------------------------------------------------------------------
# DB sessions
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with get_db_contextmanager() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def e2e_db_session():
    async with get_db_contextmanager() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def jwt_manager() -> JWTAuthManagerInterface:
    settings = get_settings()
    return JWTAuthManager(
        secret_key_access=settings.SECRET_KEY_ACCESS,
        secret_key_refresh=settings.SECRET_KEY_REFRESH,
        algorithm=settings.JWT_SIGNING_ALGORITHM
    )


@pytest_asyncio.fixture(scope="function")
async def seed_user_groups(db_session: AsyncSession):
    groups_data = [{"name": group.value} for group in UserGroupEnum]

    stmt = pg_insert(UserGroupModel).values(groups_data).on_conflict_do_nothing(index_elements=["name"])

    await db_session.execute(stmt)
    await db_session.commit()
    yield db_session


@pytest_asyncio.fixture(scope="function")
async def seed_database(db_session):
    settings = get_settings()
    seeder = CSVDatabaseSeeder(csv_file_path=settings.PATH_TO_MOVIES_CSV, db_session=db_session)

    if not await seeder.is_db_populated():
        await seeder.seed()

    yield db_session


@pytest_asyncio.fixture(scope="function")
async def mongo_db(_app_lifespan, settings):
    """
    MongoDB database taken from the client created by the app lifespan
    (same event loop as the test, same client type as the app: pymongo async).
    """
    client = app.state.mongo_client
    return client[settings.MONGO_DB]


@pytest_asyncio.fixture(scope="function")
async def cleanup_mongo_user_activity(mongo_db):
    """
    Clean the user_activity collection both before and after the test.
    """
    await mongo_db["user_activity"].delete_many({})
    yield
    await mongo_db["user_activity"].delete_many({})
