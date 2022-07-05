import os
import json
import re

base_directory = os.path.join('scripts', 'windows')

# read build number, repo tag name and git commit hash from env vars 
build = os.getenv('GITHUB_RUN_ATTEMPT', '0')
if os.getenv('GITHUB_REF_TYPE') == 'tag':
  version = os.environ['GITHUB_REF_NAME']
else:
  version = '0.0.0'
commit = os.environ['GITHUB_SHA'][:7] if os.getenv('GITHUB_SHA') else 'dev'

print('-----------')
print('Version tag: %s' % version)
print('Build number: %s' % build)
print('Commit hash: %s' % commit)

major, minor, patch = version.split('.')
print(f'Generate file version: {major}.{minor}.{patch}.{build}')
print('-----------')



s = f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({major}, {minor}, {patch}, {build}),
    prodvers=({major}, {minor}, {patch}, {build}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Zoomer Analytics LLC'),
        StringStruct(u'FileDescription', u'Git XL'),
        StringStruct(u'FileVersion', u'{major}.{minor}.{patch}'),
        StringStruct(u'InternalName', u'git-xl'),
        StringStruct(u'LegalCopyright', u'Zoomer Analytics LLC'),
        StringStruct(u'OriginalFilename', u'git-xl'),
        StringStruct(u'ProductName', u'Git XL'),
        StringStruct(u'ProductVersion', u'{major}.{minor}.{patch}')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)"""

# update 'git-xl-version-info.py
path = os.path.join(base_directory, 'git-xl-version-info.py')
with open(path, 'w') as f:
    f.write(s)

# update git-xl.py (VERSION and COMMIT)
path = 'src\\cli.py'
with open(path, 'r') as f:
    s = f.read()

s = re.sub("VERSION\s*=\s*('|\")\d\.\d.\d('|\")", f"VERSION = '{major}.{minor}.{patch}'", s, re.MULTILINE)
s = re.sub("GIT_COMMIT\s*=\s*('|\")[a-zA-Z0-9]*('|\")", f"GIT_COMMIT = '{commit}'", s, re.MULTILINE)

with open(path, 'w') as f:
    f.write(s)