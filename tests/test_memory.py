import base64
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


def test_loading_font_from_settings():
    test_font = base64.b64encode(bytearray(
        [0x20, 0x10, 0x13, 0xaa, 0xea, 0x17, 0x00, 0x1, 0xff, 0x37, 0x6d])).decode('utf-8')
    emu = emulator.Emulator({
        'fontset': test_font
    })
    emu.init_optable()
    offset = 0
    assert emu.memory[offset + 0] == 0x20
    assert emu.memory[offset + 1] == 0x10
    assert emu.memory[offset + 2] == 0x13
    assert emu.memory[offset + 3] == 0xaa
    assert emu.memory[offset + 4] == 0xea
    assert emu.memory[offset + 5] == 0x17
    assert emu.memory[offset + 6] == 0x00
    assert emu.memory[offset + 7] == 0x01
    assert emu.memory[offset + 8] == 0xff
    assert emu.memory[offset + 9] == 0x37
    assert emu.memory[offset + 10] == 0x6d


def test_font_loading_other_memory_unchanged():
    test_font = base64.b64encode(bytearray(
        [0x20, 0x10, 0x13, 0xaa, 0xea, 0x17, 0x00, 0x1, 0xff, 0x37, 0x6d])).decode('utf-8')
    emu = emulator.Emulator({
        'fontset': test_font
    })
    emu.init_optable()
    assert emu.memory[11:] == bytearray(4085)
    for i in range(11, 4096):
        assert emu.memory[i] == 0


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
