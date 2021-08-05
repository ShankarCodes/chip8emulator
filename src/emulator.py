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
            0x3000: self.OP_XYN,
            0x4000: self.OP_XYN,
            0x5000: self.OP_XYK,
            0x6000: self.OP_XYN,
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
        }
        self.is_init = True

    def execute_opcode(self, opcode):
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
            # Jump to address
            self.pc = op & NNN
            # Already we have jumped, so stay at that position.
            self.pc_increment = 0
        if K == 2:
            # Calls subroutine
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
            self.pc = self.V[0] + NNN
            self.pc_increment = 0

    def OP_XKK(self, op):
        pass

    def OP_XNN(self, op):
        pass

    def OP_XYK(self, op):
        S = (op & 0xF000) >> 12
        X = (op & 0x0F00) >> 8
        Y = (op & 0x00F0) >> 4
        K = (op & 0x000F)

        if S == 8:
            if K == 0:
                # Assignment
                V[X] = V[Y]
            if K == 1:
                # Vx = Vx | Vy
                V[X] = V[X] | V[Y]
            if K == 2:
                # Vx = Vx & Vy
                V[X] = V[X] & V[Y]
            if K == 3:
                # Vx = Vx ^ Vy
                V[X] = V[X] ^ V[Y]
            if K == 4:
                # Vx = Vx + Vy
                V[X] = V[X] + V[Y]
            if K == 5:
                # Vx = Vx - Vy
                V[X] = V[X] - V[Y]
            if K == 6:
                # Vx = Vx >> 1
                V[X] = V[X] >> 1
            if K == 7:
                # Vx = Vx - Vy
                V[X] = V[Y] - V[X]
            if K == 0xE:
                # Vx = Vx << 1
                V[X] = V[X] << 1

    def OP_XYN(self, op):
        pass

    # Sub functions
    def OP_RETURN(self, op):
        try:
            logger.info('Return')
            self.stack_pointer -= 1
            self.pc = self.stack.pop()
        except Exception as e:
            logger.exception('Illegal return statement')
            self.variable_dump()
            self.quit(exitcode=-3)

    def quit(self, exitcode=0):
        logger.info('Stopping emulator...')
        self.ext_functions.get('close', notimpl)(exitcode)


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
