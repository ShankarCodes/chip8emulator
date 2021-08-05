import sys
import pytest
from src import emulator


@pytest.fixture
def emu():
    e = emulator.Emulator(None)

    @e.external('clear')
    def clear_display(opcode):
        print('Clearing display')

    @e.external('close')
    def close(opcode):
        sys.exit(opcode)

    e.init_optable()
    return e
