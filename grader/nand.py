import os
import subprocess
import re
import config
import shutil


def file_generator(folder):
    """iterate over all non-hidden files under folder"""
    for root, dirs, files in tuple(os.walk(folder)):
        files = [f for f in files if not f[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.']
        for f in files:
            yield root, f


def run_emulator(emulator, extension):
    def f(folder, test, is_dir=False):
        if is_dir:
            folder = os.path.join(folder, test)
        result = subprocess.run([emulator, os.path.join(folder, test + extension)],
                                capture_output=True)
        return result.stderr.decode('utf-8')
    return f


hardware_simulator = run_emulator(config.HARDWARE_SIMULATOR, '.tst')
assembler = run_emulator(config.ASSEMBLER, '.asm')
cpu_emulator = run_emulator(config.CPU_EMULATOR, '.tst')
vm_emulator = run_emulator(config.VM_EMULATOR, '.tst')


def jack_compiler(file):
    result = subprocess.run([config.JACK_COMPILER, file], capture_output=True)
    return result.stderr.decode('utf-8')


class StudentProgram:
    def __init__(self, folder, project_num):
        self.timeout = 15
        self.folder = folder
        if project_num == 6:
            self.program = 'HackAssembler'
        elif project_num in [7, 8]:
            self.program = 'VMTranslator'
        elif project_num == 10:
            self.program = 'JackAnalyzer'
        else:  # project_num == 11
            self.program = 'JackCompiler'

        lang = os.path.join(folder, 'lang.txt')
        if not os.path.exists(lang):
            self.language = ''
        else:
            with open(lang, 'r') as lang_file:
                self.language = lang_file.read().lower()

    def compile(self):
        language = self.language
        folder = self.folder
        program_path = os.path.join(folder, self.program)
        if re.search('python', language) or re.search('ruby', language) or re.search('perl', language) \
                or re.search('nodejs', language) or re.search('swift', language) or re.search('php', language):
            return 0, ''
        elif re.search('java', language):
            compiler = config.JAVAC
            flags = [os.path.join(folder, file) for file in os.listdir(folder) if file[-5:].lower() == '.java']
        elif re.search('c\+\+', language) or re.search('cpp', language):
            compiler = config.CPP
            files = [os.path.join(folder, file) for file in os.listdir(folder) if file[-4:].lower() == '.cpp']
            flags = ['-Wall'] + files + ['-o', program_path]
        elif re.search('c#', language) or re.search('f#', language) or re.search('vb', language):
            compiler = config.DOTNET
            flags = ['build', folder]
        elif re.search('c', language):
            compiler = config.C
            files = [os.path.join(folder, file) for file in os.listdir(folder) if file[-2:].lower() == '.c']
            flags = ['-Wall'] + files + ['-o', program_path]
        elif re.search('go', language):
            compiler = config.GO
            flags = ['build', '-o', program_path] + \
                    [os.path.join(folder, file) for file in os.listdir(folder) if file[-3:].lower() == '.go']
        elif re.search('file', language):
            return 0, ''
        elif language == '':
            return 1, 'The lang.txt file is missing'
        else:
            return 1, 'lang.txt file should contain only the name of a valid programming language'
        result = subprocess.run([compiler] + flags, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        output = ' '.join([compiler] + flags) + '\n'
        output += result.stdout.decode('utf-8', errors='ignore')
        return result.returncode, output

    def run(self, input_path):
        language = self.language
        folder = self.folder
        program_path = os.path.join(folder, self.program)
        flags = []
        if re.search('python', language):
            run = config.PYTHON
            extension = '.py'
        elif re.search('java', language):
            run = config.JAVA
            flags = ['-cp', folder]
            extension = ''
            program_path = self.program
        elif re.search('c#', language) or re.search('f#', language) or re.search('vb', language):
            run = config.DOTNET
            program_path = ''
            flags = ['run', '--project', folder]
            extension = ''
        elif re.search('ruby', language):
            run = config.RUBY
            extension = '.rb'
        elif re.search('perl', language):
            run = config.PERL
            extension = '.pl'
            flags = ['-I', self.folder]
        elif re.search('nodejs', language):
            run = config.NODEJS
            extension = '.js'
        elif re.search('swift', language):
            run = config.SWIFT
            extension = '.swift'
        elif re.search('php', language):
            run = config.PHP
            extension = '.php'
        elif re.search('c', language) or re.search('c\+\+', language) or re.search('cpp', language) or \
                re.search('go', language):
            run = program_path
            program_path = ''
            extension = ''
        elif re.search('file', language):
            files = []
            for f in os.listdir(folder):
                if f.lower().endswith('.hack'):
                    files.append(f)
            for f in files:
                if os.path.exists(os.path.join(folder, f[:-5])):
                    shutil.move(os.path.join(folder, f), os.path.join(folder, f[:-5], f))
            return ''
        try:
            print(' '.join([run] + flags + [program_path + extension, input_path]) + '\n')
            result = subprocess.run([run] + flags + [program_path + extension, input_path],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    timeout=self.timeout)
            print(result.stdout.decode('utf-8', errors='ignore'))
            output = ' '.join([run] + flags + [program_path + extension, input_path]) + '\n'
            output += result.stdout.decode('utf-8', errors='ignore')
            return output
        except subprocess.TimeoutExpired:
            return 'Timed out after {} seconds'.format(self.timeout)
