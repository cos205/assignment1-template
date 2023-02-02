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

def copy_folder(source, destination, permssions=None):
    shutil.copytree(source, destination, dirs_exist_ok=True)
    if permssions:
        subprocess.run(['chmod', permssions, '-R', destination])


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
                #print(f'copying {os.path.join(root, f)} into {folder}')
                shutil.move(os.path.join(root, f), folder)
            except Exception as e:
                print('Exception occurred:')
                print(e)
                pass
            for c in correct:
                if f.lower() == c.lower() + extension and f != c + extension:
                    os.rename(os.path.join(folder, f), os.path.join(folder, c + extension))

def projects_1(t):
    tests = ['And', 'DMux', 'DMux8Way', 'Mux16', 'Mux8Way16', 'Not16', 'Or16', 'Xor',
                 'And16', 'DMux4Way', 'Mux', 'Mux4Way16', 'Not', 'Or', 'Or8Way']

    def tester(temp_dir):
        feedback = FormattedFeedback(1)
        copy_upwards(temp_dir, 'hdl', tests)
        # Delete possible existing test files
        for root, f in file_generator(temp_dir):
            if f.lower().endswith('.tst') or f.lower().endswith('.cmp'):
                os.remove(os.path.join(root, f))
        copy_folder(os.path.join('grader/tests', 'p' + str(1)), temp_dir, permssions='a+rwx')

        for test in tests:
            filename = os.path.join(temp_dir, test)
            if os.path.exists(filename + '.hdl'):
                os.rename(filename + '.hdl', filename + '.hidden')

        for test in [t]:
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

# compare files ignoring whitespace
def compare_file(file1, file2):
    cmp_file = read_file(file1)
    xml_file = read_file(file2)
    return re.sub("\s*", "", cmp_file) == re.sub("\s*", "", xml_file)

def grader(filename, temp_dir, test):
    random_dir = 'temp-' + secrets.token_urlsafe(6)
    temp_dir = os.path.join(temp_dir, random_dir)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.mkdir(temp_dir)
    os.mkdir(os.path.join(temp_dir, 'src'))
    shutil.copytree(filename, os.path.join(temp_dir,'src'), symlinks=False, ignore=None, ignore_dangling_symlinks=False, dirs_exist_ok=True)
    grade, feedback = projects_1(test)(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)
    if feedback == '':
        feedback = 'Congratulations! all tests passed successfully!'
    return grade, feedback


def main():
    if len(sys.argv) < 3:
        print('Usage: python grader.py <dirname> <test>')
        print('For example: python grader.py project3.zip 3')
    else:
        temp = os.path.join('grader','temp')
        if not os.path.exists(temp):
            os.mkdir(temp)
        grade, feedback = grader(sys.argv[1], temp , sys.argv[2])
        print(feedback)


if __name__ == '__main__':
    main()
