import os
import shutil
import sys
import re
import zipfile
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


def tester(dir, test):
    temp_dir = 'temp'
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.mkdir(temp_dir)
    copy_folder(dir, temp_dir)

    output = ""
    for root, f in file_generator(temp_dir):
        if f.lower().endswith('.tst') or f.lower().endswith('.cmp'):
            os.remove(os.path.join(root, f))
    copy_folder(os.path.join('grader/tests', 'p' + str(1)), temp_dir, permissions='a+rwx')
    filename = os.path.join(temp_dir, test)
    if os.path.exists(filename + '.hdl'):
        os.rename(filename + '.hdl', filename + '.hidden')

    filename = os.path.join(temp_dir, test)
    if not os.path.exists(filename + '.hidden'):
        output = test + 'file_missing'
    os.rename(filename + '.hidden', filename + '.hdl')
    f = read_file(filename + '.hdl')
    if 'builtin' in f.lower():
        output = test + 'built_in_chip'
    response = hardware_simulator(temp_dir, test)
    os.rename(filename + '.hdl', filename + '.hidden')
    if len(response) > 0:
        output = test + ' diff_with_chip ' + response

    #cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)
    if output == "":
        output = 'Congratulations! all tests passed successfully!'
    return output

def main():
    print(tester(sys.argv[1], sys.argv[2]))

if __name__ == '__main__':
    main()
