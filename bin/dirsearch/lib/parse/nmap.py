from __future__ import annotations

from lib.utils import safe_xml


def parse_nmap(file: str) -> list[str]:
    root = safe_xml.parse_file(file).getroot()
    targets = []
    for host in root.iter("host"):
        hostname = (
            host.find("hostnames").find("hostname").get("name")
            or host.find("address").get("addr")
        )
        targets.extend(
            f"{hostname}:{port.get('portid')}"
            for port in host.find("ports").iter("port")
            if (
                port.get("protocol") == "tcp"  # UDP is not used in HTTP because it is not a "reliable transport"
                and port.find("state").get("state") == "open"
                and port.find("service").get("name") in ["http", "unknown"]
            )
        )

    return targets
