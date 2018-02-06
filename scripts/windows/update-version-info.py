import os
import json
import re

base_directory = os.path.join('scripts', 'windows')

# read from version info
with open('versioninfo.json', 'r') as f:
    version_info = json.loads(f.read())

major = version_info['version']['major']
minor = version_info['version']['minor']
patch = version_info['version']['patch']
build = version_info['version']['build']


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
        StringStruct(u'FileDescription', u'Git xltrail'),
        StringStruct(u'FileVersion', u'{major}.{minor}.{patch}'),
        StringStruct(u'InternalName', u'git-xltrail'),
        StringStruct(u'LegalCopyright', u'Zoomer Analytics LLC'),
        StringStruct(u'OriginalFilename', u'git-xltrail'),
        StringStruct(u'ProductName', u'Git xltrail'),
        StringStruct(u'ProductVersion', u'{major}.{minor}.{patch}')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)"""

# update 'git-xltrail-version-info.py
path = os.path.join(base_directory, 'git-xltrail-version-info.py')
with open(path, 'w') as f:
    f.write(s)

# update git-xltrail.py
path = 'git-xltrail.py'
with open(path, 'r') as f:
    s = f.read()

s = re.sub("VERSION\s*=\s*('|\")\d\.\d.\d('|\")", f"VERSION = '{major}.{minor}.{patch}'", s, re.MULTILINE)
with open(path, 'w') as f:
    f.write(s)