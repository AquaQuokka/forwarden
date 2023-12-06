import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve
from core.forwarder import app, username, AppConfig, IP, SixToFour
from tabulate import tabulate

if __name__ == '__main__':
    # Configuration
    cfg = AppConfig().config

    # IP handling
    ipv4_instance = IP(target='192.0.2.0', default='127.0.0.1')
    ipv4 = ipv4_instance.handle()

    ipv6_instance = SixToFour(ipv4)
    ipv6 = f"[{ipv6_instance.handle()}]"

    url = lambda ip: f"http://{ip}:{cfg['bind'].replace('0.0.0.0:', '')}/view/{username}/display/0"

    host_data = [
        ["IPv4", f"{url(ipv4)}"],
        ["IPv6", f"{url(ipv6)}"],
    ]

    # Print tabulated data
    print(tabulate(host_data, tablefmt="rounded_outline"))

    # Run the server
    asyncio.run(serve(app, Config.from_mapping(cfg)))
