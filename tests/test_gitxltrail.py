from unittest import TestCase, mock
git_xltrail = __import__("git-xltrail")


class TestLocalInstaller(TestCase):

    @mock.patch('git-xltrail.is_git_repository', return_value=True)
    def test_paths(self, mock_is_git_repository):
        installer = git_xltrail.Installer(mode='local', path='\\path\\to\\repository')
        self.assertEqual(installer.get_git_attributes_path(), '\\path\\to\\repository\\.gitattributes')
        self.assertEqual(installer.get_git_attributes_path(), '\\path\\to\\repository\\.gitattributes')

    @mock.patch('git-xltrail.subprocess.run')
    @mock.patch('git-xltrail.is_git_repository', return_value=True)
    @mock.patch('git-xltrail.os.path.exists', return_value=False)
    @mock.patch('builtins.open', new_callable=mock.mock_open)
    def test_can_install_when_files_do_not_exist(self, mock_file_open, mock_path_exists, mock_is_git_repository, mock_run):
        installer = git_xltrail.Installer(mode='local', path='\\path\\to\\repository')
        installer.install()
        mock_run.assert_called_once_with(['git', 'config', 'diff.xltrail.command', 'git-xltrail-diff.exe'], cwd='\\path\\to\\repository', stderr=-1, stdout=-1, universal_newlines=True)
        mock_file_open.assert_has_calls([
            mock.call('\\path\\to\\repository\\.gitattributes', 'w'),
            mock.call().__enter__(),
            mock.call().writelines('*.xla diff=xltrail\n*.xlam diff=xltrail\n*.xls diff=xltrail\n*.xlsb diff=xltrail\n*.xlsm diff=xltrail\n*.xlsx diff=xltrail\n*.xlt diff=xltrail'),
            mock.call().__exit__(None, None, None),
            mock.call('\\path\\to\\repository\\.gitignore', 'w'),
            mock.call().__enter__(),
            mock.call().writelines('~$*.xla\n~$*.xlam\n~$*.xls\n~$*.xlsb\n~$*.xlsm\n~$*.xlsx\n~$*.xlt'),
            mock.call().__exit__(None, None, None)
        ])

    @mock.patch('git-xltrail.subprocess.run')
    @mock.patch('git-xltrail.is_git_repository', return_value=True)
    @mock.patch('git-xltrail.os.path.exists', return_value=True)
    @mock.patch('builtins.open', new_callable=mock.mock_open, read_data='something\n')
    def test_can_install_when_files_exist(self, mock_file_open, mock_path_exists, mock_is_git_repository, mock_run):
        installer = git_xltrail.Installer(mode='local', path='\\path\\to\\repository')
        installer.install()
        mock_run.assert_called_once_with(['git', 'config', 'diff.xltrail.command', 'git-xltrail-diff.exe'], cwd='\\path\\to\\repository', stderr=-1, stdout=-1, universal_newlines=True)
        mock_file_open.assert_has_calls([
            mock.call('\\path\\to\\repository\\.gitattributes', 'r'),
            mock.call().__enter__(),
            mock.call().read(),
            mock.call().__exit__(None, None, None),
            mock.call('\\path\\to\\repository\\.gitattributes', 'w'),
            mock.call().__enter__(),
            mock.call().writelines('*.xla diff=xltrail\n*.xlam diff=xltrail\n*.xls diff=xltrail\n*.xlsb diff=xltrail\n*.xlsm diff=xltrail\n*.xlsx diff=xltrail\n*.xlt diff=xltrail\nsomething'),
            mock.call().__exit__(None, None, None),
            mock.call('\\path\\to\\repository\\.gitignore', 'r'),
            mock.call().__enter__(),
            mock.call().read(),
            mock.call().__exit__(None, None, None),
            mock.call('\\path\\to\\repository\\.gitignore', 'w'),
            mock.call().__enter__(),
            mock.call().writelines('something\n~$*.xla\n~$*.xlam\n~$*.xls\n~$*.xlsb\n~$*.xlsm\n~$*.xlsx\n~$*.xlt'),
            mock.call().__exit__(None, None, None)
        ])

    @mock.patch('git-xltrail.subprocess.run')
    @mock.patch('git-xltrail.is_git_repository', return_value=True)
    @mock.patch('git-xltrail.os.path.exists', return_value=False)
    @mock.patch('git-xltrail.os.remove')
    @mock.patch('builtins.open', new_callable=mock.mock_open)
    def test_can_uninstall_when_files_do_not_exist(self, mock_file_open, mock_os_remove,  mock_path_exists, mock_is_git_repository, mock_run):
        installer = git_xltrail.Installer(mode='local', path='\\path\\to\\repository')
        installer.uninstall()
        mock_run.assert_called_once_with(['git', 'config', '--list'], cwd='\\path\\to\\repository', stderr=-1, stdout=-1, universal_newlines=True)
        mock_os_remove.assert_has_calls([
            mock.call('\\path\\to\\repository\\.gitattributes'),
            mock.call('\\path\\to\\repository\\.gitignore')
        ])


    @mock.patch('git-xltrail.subprocess.run')
    @mock.patch('git-xltrail.is_git_repository', return_value=True)
    @mock.patch('git-xltrail.os.path.exists', return_value=True)
    @mock.patch('git-xltrail.os.remove')
    @mock.patch('builtins.open', new_callable=mock.mock_open, read_data='something')
    def test_can_uninstall_when_files_exist(self, mock_file_open, mock_os_remove,  mock_path_exists, mock_is_git_repository, mock_run):
        installer = git_xltrail.Installer(mode='local', path='\\path\\to\\repository')
        installer.uninstall()
        mock_run.assert_called_once_with(['git', 'config', '--list'], cwd='\\path\\to\\repository', stderr=-1, stdout=-1, universal_newlines=True)
        self.assertEqual(mock_os_remove.call_count, 0)
        mock_file_open.assert_has_calls([
            mock.call('\\path\\to\\repository\\.gitattributes', 'r'),
            mock.call().__enter__(),
            mock.call().read(),
            mock.call().__exit__(None, None, None),
            mock.call('\\path\\to\\repository\\.gitattributes', 'w'),
            mock.call().__enter__(),
            mock.call().writelines('something'),
            mock.call().__exit__(None, None, None),
            mock.call('\\path\\to\\repository\\.gitattributes', 'r'),
            mock.call().__enter__(),
            mock.call().read(),
            mock.call().__exit__(None, None, None),
            mock.call('\\path\\to\\repository\\.gitattributes', 'w'),
            mock.call().__enter__(),
            mock.call().writelines('something'),
            mock.call().__exit__(None, None, None)
        ])
