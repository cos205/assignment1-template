import os, shutil, sys, re, zipfile
import subprocess

from penalties import FormattedFeedback
from nand import hardware_simulator, assembler, cpu_emulator, vm_emulator, StudentProgram, \
                 file_generator, jack_compiler
import config
from chardet import detect
import secrets


def read_file(filename):
    with open(filename, 'rb') as f:
        try:
            bytes = f.read()
            return bytes.decode('utf-8').lower()
        except:
            d = detect(bytes)
            return bytes.decode(d['encoding']).lower()

def copy_folder(source, destination, permissions=None):
    shutil.copytree(source, destination, dirs_exist_ok=True)
    if permissions:
        subprocess.run(['chmod', permissions, destination])


def find_subfolder(folder, file):
    """finds sub-folder which contains a file"""
    for root, f in file_generator(folder):
        if f.lower() == file.lower():
            return root
    return folder


def copy_upwards(folder, extension, correct=[]):
    """ copy files with specific extension from sub-folders upwards
        and fix upper/lower case mistakes """
    for root, f in file_generator(folder):
        if f.split('.')[-1].lower() == extension:
            try:
                print(f'copying {os.path.join(root, f)} into {folder}')
                shutil.move(os.path.join(root, f), folder)
            except Exception as e:
                print('Exception occurred:')
                print(e)
                pass
            for c in correct:
                if f.lower() == c.lower() + extension and f != c + extension:
                    os.rename(os.path.join(folder, f), os.path.join(folder, c + extension))


def project0(temp_dir):
    feedback = FormattedFeedback(0)
    copy_upwards(temp_dir, 'txt')
    # Delete possible existing test files
    for root, f in file_generator(temp_dir):
        if f.lower().endswith('.cmp'):
            os.remove(os.path.join(root, f))
    copy_folder(os.path.join('tests', 'p0'), temp_dir, permissions='a+rwx')
    cmp = read_file(os.path.join('tests', 'p0', 'cmp.txt'))
    if not os.path.exists(os.path.join(temp_dir, 'file.txt')):
        feedback.append('', 'file_missing')
        return feedback.get()
    file = read_file(os.path.join(temp_dir, 'file.txt'))
    if file != cmp:
        feedback.append('', 'file_contents')
    return feedback.get()


def projects_123(project_num):
    if project_num == 1:
        tests = ['And', 'DMux', 'DMux8Way', 'Mux16', 'Mux8Way16', 'Not16', 'Or16', 'Xor',
                 'And16', 'DMux4Way', 'Mux', 'Mux4Way16', 'Not', 'Or', 'Or8Way']
    elif project_num == 2:
        tests = ['ALU', 'Add16', 'FullAdder', 'HalfAdder', 'Inc16']
    elif project_num == 3:
        tests = ['Bit', 'PC', 'RAM64', 'RAM8', 'Register', 'RAM16K', 'RAM4K', 'RAM512']

    def tester(temp_dir):
        feedback = FormattedFeedback(project_num)
        # copy_upwards(temp_dir, 'hdl', tests)
        # Delete possible existing test files
        for root, f in file_generator(temp_dir):
            if f.lower().endswith('.tst') or f.lower().endswith('.cmp'):
                os.remove(os.path.join(root, f))
        copy_folder(os.path.join('grader/tests', 'p' + str(project_num)), temp_dir, permissions='a+rwx')

        for test in tests:
            filename = os.path.join(temp_dir, test)
            if os.path.exists(filename + '.hdl'):
                os.rename(filename + '.hdl', filename + '.hidden')

        for test in tests:
            filename = os.path.join(temp_dir, test)
            if not os.path.exists(filename + '.hidden'):
                feedback.append(test, 'file_missing')
                continue
            os.rename(filename + '.hidden', filename + '.hdl')
            f = read_file(filename + '.hdl')
            if 'builtin' in f.lower():
                feedback.append(test, 'built_in_chip')
            output = hardware_simulator(temp_dir, test)
            os.rename(filename + '.hdl', filename + '.hidden')
            if len(output) > 0:
                feedback.append(test, 'diff_with_chip', output)

        return feedback.get()

    return tester


def project4(temp_dir):
    print('temp_dir:', temp_dir)
    tests = ['Mult', 'Fill']
    copy_upwards(temp_dir, 'asm', tests)
    # Delete possible existing test files
    for root, f in file_generator(temp_dir):
        if f.lower().endswith('.tst') or f.lower().endswith('.cmp'):
            os.remove(os.path.join(root, f))
    copy_folder(os.path.join('tests', 'p4'), temp_dir, permissions='a+rwx')
    feedback = FormattedFeedback(4)
    for test in tests:
        filename = os.path.join(temp_dir, test)
        print('checking file:', filename + '.asm')
        if not os.path.exists(filename + '.asm'):
            print(f'''File doen't exist:''', filename + '.asm')
            feedback.append(test, 'file_missing')
            continue
        output = assembler(temp_dir, test)
        if len(output) > 0:
            print('assembler error')
            feedback.append(test, 'assembly_error', output)
            continue
        output = cpu_emulator(temp_dir, test)
        if len(output) > 0:
            print('comparison error:', output)
            feedback.append(test, 'diff_with_test', output)

    return feedback.get()


