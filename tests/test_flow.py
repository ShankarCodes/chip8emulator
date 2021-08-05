import pytest
from src import emulator


def test_jump(emu: emulator.Emulator):
    # Tests jump statement, i.e goto
    assert emu.pc == 0x0200
    assert emu.pc_increment == 2
    # Jump to address 205
    emu.execute_opcode(0x1000)
    assert emu.pc == 0x000
    assert emu.pc_increment == 0

    emu.execute_opcode(0x1378)
    assert emu.pc == 0x378
    assert emu.pc_increment == 0

    emu.execute_opcode(0x00E0)
    assert emu.pc_increment == 2
    assert emu.pc == 0x378 + 2


def test_call(emu: emulator.Emulator):
    # Tests that the emulator can call subroutines and return back
    # Also check for edge cases such as stack overflow

    assert emu.stack == []
    # Calls subroutine at memory location 0x308
    emu.execute_opcode(0x2308)

    assert len(emu.stack) > 0
    assert emu.stack_pointer == 0
    assert emu.stack[-1] == 0x200
    assert emu.pc_increment == 0
    assert emu.pc == 0x308

    # Dummy instructions
    emu.execute_opcode(0x0000)
    emu.execute_opcode(0x0000)
    assert emu.pc == 0x308 + 4

    # Calls subroutine at memory location 0x78a
    emu.execute_opcode(0x278a)
    assert emu.pc == 0x78a
    assert emu.stack_pointer == 1
    assert emu.pc_increment == 0
    assert emu.stack[-1] == 0x30c
    assert emu.stack == [0x200, 0x30c]


def test_call_stack_overflow(emu: emulator.Emulator):
    # Maximum of 5 jumps
    emu.MAX_STACK_SIZE = 5
    emu.execute_opcode(0x2308)
    emu.execute_opcode(0x2408)
    emu.execute_opcode(0x2508)
    emu.execute_opcode(0x2608)
    emu.execute_opcode(0x2708)
    with pytest.raises(SystemExit) as exc:
        emu.execute_opcode(0x2808)
    assert exc.value.code == -2


def test_return(emu: emulator.Emulator):
    emu.execute_opcode(0x2308)
    emu.execute_opcode(0x2408)
    # Return
    emu.execute_opcode(0x00EE)
    assert emu.stack_pointer == 0
    assert emu.pc_increment == 2
    assert emu.pc == 0x30a
    assert emu.stack[-1] == 0x200

    emu.execute_opcode(0x2508)
    emu.execute_opcode(0x2608)
    emu.execute_opcode(0x2708)
    assert emu.stack_pointer == 3

    # We test the previous PC + 2 because, if no increment is there
    # The program gets stuck in endless loop
    emu.execute_opcode(0x00EE)
    assert emu.pc == 0x60a
    emu.execute_opcode(0x00EE)
    assert emu.pc == 0x50a
    assert emu.stack_pointer == 1
    emu.execute_opcode(0x00EE)
    assert emu.stack_pointer == 0
    assert emu.stack[-1] == 0x200
    emu.execute_opcode(0x00EE)
    assert emu.pc == 0x202
    assert emu.stack_pointer == -1
    assert emu.stack == []


def test_return_no_jumps(emu: emulator.Emulator):
    assert emu.stack_pointer == -1
    assert emu.stack == []
    with pytest.raises(SystemExit) as exc:
        emu.execute_opcode(0x00EE)
    assert exc.value.code == -3


def test_jump_to_NNN(emu: emulator.Emulator):
    # PC = V0 + NNN
    assert emu.pc == 0x200
    emu.V[0] = 121
    emu.execute_opcode(0xB320)
    assert emu.pc_increment == 0
    assert emu.pc == 121 + 0x320
