import logging
import sys

import yaml


def load_config():
    with open('config.yaml', 'r') as config_file:
        return yaml.safe_load(config_file)


def main():
    logging.info("pskreporter-monitor")


if __name__ == "__main__":
    config = load_config()

    logger_level = config.get('LOG_LEVEL', 'INFO')
    logger_format = config.get('LOG_FORMAT', '%(asctime)-15s %(levelname)s:%(funcName)s:%(lineno)d:%(message)s')
    logging.basicConfig(stream=sys.stdout, level=logger_level, format=logger_format)

    callsigns = config.get('callsigns')
    zones = config.get('zones')
    logging.info(f"callsigns = {callsigns}")
    logging.info(f"zones = {zones}")

    main()
