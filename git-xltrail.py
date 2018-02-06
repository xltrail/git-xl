#!/usr/bin/env python
import sys
import os
import subprocess


VERSION = '0.0.0'
PYTHON_VERSION = f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'
GIT_XLTRAIL_DIFF = 'git-xltrail-diff.exe'

GIT_ATTRIBUTES = [
	'*.xls diff=xltrail',
	'*.xlt diff=xltrail',
	'*.xla diff=xltrail',
	'*.xlm diff=xltrail',
	'*.xlsx diff=xltrail',
	'*.xlsm diff=xltrail',
	'*.xlsb diff=xltrail'
]

class Installer:

	def __init__(self, mode='global', path=None):
		if mode == 'global' and path:
			raise ValueError('must not specify repository path when installing globally')

		if mode == 'local' and not path:
			raise ValueError('must specify repository path when installing locally')

		self.mode = mode
		self.path = path

	def install(self):
		self.execute(['diff.xltrail.command', GIT_XLTRAIL_DIFF])
		git_attributes = self.git_attributes()

		if os.path.exists(git_attributes):
			with open(git_attributes, 'r') as f:
				content = f.read().split('\n')
		else:
			content = []
		content = list(set(content).union(set(GIT_ATTRIBUTES)))
		with open(git_attributes, 'w') as f:
			f.writelines('\n'.join(content))

		# set core.attributesfile when editing global git config
		if self.mode == 'global':
			self.execute(['core.attributesfile', global_attributes])


	def execute(self, args):
		command = ['git', 'config']
		if self.mode == 'global':
			command.append('--global')
		command += args
		return subprocess.run(command, cwd=self.path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True).stdout
	
	def git_attributes(self):
		if self.mode == 'local':
			return os.path.join(self.path, '.gitattributes')

		# check if core.attributesfile is configured
		core_attributesfile = self.execute(['--get', 'core.attributesfile']).split('\n')[0]
		if core_attributesfile:
			return core_attributesfile

		# put .gitattributes in same folder as global .gitconfig
		# determine .gitconfig path
		f = self.execute(['--list', '--show-origin']).split('\n')[0]
		p = self.execute(['--list']).split('\n')[0]
		return f[:f.index(p)][5:][:-11] + '.gitattributes'


	def uninstall(self):
		keys = self.execute(['--list']).split('\n')
		if [key for key in keys if key.startswith('diff.xltrail.command')]:
			self.execute(['--remove-section', 'diff.xltrail'])

		# clean up gitattributes
		git_attributes = self.git_attributes()
		if os.path.exists(git_attributes):
			with open(git_attributes, 'r') as f:
				content = f.read().split('\n')
			content = [line for line in content if line and line not in GIT_ATTRIBUTES]
			if not content:
				# no content left
				if self.mode == 'global':
					self.execute(['--remove-section', 'core.attributesfile'])
				# delete file
				os.remove(git_attributes)
			else:
				with open(git_attributes, 'w') as f:
					f.writelines('\n'.join(content))


class CommandParser:

	def __init__(self):
		self.args = sys.argv[1:]
	
	def execute(self):
		if not self.args:
			return self.help()

		command = self.args[0]
		args = self.args[1:]

		# do not process if command does not exist
		if not hasattr(self, command):
			return print(f"""Error: unknown command "{command}" for "git-xltrail"\nRun 'git-xltrail --help' for usage.""")

		# execute command
		getattr(self, command)(*args)

	
	def version(self, *args):
		print(f'git-xltrail/{VERSION} (Python {PYTHON_VERSION})')

	def install(self, *args):
		if args:
			if args[0] == '--local':
				installer = Installer(mode='local', path=os.getcwd())
			else:
				return print(f"""Invalid option "{args[0]}" for "git-xltrail install"\nRun 'git-xltrail --help' for usage.""")
		else:
			installer = Installer(mode='global')
		installer.install()

	def uninstall(self, *args):
		if args:
			if args[0] == '--local':
				installer = Installer(mode='local', path=os.getcwd())
			else:
				return print(f"""Invalid option "{args[0]}" for "git-xltrail install"\nRun 'git-xltrail --help' for usage.""")
		else:
			installer = Installer(mode='global')
		installer.uninstall()


	def help(self, *args):
		arg = args[0] if args else None
		if arg == 'install':
			print("""git xltrail install [options]\n
Perform the following actions to ensure that Git xltrail is setup properly:\n
* Set up .gitignore to make Git ignore temporary Excel files.
* Install a git-diff drop-in replacement for Excel files.\n
Options:\n
Without any options, git xltrail install will setup the Excel differ and
.gitignore globally.\n
* --local:
    Sets the .gitignore filters and the git-diff Excel drop-in replacement
    in the local repository, instead of the global git config (~/.gitconfig).""")
		elif arg == 'uninstall':
			print("""git xltrail uninstall [options]\n
Uninstalls Git xltrail:\n
Options:\n
Without any options, git xltrail uninstall will remove the git-diff drop-in 
replacement for Excel files and .gitignore globally.\n
* --local:
    Removes the .gitignore filters and the git-diff Excel drop-in replacement
    in the local repository, instead globally.""")
		elif arg is None:
			print(f"""git-xltrail/{VERSION} (windows amd64; Python {PYTHON_VERSION})
git xltrail <command> [<args>]\n
Git xltrail is a system for managing Excel workbook files in
association with a Git repository. Git xltrail:
* installs a special git-diff for Excel files 
* makes Git ignore temporary Excel files via .gitignore\n
Commands
--------\n
* git xltrail install:
    Install Git xltrail.
* git xltrail uninstall:
    Uninstall Git xltrail.
* git xltrail version:
    Report the version number.""")
		else:
			print(f'Sorry, no usage text found for "{arg}"')



if __name__ == '__main__':
	command_parser = CommandParser()
	command_parser.execute()
