from chip8emulator import Emulator


def test_VX_equals_NN(emu: Emulator):
    # Test jump, i.e V[X] == NN
    emu.V[2] = 19  # 0x13
    emu.execute_opcode(0x3213)
    assert emu.pc_increment == 4
    assert emu.pc == 0x204

    # Test no jump, i.e V[X] != NN
    emu.execute_opcode(0x3212)
    assert emu.pc_increment == 2
    assert emu.pc == 0x206


def test_VX_not_equals_NN(emu: Emulator):
    emu.V[2] = 19  # 0x13

    # Test no jump, i.e V[X] == NN
    emu.execute_opcode(0x4213)
    assert emu.pc_increment == 2
    assert emu.pc == 0x202

    # Test jump, i.e V[X] != NN
    emu.execute_opcode(0x4212)
    assert emu.pc_increment == 4
    assert emu.pc == 0x206


def test_VX_equals_VY(emu: Emulator):
    emu.V[2] = 19
    emu.V[8] = 19
    emu.V[9] = 12

    # Test jump condition, V[X] == V[Y]
    emu.execute_opcode(0x5280)
    assert emu.pc_increment == 4
    assert emu.pc == 0x204

    # Test no jump condition, V[X] != V[Y]
    emu.execute_opcode(0x5290)
    assert emu.pc_increment == 2
    assert emu.pc == 0x206


def test_VX_not_equals_VY(emu: Emulator):
    emu.V[2] = 19
    emu.V[8] = 19
    emu.V[9] = 12

    # Test jump condition, V[X] != V[Y]
    emu.execute_opcode(0x9290)
    assert emu.pc_increment == 4
    assert emu.pc == 0x204

    # Test no jump condition, V[X] == V[Y]
    emu.execute_opcode(0x9280)
    assert emu.pc_increment == 2
    assert emu.pc == 0x206
