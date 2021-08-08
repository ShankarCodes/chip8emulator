import os
import sys
from chip8emulator import Engine
from chip8emulator import log
logger = log.create_logger(__name__)
if __name__ == '__main__':
    if len(sys.argv) > 1:
        if os.path.isfile(sys.argv[1]):
            engine = Engine()
            engine.load_settings()
            engine.init()
            engine.run(rompath=sys.argv[1])
        else:
            logger.info('Please specify a valid rom file name.')
    else:
        engine = Engine()
        engine.load_settings()
        engine.init()
        logger.info('No rom specified, running default rom.')
        engine.run(rompath='roms/TEST_ROM_DISPLAY_A')
