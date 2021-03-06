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

DEFAULT = '''{
	"width": 640,
	"height": 320,
	"fps": 60,
	"title": "Chip-8 Emulator",
	"creation_flags": [
		"HWSURFACE",
		"DOUBLEBUF",
		"HWACCEL"
	],
	"exit_on_error": true,
	"show_grids": true,
	"tile_size": 10,
	"tile_x": 64,
	"tile_y": 32,
	"speed": 10,
	"fontset": "8JCQkPAgYCAgcPAQ8IDw8BDwEPCQkPAQEPCA8BDw8IDwkPDwECBAQPCQ8JDw8JDwEPDwkPCQkOCQ4JDg8ICAgPDgkJCQ4PCA8IDw8IDwgIA="
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
        kc = pygame.key.key_code
        self.keyboard = {
            kc('1'): 1, kc('2'): 2, kc('3'): 3, kc('4'): 0xc,
            kc('q'): 4, kc('w'): 5, kc('e'): 6, kc('r'): 0xd,
            kc('a'): 7, kc('s'): 8, kc('d'): 9, kc('f'): 0xe,
            kc('z'): 0xa, kc('x'): 0, kc('c'): 0xb, kc('v'): 0xf,
        }

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
            self.create_emulator()
            self.tile_size = self.settings['tile_size']
            logger.info(f'Emulator:{self.emulator.name}')
            logger.info(f'Emulator version:{self.emulator.version}')
            logger.info("Created emulator")

            self.settings['is_paused'] = False
            self.to_draw = False
        except Exception as e:
            logger.exception("An error occured while Initializing")
            self.quit(-1)

    def create_emulator(self):
        self.emulator = Emulator(self.settings)

        @self.emulator.external('clear')
        def clear_display(opcode):
            logger.info('Clearing screen')
            # self.screen.fill(pygame.Color('black'))

            self.emulator.graphic_memory = bytearray(64*32)

        @self.emulator.external('close')
        def close(opcode):
            self.quit(exit_code=opcode)

        @self.emulator.external('draw')
        def draw(opcode):
            X = (opcode & 0x0F00) >> 8
            Y = (opcode & 0x00F0) >> 4
            x = self.emulator.V[X]
            y = self.emulator.V[Y]
            N = (opcode & 0x000F)

            self.screen.fill(pygame.Color('black'))
            self.emulator.V[0xF] = 0
            # Draws N+1 lines
            for i in range(N):
                line = self.emulator.memory[self.emulator.I + i]
                self.setPixel((x + 0) % 64, (y+i) % 32, (line & 0x80) >> 7)
                self.setPixel((x + 1) % 64, (y+i) % 32, (line & 0x40) >> 6)
                self.setPixel((x + 2) % 64, (y+i) % 32, (line & 0x20) >> 5)
                self.setPixel((x + 3) % 64, (y+i) % 32, (line & 0x10) >> 4)
                self.setPixel((x + 4) % 64, (y+i) % 32, (line & 0x08) >> 3)
                self.setPixel((x + 5) % 64, (y+i) % 32, (line & 0x04) >> 2)
                self.setPixel((x + 6) % 64, (y+i) % 32, (line & 0x02) >> 1)
                self.setPixel((x + 7) % 64, (y+i) % 32, (line & 0x01))
            self.to_draw = True

        self.emulator.init_optable()

    def setPixel(self, x, y, val):
        #old_val = self.emulator.graphic_memory[y*64 + x]
        #self.emulator.graphic_memory[y*64 + x] ^= val
        # if val == 0:
        #    return None
        # if old_val == 1 and val == 1:
        #    self.emulator.graphic_memory[y*64 + x] = 0
        #    self.emulator.V[0xF] = 1
        #    logger.warning('Flipped')
        # if old_val == 0 and val == 1:
        #    self.emulator.graphic_memory[y*64 + x] = 1
        if val != 0:
            if self.emulator.graphic_memory[y*64 + x] == 1:
                self.emulator.V[0xF] = 1
            self.emulator.graphic_memory[y*64 + x] ^= 1

        #new_val = self.emulator.graphic_memory[y*64 + x]
        # If any pixel changes from 1 to 0, set V[F] to 1
        # if (new_val != old_val) and old_val == 1:
        #    logger.warning('Flipped!')
        #    self.emulator.V[0xF] = 1

    def render_tiles(self):
        if not self.to_draw:
            return None
        for x in range(64):
            for y in range(32):
                if self.emulator.graphic_memory[y*64 + x] != 0:
                    pygame.draw.rect(self.screen, pygame.Color(
                        'white'), (x*self.tile_size, y*self.tile_size, self.tile_size, self.tile_size))
        self.to_draw = False

    def run(self, rompath):
        """
        rom = [0x1208, 0x9090, 0xf090, 0x9000, 0x00e0,
               0xa202, 0x6205, 0x6304, 0xd234, 0x1212]
        rom_bytes = bytearray(20)
        for i, rb in enumerate(rom):
            rom_bytes[i] = rb >> 8
            rom_bytes[i+1] = rb & 0x00FF
        """
        byt = bytearray()
        with open(rompath, 'rb') as rom:
            byt = bytearray(rom.read())
        pygame.display.set_caption(f'CHIP-8 interpreter ({rompath})')
        self.emulator.load_to_memory(byt)
        try:
            logger.info("Starting emulator....")
            success = False
            while True:
                # logger.debug(f'{self.emulator.pc}')
                keys = pygame.key.get_pressed()
                if keys[K_ESCAPE]:
                    self.quit()

                if not self.settings['is_paused']:
                    for i in range(self.settings['speed']):
                        for k, v in self.keyboard.items():
                            self.emulator.keyboard_snap[v] = keys[k]
                        success = self.emulator.execute_opcode_from_memory()
                        if not success:
                            self.emulator.quit()
                            self.quit()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.quit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_o:
                            self.settings['speed'] += 1
                            logger.info(
                                f'Increasing speed by 1, New speed: {self.settings["speed"]}')
                        if event.key == pygame.K_p:
                            self.settings['speed'] -= 1
                            logger.info(
                                f'Decreasing speed by 1, New speed: {self.settings["speed"]}')
                        if event.key == pygame.K_i:
                            self.settings['fps'] += 1
                            logger.info(
                                f'Increasing fps by 1, New fps: {self.settings["fps"]}')
                        if event.key == pygame.K_u:
                            self.settings['fps'] -= 1
                            logger.info(
                                f'Decreasing fps by 1, New fps: {self.settings["fps"]}')
                        if event.key == pygame.K_l:
                            logger.info('Restarting emulator...')
                            self.create_emulator()
                            byt = bytearray()
                            with open(rompath, 'rb') as rom:
                                byt = bytearray(rom.read())
                            self.emulator.load_to_memory(byt)

                if self.settings['is_paused']:
                    for k, v in self.keyboard.items():
                        self.emulator.keyboard_snap[v] = keys[k]
                    for i, k in enumerate(self.emulator.keyboard_snap):
                        if k == 1:
                            if self.settings.get('temp') is not None:
                                self.emulator.V[self.settings.get('temp')] = i
                                self.settings['is_paused'] = False
                            break
                # self.screen.fill(pygame.Color('black'))
                self.render_tiles()

                pygame.display.flip()
                dt = self.clock.tick(self.settings['fps'])
                self.emulator.add_time(dt)
                self.emulator.update_delay_timer()
        except Exception as e:
            logger.exception(
                f"An error occured while running the emulator!")

    def quit(self, exit_code=0):
        logger.info(
            f"Exiting....")
        self.emulator.variable_dump()
        logger.info('Keyboard State')
        logger.info(self.emulator.keyboard_snap)

        pygame.quit()
        sys.exit(exit_code)
