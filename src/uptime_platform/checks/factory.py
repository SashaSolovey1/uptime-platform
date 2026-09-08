from uptime_platform.checks.dns import DnsChecker
from uptime_platform.checks.http import HttpChecker
from uptime_platform.checks.protocols import (
    CheckerProtocol,
)
from uptime_platform.checks.tcp import TcpChecker
from uptime_platform.monitors.entities import (
    DnsMonitorConfig,
    HttpMonitorConfig,
    Monitor,
    MonitorType,
    TcpMonitorConfig,
)


class CheckerFactory:
    def create(
        self,
        monitor: Monitor,
    ) -> CheckerProtocol:
        if monitor.monitor_type is MonitorType.HTTP:
            if not isinstance(
                monitor.config,
                HttpMonitorConfig,
            ):
                raise TypeError("HTTP monitor has invalid config")

            return HttpChecker(
                url=monitor.config.url,
            )

        if monitor.monitor_type is MonitorType.TCP:
            if not isinstance(
                monitor.config,
                TcpMonitorConfig,
            ):
                raise TypeError("TCP monitor has invalid config")

            return TcpChecker(
                host=monitor.config.host,
                port=monitor.config.port,
            )

        if monitor.monitor_type is MonitorType.DNS:
            if not isinstance(
                monitor.config,
                DnsMonitorConfig,
            ):
                raise TypeError("DNS monitor has invalid config")

            return DnsChecker(
                host=monitor.config.host,
                record_type=monitor.config.record_type,
            )

        raise ValueError(f"Unsupported monitor type: {monitor.monitor_type}")
