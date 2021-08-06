import logging
import sys
import pytest
from src import emulator
from src import log


def create_emulator():
    e = emulator.Emulator(None)

    @e.external('clear')
    def clear_display(opcode):
        print('Clearing display')

    @e.external('close')
    def close(opcode):
        sys.exit(opcode)

    e.init_optable()

    return e


@pytest.fixture
def emu():
    e = create_emulator()
    e.V[3] = 211
    e.V[5] = 181
    return e