def project5(temp_dir):
    tests = ['Memory', 'CPU', 'Computer']
    computer_tests = ['ComputerAdd', 'ComputerMax', 'ComputerRect']
    feedback = FormattedFeedback(5)
    copy_upwards(temp_dir, 'hdl', tests)
    # Delete possible existing test files
    for root, f in file_generator(temp_dir):
        if f.lower().endswith('.tst') or f.lower().endswith('.cmp'):
            os.remove(os.path.join(root, f))
    copy_folder(os.path.join('tests', 'p5'), temp_dir, permissions='a+rwx')

    for test in tests:
        filename = os.path.join(temp_dir, test)
        if not os.path.exists(filename + '.hdl'):
            feedback.append(test, 'file_missing')
            continue
        f = read_file(filename + '.hdl')
        if 'builtin' in f.lower():
            feedback.append(test, 'built_in_chip')
        if test == 'Computer':
            break
        output = hardware_simulator(temp_dir, test)
        if len(output) > 0:
            feedback.append(test, 'diff_with_chip', output)

    if not os.path.exists(os.path.join(temp_dir, 'Computer.hdl')):
        feedback.append('Computer', 'file_missing')
    else:
        os.replace(os.path.join(temp_dir, 'CPU_DMT.hdl'), os.path.join(temp_dir, 'CPU.hdl'))
        os.replace(os.path.join(temp_dir, 'Memory_DMT.hdl'), os.path.join(temp_dir, 'Memory.hdl'))
        for test in computer_tests:
            output = hardware_simulator(temp_dir, test)
            if len(output) > 0:
                feedback.append(test, 'diff_with_chip', output)

    return feedback.get()


# compare files ignoring whitespace
def compare_file(file1, file2):
    cmp_file = read_file(file1)
    xml_file = read_file(file2)
    return re.sub("\s*", "", cmp_file) == re.sub("\s*", "", xml_file)


# Execute one test for project 10 (one iteration of the loop inside sotfware_project)
def check_10(temp_dir, test, output, feedback):
    for root, f in file_generator(os.path.join(temp_dir, test)):
        if f.lower().endswith('.cmp'):
            full_path = os.path.join(root, f)
            if not os.path.exists(full_path[:-3] + 'xml'):
                feedback.append(test, 'file_missing', output)
                continue
            if not compare_file(full_path, full_path[:-3] + 'xml'):
                feedback.append(test, 'test_failed', f[:-3] + 'xml is different from ' + f)


def software_project(project_num):
    # tests with only one file to translate
    one_file = ['Add', 'Max', 'MaxL', 'Rect', 'Pong'] +\
               ['StaticTest', 'PointerTest', 'BasicTest', 'StackTest', 'SimpleAdd'] +\
               ['BasicLoop', 'FibonacciSeries', 'SimpleFunction']

    def tester(temp_dir):
        if project_num == 6:
            tests = ['Add', 'Max', 'Rect', 'Pong']
            input_extension = '.asm'
            output_extension = '.hack'
        elif project_num == 7:
            tests = ['StaticTest', 'PointerTest', 'BasicTest', 'StackTest', 'SimpleAdd']
            input_extension = '.vm'
            output_extension = '.asm'
            emulator = cpu_emulator
        elif project_num == 8:
            tests = ['BasicLoop', 'FibonacciElement', 'FibonacciSeries', 'NestedCall',
                     'SimpleFunction', 'StaticsTest']
            input_extension = '.vm'
            output_extension = '.asm'
            emulator = cpu_emulator
        elif project_num == 10:
            tests = ['ArrayTest', 'Square', 'ExpressionlessSquare']
            output_extension = '.xml'
        else:  # project_num == 11
            tests = ['Average', 'ComplexArrays', 'ConvertToBin', 'Seven']
            input_extension = '.jack'
            output_extension = '.vm'
            emulator = vm_emulator

        feedback = FormattedFeedback(project_num)
        temp_dir = find_subfolder(temp_dir, 'lang.txt')
        if os.path.exists(os.path.join(temp_dir, 'lang.txt')):
            lang = read_file(os.path.join(temp_dir, 'lang.txt'))
        else:
            lang = ''
        if not re.search('file', lang):
            # Delete possible already existing output files
            for root, f in file_generator(temp_dir):
                if f.lower().endswith(output_extension):
                    os.remove(os.path.join(root, f))
        elif project_num == 6:
            tests = ['MaxL', 'Rect']
            feedback = FormattedFeedback('6_file')
        copy_folder(os.path.join('tests', 'p' + str(project_num)), temp_dir, permissions='a+rwx')
        program = StudentProgram(temp_dir, project_num)
        return_code, output = program.compile()
        if return_code:
            grade = 0
            feedback = 'Problems encountered in the compilation\n' + output
            return grade, feedback.strip()

        for test in tests:
            dirname = os.path.join(temp_dir, test)
            filename = os.path.join(dirname, test)
            if test in one_file:
                output = program.run(filename + input_extension)
            else:
                output = program.run(dirname)
            if project_num == 10:
                check_10(temp_dir, test, output, feedback)
                continue
            if os.path.exists(dirname + output_extension):
                shutil.move(dirname + output_extension, filename + output_extension)
                feedback.append(test, 'wrong_dir')
            if os.path.exists(test + output_extension):
                shutil.move(test + output_extension, filename + output_extension)
                feedback.append(test, 'wrong_dir')
            if (not os.path.exists(filename + output_extension) and project_num != 11) or \
                (project_num == 11 and not os.path.exists(os.path.join(dirname, 'Main.vm'))):
                print(os.path.join(dirname, 'Main.vm'))
                feedback.append(test, 'file_missing', output)
                continue
            if project_num == 6:
                if not compare_file(filename + '.cmp', filename + output_extension):
                    feedback.append(test, 'test_failed',
                                    test + output_extension + ' is wrong')
                continue
            output = emulator(temp_dir, test, is_dir=True)
            if len(output) > 0:
                feedback.append(test, 'test_failed', output)

        return feedback.get()

    return tester


