#!/usr/bin/env python
import sys
import os
import subprocess


VERSION = '0.0.0'
GIT_COMMIT = ''
PYTHON_VERSION = f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'
GIT_XLTRAIL_DIFF = 'git-xltrail-diff.exe'

FILE_EXTENSIONS = ['xls', 'xlt', 'xla', 'xlam', 'xlsx', 'xlsm', 'xlsb', 'xltx', 'xltm',
                   'doc', 'docm', 'dotm'
                   'ppt', 'ppa' 'pptm', 'potm', 'ppsm', 'ppam']
GIT_ATTRIBUTES = ['*.' + file_ext + ' diff=xltrail' for file_ext in FILE_EXTENSIONS]
GIT_IGNORE = ['~$*.' + file_ext for file_ext in FILE_EXTENSIONS]


def is_git_repository(path):
    cmd = subprocess.run(['git', 'rev-parse'], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         universal_newlines=True)
    if not cmd.stderr.split('\n')[0]:
        return True
    return False


class Installer:

    def __init__(self, mode='global', path=None):
        if mode == 'global' and path:
            raise ValueError('must not specify repository path when installing globally')

        if mode == 'local' and not path:
            raise ValueError('must specify repository path when installing locally')

        if mode == 'local' and not is_git_repository(path):
            raise ValueError('not a Git repository')

        self.mode = mode
        self.path = path

        # global config dir (only set when running in `global` mode)
        self.git_global_config_dir = self.get_global_gitconfig_dir() if self.mode == 'global' else None

        # paths to .gitattributes and .gitignore
        self.git_attributes_path = self.get_git_attributes_path()
        self.git_ignore_path = self.get_git_ignore_path()

    def install(self):
        # 1. gitconfig: set-up diff.xltrail.command
        self.execute(['diff.xltrail.command', GIT_XLTRAIL_DIFF])

        # 2. set-up gitattributes (define differ for Excel file formats)
        self.update_git_file(path=self.git_attributes_path, keys=GIT_ATTRIBUTES, operation='SET')

        # 3. set-up gitignore (define differ for Excel file formats)
        self.update_git_file(path=self.git_ignore_path, keys=GIT_IGNORE, operation='SET')

        # when in global mode, update gitconfig
        if self.mode == 'global':
            # set core.attributesfile
            self.execute(['core.attributesfile', self.git_attributes_path])
            # set core.excludesfile
            self.execute(['core.excludesfile', self.git_ignore_path])

    def uninstall(self):
        # 1. gitconfig: remove diff.xltrail.command from gitconfig
        keys = self.execute(['--list']).split('\n')
        if [key for key in keys if key.startswith('diff.xltrail.command')]:
            self.execute(['--remove-section', 'diff.xltrail'])

        # 2. gitattributes: remove keys
        gitattributes_keys = self.update_git_file(path=self.git_attributes_path, keys=GIT_ATTRIBUTES,
                                                  operation='REMOVE')
        # when in global mode and gitattributes is empty, update gitconfig and delete gitattributes
        if not gitattributes_keys:
            if self.mode == 'global':
                self.execute(['--unset', 'core.attributesfile'])
            self.delete_git_file(self.git_attributes_path)

        # 3. gitignore: remove keys
        gitignore_keys = self.update_git_file(path=self.git_attributes_path, keys=GIT_IGNORE, operation='REMOVE')
        # when in global mode and gitignore is empty, update gitconfig and delete gitignore
        if not gitignore_keys:
            if self.mode == 'global':
                self.execute(['--unset', 'core.excludesfile'])
            self.delete_git_file(self.git_ignore_path)

    def execute(self, args):
        command = ['git', 'config']
        if self.mode == 'global':
            command.append('--global')
        command += args
        return subprocess.run(command, cwd=self.path, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              universal_newlines=True).stdout

    def get_global_gitconfig_dir(self):
        # put .gitattributes in same folder as global .gitconfig
        # determine .gitconfig path
        # this requires Git 2.8+ (March 2016)
        f = self.execute(['--list', '--show-origin'])
        p = self.execute(['--list'])

        f = f.split('\n')[0]
        p = p.split('\n')[0]

        return f[:f.index(p)][5:][:-11]

    def get_git_attributes_path(self):
        if self.mode == 'local':
            return os.path.join(self.path, '.gitattributes')

        # check if core.attributesfile is configured
        core_attributesfile = self.execute(['--get', 'core.attributesfile']).split('\n')[0]
        if core_attributesfile:
            return core_attributesfile

        # put .gitattributes into same directory as global .gitconfig
        return os.path.join(self.git_global_config_dir, '.gitattributes')

    def get_git_ignore_path(self):
        if self.mode == 'local':
            return os.path.join(self.path, '.gitignore')

        # check if core.excludesfile is configured
        core_excludesfile = self.execute(['--get', 'core.excludesfile']).split('\n')[0]
        if core_excludesfile:
            return core_excludesfile

        # put .gitattributes into same directory as global .gitconfig
        return os.path.join(self.git_global_config_dir, '.gitignore')

    def update_git_file(self, path, keys, operation):
        assert operation in ('SET', 'REMOVE')
        if os.path.exists(path):
            with open(path, 'r') as f:
                content = [line for line in f.read().split('\n') if line]
        else:
            content = []

        if operation == 'SET':
            # create union set: keys + existing content
            content = sorted(list(set(content).union(set(keys))))
        else:
            # remove keys from content
            content = [line for line in content if line and line not in keys]

        if content:
            with open(path, 'w') as f:
                f.writelines('\n'.join(content))

        return content

    def delete_git_file(self, path):
        if os.path.exists(path):
            os.remove(path)


