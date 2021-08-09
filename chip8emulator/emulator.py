import random
import sys
from .log import create_logger
import base64

logger = create_logger(__name__)


def hexrepr(x): return f"{f'{x:#06x}': ^8}"


def notimpl(op): return logger.warning(
    f'{hexrepr(op)} | External function not implemented')


def unknownop(op):
    if op == 0:
        return
    return logger.warning(
        f'{hexrepr(op)} | Not found in the table')


def debugop(op, msg):
    return f'{hexrepr(self.pc)} | {hexrepr(op)} | {msg}'


class Emulator:
    def __init__(self, settings):
        self.settings = settings
        self.name = "CHIP-8"
        self.version = '0.0.1'
        self.pc = 0x200
        self.pc_increment = 2
        self.I = 0
        self.V = bytearray(16)
        self.MAX_STACK_SIZE = 32
        self.stack = []
        self.stack_pointer = -1
        self.is_init = False
        self.memory = bytearray(4096)
        self.fontset = None
        self.font = None
        self.delay_timer = 0
        # Stores the time elapsed, in milliseconds
        self.accumulator = 0

        self.keyboard_snap = [0 for i in range(16)]

        # External functions, related to graphics, input, etc.
        self.ext_functions = {}
        self.op_table = {}
        logger.info("Running Emulator...")

    def init_optable(self):
        """
        Initializes the OP Table, call this after implementing external functions, clear, draw, etc.
        """
        # self.ext_functions.get('clear', notimpl)

        # NOTE: To prevent exceptions, I have increased the size of the bytearray.
        # self.emulator.graphic_memory = bytearray(64*32)
        self.graphic_memory = bytearray(70*40)

        self.op_table = {
            0x0000: self.OP_KKK,
            0x1000: self.OP_NNN,
            0x2000: self.OP_NNN,
            0x3000: self.OP_XNN,
            0x4000: self.OP_XNN,
            0x5000: self.OP_XYK,
            0x6000: self.OP_XNN,
            0x7000: self.OP_XNN,
            0x8000: self.OP_XYK,
            0x9000: self.OP_XYK,
            0xA000: self.OP_NNN,
            0xB000: self.OP_NNN,
            0xC000: self.OP_XNN,
            0xD000: self.OP_XYN,
            0xE000: self.OP_XKK,
            0xF000: self.OP_XKK,
        }

        # For OP_KKK
        self.op_table_const = {
            0x00E0: self.ext_functions.get('clear', notimpl),
            0x00EE: self.OP_RETURN,
            # Simple halt function, for debugging purpose
            0x0FFF: self.ext_functions.get('halt', notimpl)
        }

        default_fontset = '8JCQkPAgYCAgcPAQ8IDw8BDwEPCQkPAQEPCA8BDw8IDwkPDwECBAQPCQ8JDw8JDwEPDwkPCQkOCQ4JDg8ICAgPDgkJCQ4PCA8IDw8IDwgIA='
        default_font = base64.b64decode(default_fontset)

        fontset = self.settings.get('fontset')
        if fontset is None:
            logger.warning(
                'No fontset found in settings!, Using default fontset')
            self.font = default_font
        else:
            try:
                self.font = base64.b64decode(fontset)
            except Exception as e:
                logger.warning(
                    'Error while reading fontset from settings, using default one')
                self.font = default_font

        self.load_to_memory(self.font, offset=0)

        self.is_init = True

    def load_to_memory(self, array_of_bytes, offset=0x200):
        # TODO: Add checks for out of bounds memory access, i.e >= 4096
        logger.debug(array_of_bytes)
        self.memory[offset: offset + len(array_of_bytes)] = array_of_bytes

    def execute_opcode(self, opcode):
        # logger.debug(f'{hexrepr(opcode)} | ')
        if not self.is_init:
            logger.error('Emulator not initialized ! Call init_optable()')
            self.quit(-5)

        self.pc_increment = 2
        try:
            self.op_table.get(opcode & 0xF000, unknownop)(opcode)
            self.pc += self.pc_increment
        except Exception as e:
            logger.exception(
                f'{hexrepr(opcode)} | Exception while executing this opcode\n')
            self.variable_dump()
            self.quit(exitcode=-4)

    def update_delay_timer(self):
        if self.delay_timer <= 0:
            self.delay_timer = 0
        else:
            if self.accumulator >= 16.66:
                self.accumulator -= 16.66
                self.delay_timer -= 1

    def add_time(self, time_in_ms):
        self.accumulator += time_in_ms

    def external(self, func_name):
        # This just uses the decorator pattern to add the function to the table
        # NOTE: Here the wrapper function will execute.
        def wrapper(f, *args, **kwargs):
            self.ext_functions[func_name] = f
            return f
        return wrapper

    def variable_dump(self):
        logger.info('Variable Dump')
        logger.info('-'*50)
        logger.info(f'I : {self.I}')
        logger.info(f'PC : {hexrepr(self.pc)}')
        logger.info('Registers:')
        for i in range(16):
            logger.info(f'V[{i}] = {self.V[i]}')
        logger.info('Stack:')
        logger.info(' '.join([str(i) for i in self.stack]))
        logger.info('-'*50)
        logger.info('Graphic memory')
        logger.info('-'*50)
        logger.info('\n'.join(['']+[' '.join(['%s' % self.graphic_memory[y*64 + x]
                                              for x in range(64)]) for y in range(32)]))
        logger.info('-'*50)

    def OP_KKK(self, op):
        self.op_table_const.get(op, unknownop)(op)

    def OP_NNN(self, op):
        K = (op & 0xF000) >> 12
        NNN = op & 0x0FFF
        if K == 1:
            logger.debug(
                f'{hexrepr(self.pc)} | {hexrepr(op)} | JUMP {hexrepr(NNN)}')
            # Jump to address
            self.pc = op & NNN
            # Already we have jumped, so stay at that position.
            self.pc_increment = 0
        if K == 2:
            # Calls subroutine
            logger.debug(
                f'{hexrepr(self.pc)} | {hexrepr(op)} | CALL {hexrepr(NNN)}')
            self.stack_pointer += 1
            if(self.stack_pointer >= self.MAX_STACK_SIZE):
                logger.critical('Stack overflow ! Maximum stack size reached')
                self.variable_dump()
                self.quit(exitcode=-2)
            self.stack.append(self.pc)
            self.pc = NNN
            self.pc_increment = 0
        if K == 0xA:
            # Sets the value of I = NNN
            logger.debug(
                f'{hexrepr(self.pc)} | {hexrepr(op)} | I = {hexrepr(NNN)}')
            self.I = NNN
        if K == 0xB:
            # PC = V0 + NNN
            logger.debug(
                f'{hexrepr(self.pc)} | {hexrepr(op)} | PC = V0 + {hexrepr(NNN)}')
            self.pc = self.V[0] + NNN
            self.pc_increment = 0

    def OP_XKK(self, op):
        S = (op & 0xF000) >> 12
        X = (op & 0x0F00) >> 8
        KK = (op & 0x00FF)

        if S == 0xE:
            if KK == 0x9E:
                # Operation if key() == V[x], then skip the block.
                if self.keyboard_snap[self.V[X]] == 1:
                    self.pc_increment = 4
            if KK == 0xA1:
                # Operation if key() != V[x], then skip the block.
                if self.keyboard_snap[self.V[X]] != 1:
                    self.pc_increment = 4

        if S == 0xF:
            if KK == 0x1E:
                logger.debug(f'{hexrepr(self.pc)} | {hexrepr(op)} | I += V{X}')
                # Limit to 16 bits
                self.I = (self.I + self.V[X]) & 0xFFFF

            if KK == 0x29:
                logger.debug(
                    f'{hexrepr(self.pc)} | {hexrepr(op)} | I = sprite_addr(V[{X}])')
                self.I = 5*self.V[X]

            if KK == 0x33:
                # Calculates BCD of value at register V[X]
                # TODO: Check for edge cases, i.e when I = 4096
                logger.debug(
                    f'{hexrepr(self.pc)} | {hexrepr(op)} | I{self.I}, I+1, I+2 = BCD(V{X})')
                self.memory[self.I] = (self.V[X] // 100) % 10
                self.memory[self.I+1] = (self.V[X] // 10) % 10
                self.memory[self.I+2] = (self.V[X]) % 10

            if KK == 0x55:
                # Dumps V0 - VX to memory address I
                logger.debug(
                    f'{hexrepr(self.pc)} | {hexrepr(op)} | Dump registers V0-V{X} to {self.I}')
                for i in range(0, X+1):
                    self.memory[self.I+i] = self.V[i]
            if KK == 0x65:
                # Loads V0 - VX from memory address I
                logger.debug(
                    f'{hexrepr(self.pc)} | {hexrepr(op)} | Load registers V0-V{X} from {self.I}')
                for i in range(0, X+1):
                    self.V[i] = self.memory[self.I+i]

            if KK == 7:
                # Sets the delay timer value to V[x]
                self.V[X] = int(self.delay_timer)
            if KK == 15:
                # Sets delay timer value
                print('Setting')
                self.delay_timer = self.V[X]

            if KK == 0x0a:
                # Halting operation, halt all operation until a key is pressed.
                # If it is pressed store it in V[X]
                self.settings['is_paused'] = True
                self.settings['temp'] = X

    def OP_XNN(self, op):
        S = (op & 0xF000) >> 12
        X = (op & 0x0F00) >> 8
        NN = (op & 0x00FF)

        if S == 3:
            if self.V[X] == NN:
                logger.debug(
                    f'{hexrepr(self.pc)} | {hexrepr(op)} | IF V[{X}] == {NN} SKIP')
                self.pc_increment = 4
        if S == 4:
            if self.V[X] != NN:
                logger.debug(
                    f'{hexrepr(self.pc)} | {hexrepr(op)} | IF V[{X}] != {NN} SKIP')
                self.pc_increment = 4
        if S == 6:
            logger.debug(f'{hexrepr(self.pc)} | {hexrepr(op)} | V[{X}] = {NN}')
            self.V[X] = NN
        if S == 7:
            logger.debug(
                f'{hexrepr(self.pc)} | {hexrepr(op)} | V[{X}] = V[{X}] + {NN}')
            self.V[X] = (self.V[X] + NN) & 0xff
        if S == 0xC:
            self.V[X] = random.randint(0, 255) & NN

    def OP_XYK(self, op):
        S = (op & 0xF000) >> 12
        X = (op & 0x0F00) >> 8
        Y = (op & 0x00F0) >> 4
        K = (op & 0x000F)

        if S == 5 and K == 0:
            if self.V[X] == self.V[Y]:
                logger.debug(
                    f'{hexrepr(self.pc)} | {hexrepr(op)} | IF V[{X}] == V[{Y}] SKIP')
                self.pc_increment = 4
        if S == 9 and K == 0:
            if self.V[X] != self.V[Y]:
                logger.debug(
                    f'{hexrepr(self.pc)} | {hexrepr(op)} | IF V[{X}] != V[{Y}] SKIP')
                self.pc_increment = 4

        if S == 8:
            if K == 0:
                # Assignment
                logger.debug(
                    f'{hexrepr(self.pc)} | {hexrepr(op)} | V[{X}] = V[{Y}]')
                self.V[X] = self.V[Y]
            if K == 1:
                # self.Vx = self.Vx | self.Vy
                logger.debug(
                    f'{hexrepr(self.pc)} | {hexrepr(op)} | V[{X}] |= V[{Y}]')
                self.V[X] = self.V[X] | self.V[Y]
            if K == 2:
                # self.Vx = self.Vx & self.Vy
                logger.debug(
                    f'{hexrepr(self.pc)} | {hexrepr(op)} | V[{X}] &= V[{Y}]')
                self.V[X] = self.V[X] & self.V[Y]
            if K == 3:
                # self.Vx = self.Vx ^ self.Vy
                logger.debug(
                    f'{hexrepr(self.pc)} | {hexrepr(op)} | V[{X}] ^= V[{Y}]')
                self.V[X] = self.V[X] ^ self.V[Y]
            if K == 4:
                # self.Vx = self.Vx + self.Vy
                logger.debug(
                    f'{hexrepr(self.pc)} | {hexrepr(op)} | V[{X}] += V[{Y}]')
                if ((self.V[X] + self.V[Y]) > 0xff):
                    self.V[0xF] = 1
                else:
                    self.V[0xF] = 0
                self.V[X] = (self.V[X] + self.V[Y]) & 0xFF
            if K == 5:
                logger.debug(
                    f'{hexrepr(self.pc)} | {hexrepr(op)} | V[{X}] -= V[{Y}]')
                # self.Vx = self.Vx - self.Vy
                # logger.debug(
                #    f'{self.V[X]}, {self.V[Y]} = {self.V[X]-self.V[Y]}')
                if self.V[X] > self.V[Y]:
                    self.V[0xF] = 0
                    self.V[X] = self.V[X] - self.V[Y]
                else:
                    self.V[0xF] = 1
                    self.V[X] = self.V[X] - self.V[Y] + 256

            if K == 6:
                logger.debug(
                    f'{hexrepr(self.pc)} | {hexrepr(op)} | V[{X}] >> 1')
                # self.Vx = self.Vx >> 1
                # Stores LSB in VF (for right shift)
                self.V[0xF] = self.V[X] & 1
                self.V[X] = self.V[X] >> 1
            if K == 7:
                # self.Vx = self.Vy- self.Vx
                logger.debug(
                    f'{hexrepr(self.pc)} | {hexrepr(op)} | V[{Y}] - V[{X}]')
                if self.V[Y] > self.V[X]:
                    self.V[0xF] = 0
                    self.V[X] = self.V[Y] - self.V[X]
                else:
                    self.V[0xF] = 1
                    self.V[X] = self.V[Y] - self.V[X] + 256
            if K == 0xE:
                # self.Vx = self.Vx << 1
                # Stores MSB in VF
                logger.debug(
                    f'{hexrepr(self.pc)} | {hexrepr(op)} | V[{X}] << 1')
                self.V[0xF] = (self.V[X] & 0b10000000) >> 7
                # The result is masked with 0xFF (255) so that it remains within a byte.
                self.V[X] = (self.V[X] << 1) & 0xFF

    def OP_XYN(self, op):
        # Opcode for drawing the sprite. DXYN
        self.ext_functions.get('draw', notimpl)(op)

    # Sub functions
    def OP_RETURN(self, op):
        try:
            logger.debug('Return')
            logger.debug(f'{hexrepr(self.pc)} | {hexrepr(op)} | Return')
            self.stack_pointer -= 1
            self.pc = self.stack.pop()
        except Exception as e:
            logger.exception('Illegal return statement')
            self.variable_dump()
            self.quit(exitcode=-3)

    def quit(self, exitcode=0):
        logger.info('Stopping emulator...')
        self.ext_functions.get('close', notimpl)(exitcode)

    def execute_opcode_from_memory(self):
        try:
            if self.pc >= 4096:
                # We have reached the end of memory.
                logger.info(
                    'No more instructions to execute! Halting emulator')
                return False

            self.execute_opcode(
                (self.memory[self.pc] << 8) | self.memory[self.pc+1])
            return True
        except Exception as e:
            logger.exception(
                'An error occured while fetching and executing opcode')
            self.variable_dump()
            self.quit(exitcode=-6)
            return False


if __name__ == '__main__':
    e = Emulator(
        {'fontset': '8JCQkPAgYCAgcPAQ8IDw8BDwEPCQkPAQEPCA8BDw8IDwkPDwECBAQPCQ8JDw8JDwEPDwkPCQkOCQ4JDg8ICAgPDgkJCQ4PCA8IDw8IDwgIA='})

    @ e.external('clear')
    def clear_display(opcode):
        logger.debug(debugop(opcode, 'Clearing display'))

    @ e.external('close')
    def close(opcode):
        sys.exit(opcode)

    rom = [0x1208, 0x9090, 0xf090, 0x9000, 0x00e0,
           0xa202, 0x6205, 0x6304, 0xd234, 0x1212]

    e.init_optable()
    for i in rom:
        e.execute_opcode(i)
