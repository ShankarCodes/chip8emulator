import os
import sys
import json

from log import create_logger
logger = create_logger(__name__)

try:
    import pygame
except Exception as e:
    logger.exception("Error while importing pygame.")
    logger.critical("pygame is required to run this game. Exiting now")
    sys.exit(1)

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
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), *args)


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
                settings = json.loads(settings_file.read())

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
                logger.warn(f'Flag {flag} not found, ignoring')
                val = 0
            flg = flg | val

        self.settings = settings
        self.settings['flag'] = flg

    def init(self):
        try:
            logger.info("Game details")
            logger.info("-"*50)
            logger.info(f"Width: {self.settings['width']}")
            logger.info(f"Height: {self.settings['height']}")
            logger.info(f"Title:{self.settings['title']}")
            logger.info(f"FPS:{self.settings['fps']}")
            logger.info(
                f"Creation Flags:{', '.join(self.settings['creation_flags'])}")
            logger.info("-"*50)
            logger.info("Initializing engine")
            pygame.init()
            logger.info("Creating screen")
            self.screen = pygame.display.set_mode(
                (self.settings['width'],
                 self.settings['height']),
                self.settings['flag'])
            logger.info("Created screen")
            inf = pygame.display.Info()
            logger.info(f"Acceleration type:{inf.hw}")
            logger.info(f"Video memory:{inf.video_mem}")
            pygame.display.set_caption(self.settings['title'])
            self.clock = pygame.time.Clock()
            logger.info("Created clock")
        except Exception as e:
            logger.exception("An error occured while Initializing")

    def run(self):
        try:
            pass
        except Exception as e:
            logger.exception(
                f"An error occured while running the emulator!")

    def quit(self):
        logger.info(
            f"Exiting....")
        pygame.quit()
        sys.exit(0)


if __name__ == '__main__':
    engine = Engine()
    engine.load_settings()
    engine.init()
    engine.run()
    engine.quit()
