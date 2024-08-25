from pathlib import Path

from pyinfra import host
from pyinfra.facts.server import Hostname
from pyinfra.facts.files import FindInFile
from pyinfra.operations import files, server

changes = {}

if host.name != "192.168.1.1":
    changes["hostname"] = server.files.line(
        name="Set hostname",
        path="/etc/config/system",
        line="	option hostname .*",
        present=True,
        replace=f"	option hostname '{host.name}'",
    )

    if changes["hostname"].changed:
        server.shell(name="Reload system", commands=["/etc/init.d/system reload"])


unet_option_key = host.get_fact(
    FindInFile, "/etc/config/network", pattern="option key '.*'"
)

if unet_option_key:
    changes["network"] = server.files.template(
        name="Upload /etc/config/network",
        src="files/network.j2",
        dest="/etc/config/network",
        unet_option_key=unet_option_key[0],
        mode="644",
    )
else:
    changes["network"] = server.files.put(
        name=f"Upload /etc/config/network",
        src=f"files/network",
        dest=f"/etc/config/network",
        mode="644",
    )

for file in ["extensions.conf", "pjsip.conf", "pjsip_wizard.conf", "lantiq.conf"]:
    changes[file] = server.files.put(
        name=f"Upload {file}",
        src=f"files/{file}",
        dest=f"/etc/asterisk/{file}",
        mode="644",
    )

for file in ["firewall", "dhcp", "asterisk", "wireless"]:
    changes[file] = server.files.put(
        name=f"Upload /etc/config/{file}",
        src=f"files/{file}",
        dest=f"/etc/config/{file}",
        mode="644",
    )

if (
    changes["asterisk"].changed
    or changes["extensions.conf"].changed
    or changes["pjsip.conf"].changed
    or changes["pjsip_wizard.conf"].changed
    or changes["lantiq.conf"].changed
):
    server.shell(name="Reload asterisk", commands=["/etc/init.d/asterisk reload"])

if changes["dhcp"].changed:
    server.shell(name="Restart dnsmasq", commands=["/etc/init.d/dnsmasq restart"])

if changes["firewall"].changed:
    server.shell(name="Restart firewall", commands=["/etc/init.d/firewall reload"])

if changes["wireless"].changed:
    server.shell(name="Restart wireless", commands=["wifi"])

server.files.put(
    name="Upload  /etc/hotplug.d/iface/99-dnsmasq-restart",
    src="files/99-dnsmasq-restart",
    dest="/etc/hotplug.d/iface/99-dnsmasq-restart",
    mode="755",
)

# if changes["network"].changed:
#     server.shell(name="Restart network", commands=["/etc/init.d/network restart"])
