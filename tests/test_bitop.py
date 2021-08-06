from src import emulator


def test_bitwise_or(emu: emulator.Emulator):
    emu.execute_opcode(0x8351)
    assert emu.V[3] == 211 | 181


def test_bitwise_and(emu: emulator.Emulator):
    emu.execute_opcode(0x8352)
    assert emu.V[3] == 211 & 181


def test_bitwise_xor(emu: emulator.Emulator):
    emu.execute_opcode(0x8353)
    assert emu.V[3] == 211 ^ 181


def test_left_shift(emu: emulator.Emulator):
    # Shifts to the left and checks if MSB is stored in Vf
    emu.execute_opcode(0x830E)
    assert emu.V[0xF] == (211 & 0b10000000) >> 7
    assert emu.V[3] == (211 << 1) & 0xFF


def test_right_shift(emu: emulator.Emulator):
    # Shifts right and checks if LSB is stored in Vf
    emu.execute_opcode(0x8306)
    assert emu.V[0xF] == 211 & 1
    assert emu.V[3] == 211 >> 1