def project12(temp_dir):
    tests = ['Array', 'Math', 'Memory']
    os_files = ['Array', 'Keyboard', 'Math', 'Memory', 'Output', 'Screen', 'String', 'Sys']
    copy_upwards(temp_dir, 'jack', tests)
    feedback = FormattedFeedback(12)
    # Delete possible already existing vm files
    for root, f in file_generator(temp_dir):
        if f.lower().endswith('vm'):
            os.remove(os.path.join(root, f))
    copy_folder(os.path.join('tests', 'p12'), temp_dir, permissions='a+rwx')

    os.mkdir(os.path.join(temp_dir, 'studentOS'))
    for file in os_files:
        output = jack_compiler(os.path.join(temp_dir, file + '.jack'))
        if len(output) > 0:
            feedback.append(file, 'compilation_error', output)
        else:
            shutil.copy(os.path.join(temp_dir, file + '.vm'), os.path.join(temp_dir, 'studentOS'))

    failed = False
    passed_all = True
    errors = ''
    for t in tests:
        test = t + 'Test'
        copy_folder(os.path.join(temp_dir, 'OS'), os.path.join(temp_dir, test))
        copy_folder(os.path.join(temp_dir, 'studentOS'), os.path.join(temp_dir, test), permissions='a+rwx')
        output = vm_emulator(os.path.join(temp_dir, test), test)
        if len(output) == 0:  # passed test
            continue
        # give a second chance - try to test the file separately
        elif not os.path.exists(os.path.join(temp_dir, 'studentOS', t + '.vm')):
            feedback.append(test, 'diff_with_test', output)
            passed_all = False
            continue
        copy_folder(os.path.join(temp_dir, 'OS'), os.path.join(temp_dir, test), permissions='a+rwx')
        shutil.copy(os.path.join(temp_dir, 'studentOS', t + '.vm'), os.path.join(temp_dir, test))
        output2 = vm_emulator(os.path.join(temp_dir, test), test)
        if len(output2) > 0:
            message = 'All OS files: ' + output + 'Only {}.vm: '.format(t) + output2
            feedback.append(test, 'diff_with_test', message)
            passed_all = False
        elif not failed:
            failed = True
            errors = output
            where = test
    # if all os files don't work together but only separately
    if failed and passed_all:
        feedback.append(where, 'diff_with_test', errors)

    return feedback.get()


check = {
    0: project0,
    1: projects_123(1),
    2: projects_123(2),
    3: projects_123(3),
    4: project4,
    5: project5,
    6: software_project(6),
    7: software_project(7),
    8: software_project(8),
    10: software_project(10),
    11: software_project(11),
    12: project12
}


def grader(dirname, project_num, temp_dir):
    random_dir = 'temp-' + secrets.token_urlsafe(6)
    temp_dir = os.path.join(temp_dir, random_dir)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.mkdir(temp_dir)
    copy_folder(dirname, temp_dir)
    grade, feedback = check[project_num](temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)
    if feedback == '':
        feedback = 'Congratulations! all tests passed successfully!'
    return grade, feedback


def main():
    if len(sys.argv) < 3:
        print('Usage: python grader.py <dirname> <project number>')
        print('For example: python grader.py project3dir 3')
    else:
        if not os.path.exists("grader/temp"):
            os.mkdir("grader/temp")
        grade, feedback = grader(sys.argv[1], int(sys.argv[2]), "grader/temp")
        print('Grade:', grade)
        print('Feedback:')
        print(feedback)

if __name__ == '__main__':
    main()
