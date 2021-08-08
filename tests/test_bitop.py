from chip8emulator import Emulator


def test_bitwise_or(emu: Emulator):
    emu.execute_opcode(0x8351)
    assert emu.V[3] == 211 | 181


def test_bitwise_and(emu: Emulator):
    emu.execute_opcode(0x8352)
    assert emu.V[3] == 211 & 181


def test_bitwise_xor(emu: Emulator):
    emu.execute_opcode(0x8353)
    assert emu.V[3] == 211 ^ 181


def test_left_shift(emu: Emulator):
    # Shifts to the left and checks if MSB is stored in Vf
    emu.execute_opcode(0x830E)
    assert emu.V[0xF] == (211 & 0b10000000) >> 7
    assert emu.V[3] == (211 << 1) & 0xFF


def test_right_shift(emu: Emulator):
    # Shifts right and checks if LSB is stored in Vf
    emu.execute_opcode(0x8306)
    assert emu.V[0xF] == 211 & 1
    assert emu.V[3] == 211 >> 1


def test_bcd(emu: Emulator):
    emu.V[2] = 164
    emu.I = 100
    emu.execute_opcode(0xF233)
    assert emu.memory[100] == 1
    assert emu.memory[101] == 6
    assert emu.memory[102] == 4

    emu.V[2] = 219
    emu.I = 100
    emu.execute_opcode(0xF233)
    assert emu.memory[100] == 2
    assert emu.memory[101] == 1
    assert emu.memory[102] == 9

    emu.V[2] = 0
    emu.I = 100
    emu.execute_opcode(0xF233)
    assert emu.memory[100] == 0
    assert emu.memory[101] == 0
    assert emu.memory[102] == 0
