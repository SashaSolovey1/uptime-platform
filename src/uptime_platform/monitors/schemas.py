from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    model_validator,
)

from uptime_platform.monitors.entities import (
    DnsRecordType,
    HttpMethod,
    MonitorStatus,
    MonitorType,
)

HttpStatusCode = Annotated[
    int,
    Field(
        ge=100,
        le=599,
    ),
]


class HttpMonitorConfigCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    url: HttpUrl
    method: HttpMethod = HttpMethod.GET

    expected_status_codes: list[HttpStatusCode] | None = Field(
        default=None,
        min_length=1,
    )

    body_contains: str | None = Field(
        default=None,
        min_length=1,
        max_length=4096,
    )

    follow_redirects: bool = False
    verify_tls: bool = True


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


class DnsMonitorConfigCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    host: str = Field(
        min_length=1,
        max_length=253,
    )

    record_type: DnsRecordType


class TlsMonitorConfigCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    host: str = Field(
        min_length=1,
        max_length=253,
    )

    port: int = Field(
        default=443,
        ge=1,
        le=65535,
    )

    expiry_threshold_days: int = Field(
        default=14,
        ge=0,
        le=365,
    )


class IcmpMonitorConfigCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    host: str = Field(
        min_length=1,
        max_length=253,
    )


class MonitorCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    monitor_type: MonitorType

    config: (
        HttpMonitorConfigCreate
        | TcpMonitorConfigCreate
        | DnsMonitorConfigCreate
        | TlsMonitorConfigCreate
        | IcmpMonitorConfigCreate
    )

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

    @model_validator(mode="before")
    @classmethod
    def parse_config(
        cls,
        data: object,
    ) -> object:
        if not isinstance(data, dict):
            return data

        raw_config = data.get("config")

        if not isinstance(raw_config, dict):
            return data

        try:
            monitor_type = MonitorType(data.get("monitor_type"))
        except (TypeError, ValueError):
            return data

        config_models = {
            MonitorType.HTTP: HttpMonitorConfigCreate,
            MonitorType.TCP: TcpMonitorConfigCreate,
            MonitorType.DNS: DnsMonitorConfigCreate,
            MonitorType.TLS: TlsMonitorConfigCreate,
            MonitorType.ICMP: IcmpMonitorConfigCreate,
        }

        config_model = config_models[monitor_type]

        return {
            **data,
            "config": config_model.model_validate(raw_config),
        }

    @model_validator(mode="after")
    def validate_config(
        self,
    ) -> "MonitorCreate":
        expected_config_types = {
            MonitorType.HTTP: HttpMonitorConfigCreate,
            MonitorType.TCP: TcpMonitorConfigCreate,
            MonitorType.DNS: DnsMonitorConfigCreate,
            MonitorType.TLS: TlsMonitorConfigCreate,
            MonitorType.ICMP: IcmpMonitorConfigCreate,
        }

        expected_type = expected_config_types[self.monitor_type]

        if not isinstance(
            self.config,
            expected_type,
        ):
            raise ValueError(  # noqa: TRY004
                f"{self.monitor_type.value.upper()} monitor "
                "requires matching configuration"
            )

        return self


class HttpMonitorConfigUpdate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    url: HttpUrl | None = None
    method: HttpMethod | None = None

    expected_status_codes: list[HttpStatusCode] | None = Field(
        default=None,
        min_length=1,
    )

    body_contains: str | None = Field(
        default=None,
        min_length=1,
        max_length=4096,
    )

    follow_redirects: bool | None = None
    verify_tls: bool | None = None


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


class DnsMonitorConfigUpdate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    host: str | None = Field(
        default=None,
        min_length=1,
        max_length=253,
    )

    record_type: DnsRecordType | None = None


class TlsMonitorConfigUpdate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    host: str | None = Field(
        default=None,
        min_length=1,
        max_length=253,
    )

    port: int | None = Field(
        default=None,
        ge=1,
        le=65535,
    )

    expiry_threshold_days: int | None = Field(
        default=None,
        ge=0,
        le=365,
    )


class IcmpMonitorConfigUpdate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    host: str | None = Field(
        default=None,
        min_length=1,
        max_length=253,
    )


class MonitorUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    config: dict[str, object] | None = None

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
    method: HttpMethod
    expected_status_codes: list[int] | None
    body_contains: str | None
    follow_redirects: bool
    verify_tls: bool


class TcpMonitorConfigResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    host: str
    port: int


class DnsMonitorConfigResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    host: str
    record_type: DnsRecordType


class TlsMonitorConfigResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    host: str
    port: int
    expiry_threshold_days: int


class IcmpMonitorConfigResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    host: str


class MonitorResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    name: str
    monitor_type: MonitorType

    config: (
        HttpMonitorConfigResponse
        | TcpMonitorConfigResponse
        | DnsMonitorConfigResponse
        | TlsMonitorConfigResponse
        | IcmpMonitorConfigResponse
    )

    interval_seconds: int
    timeout_seconds: int
    status: MonitorStatus
    created_at: datetime
    next_check_at: datetime

    failure_threshold: int
    recovery_threshold: int
    consecutive_failures: int
    consecutive_successes: int
