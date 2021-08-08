try:
    import pygame
    from pygame.locals import *
except Exception as e:
    logger.exception("Error while importing pygame.")
    logger.critical("pygame is required to run this game. Exiting now")
    sys.exit(1)

from .emulator import Emulator
import os
import sys
import json

from .log import create_logger
logger = create_logger(__name__)


# TODO: Make the config file loading, case independent.
# TODO: Also if the required variable is missing, choose the default one.

DEFAULT = '''
{
	"width": 640,
	"height": 480,
	"fps": 60,
	"title": "Chip-8 Emulator",
	"creation_flags":["HWSURFACE", "DOUBLEBUF", "HWACCEL", "SCALED"],
	"exit_on_error": false
}
'''

FLAGS = {
    "FULLSCREEN": pygame.FULLSCREEN,
    "DOUBLEBUF": pygame.DOUBLEBUF,
    "HWSURFACE": pygame.HWSURFACE,
    "OPENGL": pygame.OPENGL,
    "RESIZABLE": pygame.RESIZABLE,
    "NOFRAME": pygame.NOFRAME,
    "HWACCEL": pygame.HWACCEL,
    "SCALED": pygame.SCALED,
}


def get_path(*args):
    """
    Gets the path relative to the script.
    """
    # return os.path.join(os.path.abspath(os.path.dirname(__file__)), *args)
    return os.path.join(os.getcwd(), *args)


class Engine:
    '''
    This the main class in the game.
    Engine handles everything in the game
    '''

    def __init__(self):
        logger.info("creating engine")

    def load_settings(self):
        '''
        Load the settings
        If the settings file settings.json exists, load it. If not 
        create the file and create the default settings.json
        '''

        if os.path.isfile(get_path("settings.json")):
            logger.info("settings.json found ... loading settings")
            settings_file = open(get_path("settings.json"), "r")
            try:
                settings = json.loads(DEFAULT)
                load_settings = json.loads(settings_file.read())
                # Removes "", None, etc.
                load_settings = {k: v for k, v in load_settings.items() if v}
                settings.update(load_settings)

            except:
                logger.exception(
                    "an error occured while reading and processing settings")
                logger.info("Using default settings")
                settings = json.loads(DEFAULT)

            finally:
                settings_file.close()

        else:
            try:
                logger.info(
                    "settings.json not found ... trying to create settings")
                settings = open(get_path("settings.json"), 'w')
                settings.write(DEFAULT)
                settings.close()
                logger.info("settings.json created")
                settings = json.loads(DEFAULT)
            except Exception as e:
                logger.warning(
                    'Unable to create file, check permissions: '+str(e))
                logger.warning(
                    'The game will run but you will not be able to save the settings')
                settings = json.loads(DEFAULT)

        flg = 0
        for flag in settings.get('creation_flags', []):
            val = FLAGS.get(flag, None)
            if val is None:
                logger.warning(f'Flag {flag} not found, ignoring')
                val = 0
            flg = flg | val

        self.settings = settings
        self.settings['flag'] = flg

    def init(self):
        try:
            logger.info("Engine details")
            logger.info("Loaded Settings -")
            logger.info("-"*50)
            logger.info(f"Width: {self.settings['width']}")
            logger.info(f"Height: {self.settings['height']}")
            logger.info(f"Title:{self.settings['title']}")
            logger.info(f"FPS:{self.settings['fps']}")
            logger.info(
                f"Creation Flags:{', '.join(self.settings['creation_flags'])}")
            logger.info("-"*50)

            logger.info("Initializing pygame")
            pygame.init()
            logger.info("Initialized pygame")

            logger.info("Initializing graphics")
            logger.info("Creating screen")
            self.screen = pygame.display.set_mode(
                (self.settings['width'],
                 self.settings['height']),
                self.settings['flag'])
            logger.info("Created screen")
            inf = pygame.display.Info()

            logger.info("-"*50)
            logger.info(
                f"Acceleration type:{'Hardware' if inf.hw >= 1 else 'Software'}")
            logger.info(
                f"Video memory:{inf.video_mem if inf.video_mem > 0 else 'UNKNOWN'}")
            pygame.display.set_caption(self.settings['title'])
            logger.info("-"*50)
            logger.info("Initialized graphics")

            logger.info("Creating clock")
            self.clock = pygame.time.Clock()
            logger.info("Created clock")

            logger.info("Creating emulator")
            self.emulator = Emulator(self.settings)

            @self.emulator.external('close')
            def close(opcode):
                self.quit(exit_code=opcode)
            self.emulator.init_optable()
            logger.info(f'Emulator:{self.emulator.name}')
            logger.info(f'Emulator version:{self.emulator.version}')
            logger.info("Created emulator")
        except Exception as e:
            logger.exception("An error occured while Initializing")
            self.quit(-1)

    def run(self):

        rom = [0x1208, 0x9090, 0xf090, 0x9000, 0x00e0,
               0xa202, 0x6205, 0x6304, 0xd234, 0x1212]
        for i in rom:
            self.emulator.execute_opcode(i)
        try:
            logger.info("Starting emulator....")
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.quit()

                keys = pygame.key.get_pressed()
                if keys[K_x]:
                    self.quit()

                self.screen.fill(pygame.Color('white'))
                pygame.display.flip()
                dt = self.clock.tick(self.settings['fps'])
        except Exception as e:
            logger.exception(
                f"An error occured while running the emulator!")

    def quit(self, exit_code=0):
        logger.info(
            f"Exiting....")
        pygame.quit()
        sys.exit(exit_code)