GIT_XLTRAIL_VERSION = f'git-xltrail/{VERSION} (windows; Python {PYTHON_VERSION}); git {GIT_COMMIT}'

HELP_GENERIC = f"""{GIT_XLTRAIL_VERSION}
git xltrail <command> [<args>]\n
Git xltrail is a system for managing Excel workbook files in
association with a Git repository. Git xltrail:
* installs a special git-diff for Excel files 
* makes Git ignore temporary Excel files via .gitignore\n
Commands
--------\n
* git xltrail env:
    Display the Git xltrail environment.
* git xltrail install:
    Install Git xltrail.
* git xltrail uninstall:
    Uninstall Git xltrail.
* git xltrail version:
    Report the version number."""

HELP_ENV = 'git xltrail env\n\nDisplay the current Git xltrail environment.'

HELP_INSTALL = """git xltrail install [options]\n
Perform the following actions to ensure that Git xltrail is setup properly:\n
* Set up .gitignore to make Git ignore temporary Excel files.
* Install a git-diff drop-in replacement for Excel files.\n
Options:\n
Without any options, git xltrail install will setup the Excel differ and
.gitignore globally.\n
* --local:
    Sets the .gitignore filters and the git-diff Excel drop-in replacement
    in the local repository, instead of the global git config (~/.gitconfig)."""

HELP_UNINSTALL = """git xltrail uninstall [options]\n
Uninstalls Git xltrail:\n
Options:\n
Without any options, git xltrail uninstall will remove the git-diff drop-in
replacement for Excel files and .gitignore globally.\n
* --local:
    Removes the .gitignore filters and the git-diff Excel drop-in replacement
    in the local repository, instead globally."""


class CommandParser:

    def __init__(self, args):
        self.args = args

    def execute(self):
        if not self.args:
            return self.help()

        command = self.args[0]
        args = self.args[1:]

        # do not process if command does not exist
        if not hasattr(self, command):
            return print(
                f"""Error: unknown command "{command}" for "git xltrail"\nRun 'git xltrail help' for usage.""")

        # execute command
        getattr(self, command)(*args)

    def version(self, *args):
        print(GIT_XLTRAIL_VERSION)

    def env(self):
        current_path = os.getcwd()
        p = GIT_XLTRAIL_VERSION + '\n\n'
        p += 'LocalWorkingDir=' + (current_path if is_git_repository(current_path) else '') + '\n'
        p += 'LocalGitIgnore=' + (
            os.path.join(current_path, '.gitignore') if is_git_repository(current_path) else '') + '\n'
        p += 'LocalGitAttributes=' + (
            os.path.join(current_path, '.gitattributes') if is_git_repository(current_path) else '') + '\n'
        print(p)

    def help(self, *args):
        module = sys.modules[__name__]
        arg = args[0] if args else None
        if arg is None:
            print(HELP_GENERIC)
        else:
            help_text = 'HELP_%s' % arg.upper()
            if not hasattr(module, help_text):
                print(f'Sorry, no usage text found for "{arg}"')
            else:
                print(getattr(module, help_text))

    def install(self, *args):
        if args:
            if args[0] == '--local':
                installer = Installer(mode='local', path=os.getcwd())
            else:
                return print(
                    f"""Invalid option "{args[0]}" for "git xltrail install"\nRun 'git xltrail help' for usage.""")
        else:
            installer = Installer(mode='global')
        installer.install()

    def uninstall(self, *args):
        if args:
            if args[0] == '--local':
                installer = Installer(mode='local', path=os.getcwd())
            else:
                return print(
                    f"""Invalid option "{args[0]}" for "git xltrail install"\nRun 'git xltrail help' for usage.""")
        else:
            installer = Installer(mode='global')
        installer.uninstall()


if __name__ == '__main__':
    command_parser = CommandParser(sys.argv[1:])
    command_parser.execute()
