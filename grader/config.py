import platform, os, json

with open('grader/config.json', 'r') as f:
    constants = json.load(f)
globals().update(constants)

if platform.system().lower() == 'windows':
    script_extension = '.bat'
else:
    script_extension = '.sh'
HARDWARE_SIMULATOR = os.path.join(NAND, 'HardwareSimulator' + script_extension)
CPU_EMULATOR = os.path.join(NAND, 'CPUEmulator' + script_extension)
ASSEMBLER = os.path.join(NAND, 'Assembler' + script_extension)
VM_EMULATOR = os.path.join(NAND, 'VMEmulator' + script_extension)
JACK_COMPILER = os.path.join(NAND, 'JackCompiler' + script_extension)
