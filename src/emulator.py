class Emulator:
    def __init__(self, settings):
        self.settings = settings
        self.name = "CHIP-8"
        self.version = '0.0.1'

    def execute_opcode(self, opcode):
        print(f"{opcode: >10} |")
