from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class MonitorStatus(StrEnum):
    PENDING = "pending"
    UP = "up"
    DOWN = "down"
    PAUSED = "paused"


class MonitorType(StrEnum):
    HTTP = "http"
    TCP = "tcp"


@dataclass(frozen=True, slots=True)
class HttpMonitorConfig:
    url: str


@dataclass(frozen=True, slots=True)
class TcpMonitorConfig:
    host: str
    port: int


type MonitorConfig = HttpMonitorConfig | TcpMonitorConfig


@dataclass(frozen=True, slots=True)
class Monitor:
    id: UUID
    name: str

    monitor_type: MonitorType
    config: MonitorConfig

    interval_seconds: int
    timeout_seconds: int
    status: MonitorStatus
    created_at: datetime
    next_check_at: datetime

    failure_threshold: int = 3
    recovery_threshold: int = 2

    consecutive_failures: int = 0
    consecutive_successes: int = 0
