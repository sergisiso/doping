''' Configuration of pytest '''

import os
import re
import subprocess
import pytest


def pytest_addoption(parser):
    ''' Add the --compile option to the pytest executable '''
    parser.addoption("--compile", action="store_true", default=False,
                     help="Compile output code when tests produce code")


@pytest.fixture
def compiler(request):
    ''' Return a Compiler object '''
    if request.config.getoption("--compile"):
        return GCCCompiler()
    return MockCompiler()


class Compiler():
    ''' Compiler abstract class '''
    # pylint: disable=no-self-use, unused-argument
    flags = ""

    def compile(self, filename):
        ''' Compile the given source file '''
        NotImplementedError("Abstract class")

    def run(self, match=None, verbosity=0):
        ''' Run the compiled binary file '''
        NotImplementedError("Abstract class")


class MockCompiler(Compiler):
    ''' Always returns true '''

    def compile(self, filename):
        return True

    def run(self, match=None, verbosity=0):
        return True


class GCCCompiler(Compiler):
    ''' Gcc compiler '''

    flags = "gcc"

    def __init__(self):
        self._base_path = None
        self._source_file = None
        self._successful_compilation = False

    def compile(self, filename):
        self._base_path = os.path.dirname(filename)
        self._source_file = os.path.basename(filename)

        # Save the current path, it needs to be restored on exit
        current_path = os.getcwd()
        os.chdir(self._base_path)

        if not os.environ['DOPING_ROOT']:
            print("DOPING_ROOT environment variable must be defined")

        header_path = os.path.join(os.environ['DOPING_ROOT'], 'bin')
        library_path = os.path.join(header_path, 'libdoping.so')
        command = (self.flags + ' ' + self._source_file + " -o test_binary.exe -I" +
                   header_path + ' ' + library_path + " -ldl")

        try:
            # Invoke the compiler command
            compiler_invokation = subprocess.Popen(
                command.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (output, error) = compiler_invokation.communicate()
            print(os.getcwd())
            print(command)
            print(output.decode('UTF-8'))
            print(error.decode('UTF-8'))

            # Return to the working directory
            os.chdir(current_path)
            if compiler_invokation.returncode == 0:
                self._successful_compilation = True

            return self._successful_compilation

        except OSError as err:
            print("Failed to run: '" + command + "' with error " + str(err))
            # Return to the working directory
            os.chdir(current_path)
            return False

        os.chdir(current_path)
        return False

    def run(self, match=None, verbosity=0):
        if not self._successful_compilation:
            print("Failed to run, it needs to successfully compile first.")
            return False

        # Save the current path, it needs to be restored on exit
        current_path = os.getcwd()
        os.chdir(self._base_path)

        # Prepare command to run
        my_env = {**os.environ, 'DOPING_VERBOSE': str(verbosity)}
        command = "./test_binary.exe"

        try:
            # Run the compiled application
            compiler_invokation = subprocess.Popen(
                command, env=my_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (output, error) = compiler_invokation.communicate()
            print(os.getcwd())
            print(command)
            print(output.decode('UTF-8'))
            print(error.decode('UTF-8'))
            os.chdir(current_path)
            if match is not None:
                return re.search(match, str(output) + str(error))
            return True
        except OSError as err:
            print("Failed to run: '" + command + "' with error " + str(err))
            # Return to the working directory
            os.chdir(current_path)
            return False

        os.chdir(current_path)
        return False
