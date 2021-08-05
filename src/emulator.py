from log import create_logger

logger = create_logger(__name__)


def hexrepr(x): return f"{f'{x:#06x}': ^8}"


def notimpl(op): return logger.warning(
    f'Function for opcode ({hexrepr(op)}) not implemented')


def unknownop(op): return logger.warning(
    f'Opcode {hexrepr(op)} not found in the table')


class Emulator:
    def __init__(self, settings):
        self.settings = settings
        self.name = "CHIP-8"
        self.version = '0.0.1'
        self.pc = 0x200
        self.pc_increment = 2
        self.I = 0
        # External functions, related to graphics, input, etc.
        self.ext_functions = {}
        self.op_table = {}
        logger.info("Running Emulator...")

    def init_optable(self):
        """
        Initializes the OP Table, call this after implementing external functions, clear, draw, etc.
        """
        self.op_table = {
            0x00E0: self.ext_functions.get('clear', notimpl),
        }

    def execute_opcode(self, opcode):
        logger.debug(f"{hexrepr(opcode)} |")
        self.op_table.get(opcode, unknownop)(opcode)

    def external(self, func_name):

        def wrapper(f, *args, **kwargs):
            logger.info("Inside wrapper!")
            self.ext_functions[func_name] = f
            return f
        return wrapper


e = Emulator(None)


@e.external('clear')
def clear_display(opcode):
    logger.debug('Clearing display')


e.init_optable()
e.execute_opcode(0x2104)
e.execute_opcode(0x00E0)
