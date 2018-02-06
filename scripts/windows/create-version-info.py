import os
import json

base_directory = os.path.join('scripts', 'windows')


with open('versioninfo.json', 'r') as f:
    version_info = json.loads(f.read())

with open(os.path.join(base_directory, 'git-xltrail-version-info.template'), 'r') as f:
    s = f.read()

for key, value in version_info['version'].items():
    s = s.replace('{' + key + '}', str(value))

with open(os.path.join(base_directory, 'git-xltrail-version-info.py'), 'w') as f:
    f.write(s)
