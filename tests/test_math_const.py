from src import emulator


def test_set_register_to_n(emu: emulator.Emulator):
    # Tests assignment
    # Sets all registers from 0-15 to 0,2,4,6,8,...28
    for i in range(15):
        emu.execute_opcode(0x6000 | (i << 8) | (i*2))

    for i in range(15):
        assert emu.V[i] == i*2


def test_add_n_to_register(emu: emulator.Emulator):
    # Tests adding N to a register
    # Adds 2,4,6,8 .... to V[1]
    for i in range(15):
        emu.execute_opcode(0x7000 | (1 << 8) | (i*2))
    assert emu.V[1] == sum([i*2 for i in range(0, 15)])


def test_add_n_overflow_to_register(emu: emulator.Emulator):
    tmp = emu.V[0xF]
    # Add 255 to the register, max is 255 bytes
    emu.execute_opcode(0x71ff)
    assert emu.V[1] == 0xff
    # Tests if V[F] has not been affected.
    assert emu.V[0xF] == tmp

    # Execute again to check for overflow, adding 42.
    emu.execute_opcode(0x712a)
    assert emu.V[1] == 41
    assert emu.V[0xF] == tmp


def test_assign_V_x_to_V_y(emu: emulator.Emulator):
    emu.V[3] = 19
    emu.V[12] = 45
    emu.V[4] = 70

    # V[3] = V[12] = 45
    emu.execute_opcode(0x83c0)
    assert emu.V[12] == 45
    assert emu.V[3] == 45

    # V[12] = V[4] = 70
    emu.execute_opcode(0x8c40)
    assert emu.V[3] == 45
    assert emu.V[12] == 70
    assert emu.V[4] == 70


def test_add_vy_to_vx(emu: emulator.Emulator):
    # Add Vy to Vx , Vx = Vx + Vy
    # Test for no overflow condition
    for i in range(0, 6):
        for j in range(0, 6):
            emu.V[3] = i
            emu.V[5] = j

            emu.execute_opcode(0x8354)

            assert emu.V[3] == i + j
            assert emu.V[5] == j
            assert emu.V[0xF] == 0


def test_add_vy_to_vx_overflow(emu: emulator.Emulator):
    emu.V[3] = 231
    emu.V[4] = 81

    emu.execute_opcode(0x8344)
    assert emu.V[4] == 81
    assert emu.V[0xF] == 1
    assert emu.V[3] == 56


def test_sub_vy_from_vx(emu: emulator.Emulator):
    # Subtract Vy from Vx , Vx = Vx - Vy
    # Test for no overflow condition
    for i in range(20, 30):
        for j in range(0, 10):
            emu.V[3] = i
            emu.V[5] = j

            emu.execute_opcode(0x8355)

            assert emu.V[3] == i - j
            assert emu.V[5] == j
            assert emu.V[0xF] == 0


def test_sub_vy_from_vx_overflow(emu: emulator.Emulator):
    emu.V[3] = 81
    emu.V[4] = 231

    emu.execute_opcode(0x8345)
    assert emu.V[4] == 231
    assert emu.V[0xF] == 1
    assert emu.V[3] == 106
