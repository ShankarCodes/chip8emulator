from src import emulator


def test_initialization():
    emu = emulator.Emulator(None)
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
