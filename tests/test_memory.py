from src import emulator


def test_initialization():
    emu = emulator.Emulator({})
    assert len(emu.stack) == 0
    assert emu.pc == 0x200
    assert emu.pc_increment == 2
    assert emu.I == 0
    assert emu.is_init == False
    assert emu.stack_pointer == -1
    assert len(emu.V) == 16
    assert emu.V == bytearray(16)
    assert emu.memory == bytearray(4096)
    assert emu.op_table == {}
    assert emu.ext_functions == {}

    @emu.external('clear')
    def clear(op):
        print('Statement')

    emu.init_optable()
    assert emu.op_table is not None
    assert emu.is_init
    assert emu.ext_functions is not None
    assert emu.ext_functions['clear'] == clear


def test_default_font_loading():
    emu = emulator.Emulator({})
    assert emu.fontset is None
    emu.init_optable()

    fontset = [
        0xF0, 0x90, 0x90, 0x90, 0xF0, 0x20, 0x60, 0x20, 0x20, 0x70,
        0xF0, 0x10, 0xF0, 0x80, 0xF0, 0xF0, 0x10, 0xF0, 0x10, 0xF0,
        0x90, 0x90, 0xF0, 0x10, 0x10, 0xF0, 0x80, 0xF0, 0x10, 0xF0,
        0xF0, 0x80, 0xF0, 0x90, 0xF0, 0xF0, 0x10, 0x20, 0x40, 0x40,
        0xF0, 0x90, 0xF0, 0x90, 0xF0, 0xF0, 0x90, 0xF0, 0x10, 0xF0,
        0xF0, 0x90, 0xF0, 0x90, 0x90, 0xE0, 0x90, 0xE0, 0x90, 0xE0,
        0xF0, 0x80, 0x80, 0x80, 0xF0, 0xE0, 0x90, 0x90, 0x90, 0xE0,
        0xF0, 0x80, 0xF0, 0x80, 0xF0, 0xF0, 0x80, 0xF0, 0x80, 0x80, ]
    for i in range(0, 80):
        assert emu.memory[i] == fontset[i]


def test_setting_I(emu: emulator.Emulator):
    emu.execute_opcode(0xA217)
    assert emu.I == 0x217
    emu.execute_opcode(0xA0be)
    assert emu.I == 0x0be


def test_add_V_x_to_I(emu: emulator.Emulator):
    emu.V[2] = 8
    emu.V[3] = 12
    emu.execute_opcode(0xF21E)
    emu.execute_opcode(0xF31E)
    assert emu.I == 20
