chips1 = {
    'Not': 4,
    'And': 4,
    'Or': 6,
    'Xor': 6,
    'Mux': 8,
    'DMux': 8,
    'Not16': 5,
    'And16': 5,
    'Or16': 5,
    'Mux16': 5,
    'Or8Way': 8,
    'Mux4Way16': 9,
    'Mux8Way16': 9,
    'DMux4Way': 9,
    'DMux8Way': 9
}

chips2 = {
    'ALU': 52,
    'Add16': 12,
    'FullAdder': 12,
    'HalfAdder': 9,
    'Inc16': 15
}

chips3 = {
    'Bit': 10,
    'PC': 18,
    'RAM64': 19,
    'RAM8': 19,
    'Register': 10,
    'RAM16K': 8,
    'RAM4K': 8,
    'RAM512': 8
}

chips4 = {
    'Mult': 35,
    'Fill': 65
}

chips5 = {
    'Memory': 25,
    'CPU': 53,
    'Computer': 22,
    'ComputerAdd': 6,
    'ComputerMax': 8,
    'ComputerRect': 8
}

tests6 = {
    'Add': 10,
    'Max': 20,
    'Rect': 30,
    'Pong': 40
}

tests6_file = {
    'MaxL': 50,
    'Rect': 50,
}

tests7 = {
    'StaticTest': 20,
    'PointerTest': 20,
    'BasicTest': 20,
    'StackTest': 20,
    'SimpleAdd': 20
}

tests8 = {
    'BasicLoop': 16,
    'FibonacciElement': 16,
    'FibonacciSeries': 16,
    'NestedCall': 16,
    'SimpleFunction': 16,
    'StaticsTest': 16
}

tests11 = {
    'Average': 25,
    'ComplexArrays': 25,
    'ConvertToBin': 25,
    'Seven': 25
}

tests12 = {
    'ArrayTest': 17,
    'MathTest': 17,
    'MemoryTest': 17,
    'Array': 20,
    'Keyboard': 20,
    'Math': 20,
    'Memory': 20,
    'Output': 20,
    'Screen': 20,
    'String': 20,
    'Sys': 20,

}


class ProjectError:
    def __init__(self, penalty, err_msg):
        self.penalty = penalty
        self.err_msg = err_msg


err_project0 = {'file_missing': ProjectError(100, 'file.txt is missing'),
                'file_contents': ProjectError(100, 'Wrong file contents')}


def hardware_err(chips):
    err = {'built_in_chip': ProjectError(chips, 'Do not use builtin chip'),
           'file_missing': ProjectError(chips, 'Chip does not exist'),
           'diff_with_chip': ProjectError(chips, 'The chip failed to pass the test')}
    return err


err_project4 = {'assembly_error': ProjectError(chips4, 'Assembly failed'),
                'file_missing': ProjectError(chips4, 'File is missing'),
                'diff_with_test': ProjectError(chips4, 'Test failed')}


def software_err(tests):
    err = {'file_missing': ProjectError(tests, 'File is missing'),
           'test_failed': ProjectError(tests, 'Test failed'),
           'wrong_dir': ProjectError(8, 'Wrong directory for output files')}
    return err


err_project12 = {'compilation_error': ProjectError(tests12, 'Compilation failed'),
                 'diff_with_test': ProjectError(tests12, 'Test failed')}

err_projects = {
    0: err_project0,
    1: hardware_err(chips1),
    2: hardware_err(chips2),
    3: hardware_err(chips3),
    4: err_project4,
    5: hardware_err(chips5),
    6: software_err(tests6),
    '6_file': software_err(tests6_file),
    7: software_err(tests7),
    8: software_err(tests8),
    10: software_err(15),
    11: software_err(tests11),
    12: err_project12
}


def feedback_format(penalty, test, err_msg, log=''):
    if log != '':
        log = ':\n' + log + '\n'
    else:
        log = '\n'
    return '*(-{}) '.format(penalty) + test + ': ' + err_msg + log


class FormattedFeedback:
    def __init__(self, project_num):
        self.grade = 100
        self.feedback = ''
        self.project_num = project_num
        self.errors = []

    def append(self, test, error, log=''):
        p_err = err_projects[self.project_num][error]
        penalty = p_err.penalty
        if error == 'wrong_dir' and error in self.errors:
            penalty = 0  # prevent duplicate penalties in case of wrong directory
        if isinstance(penalty, dict):
            penalty = p_err.penalty[test]
        self.grade -= penalty
        self.feedback += feedback_format(penalty, test, p_err.err_msg, log)
        self.errors.append(error)

    def get(self):
        return max(0, self.grade), self.feedback.strip()
