import json
import logging
import sys
from dataclasses import dataclass

import paho.mqtt.client as mqtt
import yaml


@dataclass
class Spot:
    sq: int  # sequence number
    f: int  # frequency
    md: str  # mode
    rp: int  # report (SNR)
    t: int  # seconds since unix epoch
    sc: str  # sender call
    rc: str  # receiver call
    sl: str  # sender locator
    rl: str  # receiver locator
    sa: int  # sender ADIF country code
    ra: int  # receiver ADIF country code
    b: str  # band

    # ADIF country codes: https://www.adif.org/304/ADIF_304.htm#Country_Codes
    def __str__(self):
        return f"{self.f / 1000000:10f} {self.b:<4s} {self.md:<4s} {self.rp:3d} {self.sc:<10s} {self.rc:<10s} {self.sl[:6].upper():<6s} {self.rl[:6].upper():<6s}"


def load_config():
    with open('config.yaml', 'r') as config_file:
        return yaml.safe_load(config_file)


def callback_on_connect(client, userdata, flags, rc):
    global connected
    if rc == 0:
        logging.info("Connected to pskreporter.info MQTT broker")
        connected = True
        subscribe()

    else:
        logging.error(f"Connection failed with code {rc}")


def callback_on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    spot = Spot(**payload)
    logging.info(f"{spot}")


def callback_on_disconnect(client, userdata, rc):
    global connected
    if rc != 0:
        connected = False
        logging.info(f"Unexpected disconnection. Reconnecting...")


def subscribe():
    if connected:
        for tx in config.get('transmitters', ['+']):
            for rx in config.get('receivers', ['+']):
                for band in config.get('bands', ['+']):
                    for mode in config.get('modes', ['+']):
                        for txloc in config.get('txlocators', ['+']):
                            for rxloc in config.get('rxlocators', ['+']):
                                sub = f"pskr/filter/v2/{band}/{mode}/{tx}/{rx}/{txloc}/{rxloc}/#"
                                logging.info(f"subscribing to {sub}...")
                                client.subscribe(sub)
                                # pskr/filter/v2/{band}/{mode}/{sendercall}/{receivercall}/{senderlocator}/{receiverlocator}


def get_mqtt_client():
    cl = mqtt.Client(client_id=broker_id)
    cl.on_connect = callback_on_connect
    cl.on_message = callback_on_message
    cl.on_disconnect = callback_on_disconnect
    return cl


def main():
    logging.info("pskreporter-monitor starting ...")
    logging.info(f"Connecting to {broker_host}:{broker_port} ...")
    client.connect(broker_host, broker_port, broker_timeout)
    client.loop_start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        logging.info("Disconnected. Exiting...")
        client.disconnect()
        client.loop_stop()


if __name__ == "__main__":
    config = load_config()
    connected = False

    logger_level = config.get('LOG_LEVEL', 'INFO')
    logger_format = config.get('LOG_FORMAT', '%(asctime)-15s %(message)s')
    logging.basicConfig(stream=sys.stdout, level=logger_level, format=logger_format)

    broker_host = config.get('broker-host', 'mqtt.pskreporter.info')
    broker_port = config.get('broker-port', 1883)
    broker_timeout = config.get('broker-timeout', 60)
    broker_id = f"pskreporter-monitor: {config.get('id', '')}"

    client = get_mqtt_client()

    main()
