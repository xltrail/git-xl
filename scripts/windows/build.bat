@ECHO OFF
python -c "import sys;print('x64' if sys.maxsize > 2**32 else 'x86')" > PYTHON_ARCH
set /p PYTHON_ARCH= < PYTHON_ARCH
del PYTHON_ARCH

python .\scripts\windows\update-version-info.py
pyinstaller --onefile .\src\diff.py --name=git-xltrail-diff-%PYTHON_ARCH%.exe --version-file .\scripts\windows\git-xltrail-version-info.py --icon .\scripts\windows\git-xltrail-logo.ico --add-data .\src\xltrail-core.dll;.
pyinstaller --onefile .\src\merge.py --name=git-xltrail-merge-%PYTHON_ARCH%.exe --version-file .\scripts\windows\git-xltrail-version-info.py --icon .\scripts\windows\git-xltrail-logo.ico --add-data .\src\xltrail-core.dll;.
pyinstaller --onefile .\src\cli.py --name=git-xltrail-%PYTHON_ARCH%.exe --version-file .\scripts\windows\git-xltrail-version-info.py --icon .\scripts\windows\git-xltrail-logo.ico --add-data .\src\xltrail-core.dll;.
