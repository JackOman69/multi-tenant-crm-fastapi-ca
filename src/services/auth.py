from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from src.db.models import OrganizationMemberModel, OrganizationModel, Role, UserModel
from src.domain.exceptions import AuthenticationError, ConflictError
from src.repositories.organization import OrganizationRepository
from src.repositories.organization_member import OrganizationMemberRepository
from src.repositories.user import UserRepository


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.org_repo = OrganizationRepository(session)
        self.member_repo = OrganizationMemberRepository(session)

    async def register(self, email: str, password: str, name: str, org_name: str) -> tuple[UserModel, OrganizationModel]:
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ConflictError("Email already registered")

        user = UserModel(
            id=uuid4(),
            email=email,
            hashed_password=hash_password(password),
            name=name,
        )
        user = await self.user_repo.create(user)

        org = OrganizationModel(id=uuid4(), name=org_name)
        org = await self.org_repo.create(org)

        member = OrganizationMemberModel(
            id=uuid4(),
            organization_id=org.id,
            user_id=user.id,
            role=Role.OWNER,
        )
        await self.member_repo.create(member)

        return user, org

    async def login(self, email: str, password: str) -> dict[str, str]:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid credentials")

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    async def verify_token(self, user_id: UUID) -> UserModel:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise AuthenticationError("Invalid token")
        return user
