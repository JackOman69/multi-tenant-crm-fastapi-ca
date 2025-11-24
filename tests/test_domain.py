from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

from src.domain.entities.activity import Activity
from src.domain.entities.contact import Contact
from src.domain.entities.deal import Deal
from src.domain.entities.organization import Organization
from src.domain.entities.organization_member import OrganizationMember
from src.domain.entities.task import Task
from src.domain.entities.user import User
from src.domain.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    DomainError,
    NotFoundError,
    ValidationError,
)
from src.domain.value_objects.activity_type import ActivityType
from src.domain.value_objects.deal_stage import DealStage
from src.domain.value_objects.deal_status import DealStatus
from src.domain.value_objects.role import Role


def test_role_enum() -> None:
    assert Role.OWNER == "owner"
    assert Role.ADMIN == "admin"
    assert Role.MANAGER == "manager"
    assert Role.MEMBER == "member"


def test_deal_status_enum() -> None:
    assert DealStatus.NEW == "new"
    assert DealStatus.IN_PROGRESS == "in_progress"
    assert DealStatus.WON == "won"
    assert DealStatus.LOST == "lost"


def test_deal_stage_enum() -> None:
    assert DealStage.QUALIFICATION == "qualification"
    assert DealStage.PROPOSAL == "proposal"
    assert DealStage.NEGOTIATION == "negotiation"
    assert DealStage.CLOSED == "closed"


def test_activity_type_enum() -> None:
    assert ActivityType.COMMENT == "comment"
    assert ActivityType.STATUS_CHANGED == "status_changed"
    assert ActivityType.STAGE_CHANGED == "stage_changed"
    assert ActivityType.TASK_CREATED == "task_created"
    assert ActivityType.SYSTEM == "system"


def test_user_entity() -> None:
    user = User(
        id=uuid4(),
        email="test@example.com",
        hashed_password="hashed",
        name="Test User",
        created_at=datetime.now(),
    )
    assert user.email == "test@example.com"
    assert user.name == "Test User"


def test_organization_entity() -> None:
    org = Organization(id=uuid4(), name="Test Org", created_at=datetime.now())
    assert org.name == "Test Org"


def test_organization_member_entity() -> None:
    member = OrganizationMember(
        id=uuid4(), organization_id=uuid4(), user_id=uuid4(), role=Role.OWNER
    )
    assert member.role == Role.OWNER


def test_contact_entity() -> None:
    contact = Contact(
        id=uuid4(),
        organization_id=uuid4(),
        owner_id=uuid4(),
        name="John Doe",
        email="john@example.com",
        phone="+1234567890",
        created_at=datetime.now(),
    )
    assert contact.name == "John Doe"
    assert contact.email == "john@example.com"


def test_deal_entity() -> None:
    deal = Deal(
        id=uuid4(),
        organization_id=uuid4(),
        contact_id=uuid4(),
        owner_id=uuid4(),
        title="Big Deal",
        amount=Decimal("10000.00"),
        currency="USD",
        status=DealStatus.NEW,
        stage=DealStage.QUALIFICATION,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    assert deal.title == "Big Deal"
    assert deal.amount == Decimal("10000.00")
    assert deal.status == DealStatus.NEW
    assert deal.stage == DealStage.QUALIFICATION


def test_task_entity() -> None:
    task = Task(
        id=uuid4(),
        deal_id=uuid4(),
        title="Follow up",
        description="Call customer",
        due_date=date.today(),
        is_done=False,
        created_at=datetime.now(),
    )
    assert task.title == "Follow up"
    assert task.is_done is False


def test_activity_entity() -> None:
    activity = Activity(
        id=uuid4(),
        deal_id=uuid4(),
        author_id=uuid4(),
        type=ActivityType.COMMENT,
        payload={"text": "Test comment"},
        created_at=datetime.now(),
    )
    assert activity.type == ActivityType.COMMENT
    assert activity.payload["text"] == "Test comment"


def test_domain_exceptions() -> None:
    assert issubclass(AuthenticationError, DomainError)
    assert issubclass(AuthorizationError, DomainError)
    assert issubclass(ValidationError, DomainError)
    assert issubclass(NotFoundError, DomainError)
    assert issubclass(ConflictError, DomainError)
