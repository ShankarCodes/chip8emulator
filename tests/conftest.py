import logging
import sys
import pytest
from src import emulator
from src import log


@pytest.fixture
def create_emulator():
    e = emulator.Emulator(None)

    @e.external('clear')
    def clear_display(opcode):
        print('Clearing display')

    @e.external('close')
    def close(opcode):
        sys.exit(opcode)

    @e.external('halt')
    def halt(opcode):
        emulator.logger.info("Got halt instruction!")
        sys.exit(0)

    e.init_optable()

    return e


@pytest.fixture
def emu(create_emulator):
    e = create_emulator
    e.V[3] = 211
    e.V[5] = 181
    return e
