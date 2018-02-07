from unittest import TestCase, mock
git_xltrail = __import__("git-xltrail")


class TestInstaller(TestCase):

    @mock.patch('git-xltrail.subprocess.run')
    @mock.patch('git-xltrail.is_git_repository', return_value=True)
    @mock.patch('git-xltrail.os.path.exists', return_value=False)
    @mock.patch('builtins.open', new_callable=mock.mock_open)
    def test_can_install_locally_when_gitattributes_does_not_exist(self, mock_file_open, mock_path_exists, mock_is_git_repository, mock_run):
        installer = git_xltrail.Installer(mode='local', path='\\path\\to\\repository')
        installer.install()
        mock_run.assert_called_once_with(
            ['git', 'config', 'diff.xltrail.command', 'git-xltrail-diff.exe'],
            cwd='\\path\\to\\repository',
            stderr=-1,
            stdout=-1,
            universal_newlines=True)
        mock_file_open.assert_called_once_with('\\path\\to\\repository\\.gitattributes', 'w')
        file_handle = mock_file_open()
        file_handle.writelines.assert_called_once_with('*.xla diff=xltrail\n*.xlm diff=xltrail\n*.xls diff=xltrail\n*.xlsb diff=xltrail\n*.xlsm diff=xltrail\n*.xlsx diff=xltrail\n*.xlt diff=xltrail')

    @mock.patch('git-xltrail.subprocess.run')
    @mock.patch('git-xltrail.is_git_repository', return_value=True)
    @mock.patch('git-xltrail.os.path.exists', return_value=True)
    @mock.patch('builtins.open', new_callable=mock.mock_open, read_data='something\n')
    def test_can_install_locally_when_gitattributes_exists(self, mock_file_open, mock_path_exists, mock_is_git_repository, mock_run):
        installer = git_xltrail.Installer(mode='local', path='\\path\\to\\repository')
        installer.install()
        mock_run.assert_called_once_with(
            ['git', 'config', 'diff.xltrail.command', 'git-xltrail-diff.exe'],
            cwd='\\path\\to\\repository',
            stderr=-1,
            stdout=-1,
            universal_newlines=True)
        mock_file_open.assert_has_calls([
            mock.call('\\path\\to\\repository\\.gitattributes', 'r'),
            mock.call().__enter__(),
            mock.call().read(),
            mock.call().__exit__(None, None, None),
            mock.call('\\path\\to\\repository\\.gitattributes', 'w')
        ])
        file_handle = mock_file_open()
        file_handle.writelines.assert_called_once_with('*.xla diff=xltrail\n*.xlm diff=xltrail\n*.xls diff=xltrail\n*.xlsb diff=xltrail\n*.xlsm diff=xltrail\n*.xlsx diff=xltrail\n*.xlt diff=xltrail\nsomething')