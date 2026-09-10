from uptime_platform.checks.dns import DnsChecker
from uptime_platform.checks.http import HttpChecker
from uptime_platform.checks.icmp import IcmpChecker
from uptime_platform.checks.protocols import (
    CheckerProtocol,
)
from uptime_platform.checks.tcp import TcpChecker
from uptime_platform.checks.tls import TlsChecker
from uptime_platform.monitors.entities import (
    DnsMonitorConfig,
    HttpMonitorConfig,
    IcmpMonitorConfig,
    Monitor,
    MonitorType,
    TcpMonitorConfig,
    TlsMonitorConfig,
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
                method=monitor.config.method,
                expected_status_codes=(monitor.config.expected_status_codes),
                body_contains=monitor.config.body_contains,
                follow_redirects=(monitor.config.follow_redirects),
                verify_tls=monitor.config.verify_tls,
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

        if monitor.monitor_type is MonitorType.TLS:
            if not isinstance(
                monitor.config,
                TlsMonitorConfig,
            ):
                raise TypeError("TLS monitor has invalid config")

            return TlsChecker(
                host=monitor.config.host,
                port=monitor.config.port,
                expiry_threshold_days=(monitor.config.expiry_threshold_days),
            )

        if monitor.monitor_type is MonitorType.ICMP:
            if not isinstance(
                monitor.config,
                IcmpMonitorConfig,
            ):
                raise TypeError("ICMP monitor has invalid config")

            return IcmpChecker(
                host=monitor.config.host,
            )

        raise ValueError(f"Unsupported monitor type: {monitor.monitor_type}")
