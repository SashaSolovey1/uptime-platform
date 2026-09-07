from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    model_validator,
)

from uptime_platform.monitors.entities import (
    MonitorStatus,
    MonitorType,
)


class HttpMonitorConfigCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    url: HttpUrl


class TcpMonitorConfigCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    host: str = Field(
        min_length=1,
        max_length=255,
    )

    port: int = Field(
        ge=1,
        le=65535,
    )


class MonitorCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    monitor_type: MonitorType

    config: HttpMonitorConfigCreate | TcpMonitorConfigCreate

    interval_seconds: int = Field(
        default=60,
        ge=10,
        le=3600,
    )

    timeout_seconds: int = Field(
        default=5,
        ge=1,
        le=60,
    )

    failure_threshold: int = Field(
        default=3,
        ge=1,
        le=10,
    )

    recovery_threshold: int = Field(
        default=2,
        ge=1,
        le=10,
    )

    @model_validator(mode="after")
    def validate_config(
        self,
    ) -> "MonitorCreate":
        if self.monitor_type is MonitorType.HTTP and not isinstance(
            self.config,
            HttpMonitorConfigCreate,
        ):
            raise ValueError("HTTP monitor requires HTTP configuration")

        if self.monitor_type is MonitorType.TCP and not isinstance(
            self.config,
            TcpMonitorConfigCreate,
        ):
            raise ValueError("TCP monitor requires TCP configuration")

        return self


class HttpMonitorConfigUpdate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    url: HttpUrl | None = None


class TcpMonitorConfigUpdate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    host: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    port: int | None = Field(
        default=None,
        ge=1,
        le=65535,
    )


class MonitorUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    config: HttpMonitorConfigUpdate | TcpMonitorConfigUpdate | None = None

    interval_seconds: int | None = Field(
        default=None,
        ge=10,
        le=3600,
    )

    timeout_seconds: int | None = Field(
        default=None,
        ge=1,
        le=60,
    )

    failure_threshold: int | None = Field(
        default=None,
        ge=1,
        le=10,
    )

    recovery_threshold: int | None = Field(
        default=None,
        ge=1,
        le=10,
    )


class HttpMonitorConfigResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    url: str


class TcpMonitorConfigResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    host: str
    port: int


class MonitorResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    name: str
    monitor_type: MonitorType

    config: HttpMonitorConfigResponse | TcpMonitorConfigResponse

    interval_seconds: int
    timeout_seconds: int
    status: MonitorStatus
    created_at: datetime
    next_check_at: datetime

    failure_threshold: int
    recovery_threshold: int
    consecutive_failures: int
    consecutive_successes: int
