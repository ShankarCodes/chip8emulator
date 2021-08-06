import sys
from .log import create_logger

logger = create_logger(__name__)


def hexrepr(x): return f"{f'{x:#06x}': ^8}"


def notimpl(op): return logger.warning(
    f'{hexrepr(op)} | External function not implemented')


def unknownop(op): return logger.warning(
    f'{hexrepr(op)} | Not found in the table')


def debugop(op, msg):
    return f'{hexrepr(op)} | {msg}'


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

        # External functions, related to graphics, input, etc.
        self.ext_functions = {}
        self.op_table = {}
        logger.info("Running Emulator...")

    def init_optable(self):
        """
        Initializes the OP Table, call this after implementing external functions, clear, draw, etc.
        """
        #self.ext_functions.get('clear', notimpl)

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
        self.is_init = True

    def execute_opcode(self, opcode):
        #logger.debug(f'{hexrepr(opcode)} | ')
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
        for i in range(15):
            logger.info(f'V[{i}] = {self.V[i]}')
        logger.info('Stack:')
        logger.info(' '.join([str(i) for i in self.stack]))
        logger.info('-'*50)

    def OP_KKK(self, op):
        self.op_table_const.get(op, unknownop)(op)

    def OP_NNN(self, op):
        K = (op & 0xF000) >> 12
        NNN = op & 0x0FFF
        if K == 1:
            logger.debug(f'{hexrepr(op)} | JUMP {hexrepr(NNN)}')
            # Jump to address
            self.pc = op & NNN
            # Already we have jumped, so stay at that position.
            self.pc_increment = 0
        if K == 2:
            # Calls subroutine
            logger.debug(f'{hexrepr(op)} | CALL {hexrepr(NNN)}')
            self.stack_pointer += 1
            if(self.stack_pointer >= self.MAX_STACK_SIZE):
                logger.critical('Stack overflow ! Maximum stack size reached')
                self.variable_dump()
                self.quit(exitcode=-2)
            self.stack.append(self.pc)
            self.pc = NNN
            self.pc_increment = 0
        if K == 0xB:
            # PC = V0 + NNN
            logger.debug(f'{hexrepr(op)} | PC = V0 + {hexrepr(NNN)}')
            self.pc = self.V[0] + NNN
            self.pc_increment = 0

    def OP_XKK(self, op):
        pass

    def OP_XNN(self, op):
        S = (op & 0xF000) >> 12
        X = (op & 0x0F00) >> 8
        NN = (op & 0x00FF)

        if S == 3:
            if self.V[X] == NN:
                logger.debug(f'{hexrepr(op)} | IF V[{X}] == {NN} SKIP')
                self.pc_increment = 4
        if S == 4:
            if self.V[X] != NN:
                logger.debug(f'{hexrepr(op)} | IF V[{X}] != {NN} SKIP')
                self.pc_increment = 4
        if S == 6:
            logger.debug(f'{hexrepr(op)} | V[{X}] = {NN}')
            self.V[X] = NN
        if S == 7:
            logger.debug(f'{hexrepr(op)} | V[{X}] = V[{X}] + {NN}')
            self.V[X] = (self.V[X] + NN) & 0xff

    def OP_XYK(self, op):
        S = (op & 0xF000) >> 12
        X = (op & 0x0F00) >> 8
        Y = (op & 0x00F0) >> 4
        K = (op & 0x000F)

        if S == 5 and K == 0:
            if self.V[X] == self.V[Y]:
                logger.debug(f'{hexrepr(op)} | IF V[{X}] == V[{Y}] SKIP')
                self.pc_increment = 4
        if S == 9 and K == 0:
            if self.V[X] != self.V[Y]:
                logger.debug(f'{hexrepr(op)} | IF V[{X}] != V[{Y}] SKIP')
                self.pc_increment = 4

        if S == 8:
            if K == 0:
                # Assignment
                logger.debug(f'{hexrepr(op)} | V[{X}] = V[{Y}]')
                self.V[X] = self.V[Y]
            if K == 1:
                # self.Vx = self.Vx | self.Vy
                logger.debug(f'{hexrepr(op)} | V[{X}] |= V[{Y}]')
                self.V[X] = self.V[X] | self.V[Y]
            if K == 2:
                # self.Vx = self.Vx & self.Vy
                logger.debug(f'{hexrepr(op)} | V[{X}] &= V[{Y}]')
                self.V[X] = self.V[X] & self.V[Y]
            if K == 3:
                # self.Vx = self.Vx ^ self.Vy
                logger.debug(f'{hexrepr(op)} | V[{X}] ^= V[{Y}]')
                self.V[X] = self.V[X] ^ self.V[Y]
            if K == 4:
                # self.Vx = self.Vx + self.Vy
                logger.debug(f'{hexrepr(op)} | V[{X}] += V[{Y}]')
                if ((self.V[X] + self.V[Y]) > 0xff):
                    self.V[0xF] = 1
                else:
                    self.V[0xF] = 0
                self.V[X] = (self.V[X] + self.V[Y]) & 0xFF
            if K == 5:
                logger.debug(f'{hexrepr(op)} | V[{X}] -= V[{Y}]')
                # self.Vx = self.Vx - self.Vy
                logger.debug(
                    f'{self.V[X]}, {self.V[Y]} = {self.V[X]-self.V[Y]}')
                if self.V[X] > self.V[Y]:
                    self.V[0xF] = 0
                    self.V[X] = self.V[X] - self.V[Y]
                else:
                    self.V[0xF] = 1
                    self.V[X] = self.V[X] - self.V[Y] + 256

            if K == 6:
                logger.debug(f'{hexrepr(op)} | V[{X}] >> 1')
                # self.Vx = self.Vx >> 1
                # Stores LSB in VF (for right shift)
                self.V[0xF] = self.V[X] & 1
                self.V[X] = self.V[X] >> 1
            if K == 7:
                # self.Vx = self.Vy- self.Vx
                logger.debug(f'{hexrepr(op)} | V[{Y}] - V[{X}]')
                self.V[X] = self.V[Y] - self.V[X]
            if K == 0xE:
                # self.Vx = self.Vx << 1
                # Stores MSB in VF
                logger.debug(f'{hexrepr(op)} | V[{X}] << 1')
                self.V[0xF] = (self.V[X] & 0b10000000) >> 7
                # The result is masked with 0xFF (255) so that it remains within a byte.
                self.V[X] = (self.V[X] << 1) & 0xFF

    def OP_XYN(self, op):
        pass

    # Sub functions
    def OP_RETURN(self, op):
        try:
            logger.info('Return')
            logger.debug(f'{hexrepr(op)} | Return')
            self.stack_pointer -= 1
            self.pc = self.stack.pop()
        except Exception as e:
            logger.exception('Illegal return statement')
            self.variable_dump()
            self.quit(exitcode=-3)

    def quit(self, exitcode=0):
        logger.info('Stopping emulator...')
        self.ext_functions.get('close', notimpl)(exitcode)


if __name__ == '__main__':
    e = Emulator(None)

    @e.external('clear')
    def clear_display(opcode):
        logger.debug(debugop(opcode, 'Clearing display'))

    @e.external('close')
    def close(opcode):
        sys.exit(opcode)

    rom = [0x1208, 0x9090, 0xf090, 0x9000, 0x00e0,
           0xa202, 0x6205, 0x6304, 0xd234, 0x1212]

    e.init_optable()
    for i in rom:
        e.execute_opcode(i)
