from chip8emulator import Engine
if __name__ == '__main__':
    engine = Engine()
    engine.load_settings()
    engine.init()
    engine.run()
