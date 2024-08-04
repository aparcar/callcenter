from pyinfra.operations import server, files
from pyinfra import host
from pyinfra.facts.server import Hostname

import json

server.shell(name="Update package list", commands=["opkg update"])

for package in [
    "coreutils-stat",
    "zram-swap",
    "openssh-sftp-server",
    "coreutils-sha1sum",
]:
    server.shell(
        name=f"Install {package}",
        commands=[f"opkg install {package}"],
    )

system_board = server.shell(
    name="Get running OpenWrt version",
    commands=["ubus call system board"],
)

# print(system_board.get_fact("stdout"))

server.files.line(
    name="Set hostname",
    path="/etc/config/system",
    line="	option hostname .*",
    present=True,
    replace=f"	option hostname '{host.name}'",
)

server.shell(name="Reload system", commands=["/etc/init.d/system reload"])

for file in ["extensions.conf", "pjsip.conf", "pjsip_wizard.conf", "lantiq.conf"]:
    server.files.put(
        name=f"Upload {file}",
        src=f"files/{file}",
        dest=f"/etc/asterisk/{file}",
        mode="644",
    )

for file in ["firewall", "dhcp", "asterisk"]:
    server.files.put(
        name=f"Upload /etc/config/{file}",
        src=f"files/{file}",
        dest=f"/etc/config/{file}",
        mode="644",
    )

server.shell(name="Restart Asterisk", commands=["/etc/init.d/asterisk restart"])
server.shell(name="Restart dnsmasq", commands=["/etc/init.d/dnsmasq restart"])
server.shell(name="Restart firewall", commands=["/etc/init.d/firewall reload"])
