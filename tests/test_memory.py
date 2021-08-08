import os
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


def test_rom_loading(emu: emulator.Emulator):
    rombytes = b""
    with open(os.path.join('roms', 'TEST_ROM_DISPLAY_A'), 'rb') as rom:
        rombytes = rom.read()
    emu.load_to_memory(bytearray(rombytes))
    for i, byte in enumerate(rombytes):
        assert emu.memory[0x200 + i] == byte

    # Test memory is written correctly.
    assert emu.memory[0x200] == 0x00
    assert emu.memory[0x201] == 0xe0
    assert emu.memory[0x202] == 0x6d
    assert emu.memory[0x203] == 0x0a
    assert emu.memory[0x204] == 0xfd
    assert emu.memory[0x205] == 0x29
    assert emu.memory[0x206] == 0x63
    assert emu.memory[0x207] == 0x0f
    assert emu.memory[0x208] == 0x61
    assert emu.memory[0x209] == 0x0a
    assert emu.memory[0x20a] == 0xd1
    assert emu.memory[0x20b] == 0x34
    assert emu.memory[0x20c] == 0x0f
    assert emu.memory[0x20d] == 0xff
    # Tests if following the program, the memory is 0
    assert emu.memory[0x20e:] == bytearray(0xfff - 0x20e + 1)


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


def test_setting_I_to_sprite_address(emu: emulator.Emulator):
    emu.V[3] = 0xA
    emu.execute_opcode(0xf329)
    assert emu.I == 50

    emu.V[3] = 0x2
    emu.execute_opcode(0xf329)
    assert emu.I == 10


def test_dumping_registers():
    emu = emulator.Emulator({})
    emu.init_optable()
    emu.I = 100
    emu.V[0] = 7
    emu.V[1] = 21
    emu.V[2] = 38
    emu.V[3] = 15
    emu.V[4] = 17
    emu.V[5] = 41
    # Copies V0-V4 at memory location I
    emu.execute_opcode(0xF455)
    assert emu.I == 100
    assert emu.memory[100] == 7
    assert emu.memory[101] == 21
    assert emu.memory[102] == 38
    assert emu.memory[103] == 15
    assert emu.memory[104] == 17
    # Tests that no other memory has been altered
    assert emu.memory[105:] == bytearray(0xfff - 105 + 1)
    assert emu.memory[99] == 0


def test_loading_registers():
    emu = emulator.Emulator({})
    emu.init_optable()
    emu.memory[99] = 65
    emu.memory[100] = 17
    emu.memory[101] = 91
    emu.memory[102] = 3
    emu.memory[103] = 21
    emu.memory[104] = 39
    emu.memory[105] = 53

    # Loads from I until V4 from I = 100
    emu.I = 100
    emu.execute_opcode(0xF465)
    assert emu.I == 100

    assert emu.V[0] == 17
    assert emu.V[1] == 91
    assert emu.V[2] == 3
    assert emu.V[3] == 21
    assert emu.V[4] == 39
    # Checks if no other register has been modified
    for i in range(5, 16):
        assert emu.V[i] == 0


def test_execution_ends_when_pc_greater_than_memory(create_emulator: emulator.Emulator):
    while create_emulator.execute_opcode_from_memory():
        pass
    assert create_emulator.pc == 4096


def test_execute_opcode_from_memory(create_emulator: emulator.Emulator):
    # Test some basic setting of registers
    create_emulator.load_to_memory(
        bytearray([0x61, 0x37, 0x62, 0x45, 0x63, 0x1a]))
    while create_emulator.execute_opcode_from_memory():
        pass
    assert create_emulator.V[1] == 0x37
    assert create_emulator.V[2] == 0x45
    assert create_emulator.V[3] == 0x1a
