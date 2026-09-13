from uptime_platform.api_keys.models import (
    ApiKeyModel,
)
from uptime_platform.auth.models import (
    RefreshSessionModel,
)
from uptime_platform.checks.models import (
    CheckModel,
)
from uptime_platform.incidents.models import (
    IncidentModel,
)
from uptime_platform.maintenance.models import (
    MaintenanceWindowModel,
)
from uptime_platform.monitors.models import (
    MonitorModel,
)
from uptime_platform.notifications.models import (
    NotificationDeliveryModel,
    NotificationDestinationModel,
)
from uptime_platform.organizations.models import (
    MembershipModel,
    OrganizationModel,
)
from uptime_platform.outbox.models import (
    OutboxEventModel,
)
from uptime_platform.status_pages.models import (
    StatusPageModel,
    StatusPageMonitorModel,
)
from uptime_platform.users.models import (
    UserModel,
)

REGISTERED_MODELS = (
    ApiKeyModel,
    RefreshSessionModel,
    CheckModel,
    IncidentModel,
    MaintenanceWindowModel,
    MonitorModel,
    NotificationDeliveryModel,
    NotificationDestinationModel,
    MembershipModel,
    OrganizationModel,
    OutboxEventModel,
    StatusPageModel,
    StatusPageMonitorModel,
    UserModel,
)


def register_models() -> None:
    _ = REGISTERED_MODELS
