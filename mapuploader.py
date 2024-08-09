import argparse
from zeroconf import ServiceBrowser, Zeroconf, IPVersion, ServiceStateChange
from pftp import Pftp
from time import sleep

address = None
port = None

def on_service_state_change(zeroconf: Zeroconf, service_type: str, name: str, state_change: ServiceStateChange) -> None:
    global address, port

    if state_change is ServiceStateChange.Added:
        info = zeroconf.get_service_info(service_type, name)
        address = info.addresses_by_version(IPVersion.V6Only)[0]
        port = info.port

def main(file: str) -> None:
    zeroconf = Zeroconf(ip_version=IPVersion.V6Only)

    ServiceBrowser(zeroconf, "_polar-ftp._tcp.local.", handlers=[on_service_state_change])

    print("Waiting for device...")

    try:
        while address is None and port is None:
            sleep(0.5)
    except KeyboardInterrupt:
        print("Interrupted")
        exit()
    finally:
        zeroconf.close()

    pftp = Pftp(address, port)
    pftp.connect()
    pftp.get_device_info()
    pftp.start_sync()
    pftp.upload_map(file)
    pftp.stop_sync()
    pftp.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload map to Polar V650 device")
    parser.add_argument("map", help="path to map file")

    args = parser.parse_args()
    main(args.map)

