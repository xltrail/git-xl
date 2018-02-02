#!/usr/bin/env python
import sys
import os
import shutil

from difflib import unified_diff
from oletools.olevba3 import VBA_Parser
import colorama

from colorama import Fore, Back, Style, init


EXCEL_FILE_EXTENSIONS = ('xlsb', 'xls', 'xlsm', 'xla', 'xlt', 'xlam',)


def get_vba(workbook):
    vba_parser = VBA_Parser(workbook)
    vba_modules = vba_parser.extract_all_macros() if vba_parser.detect_vba_macros() else []

    modules = {}

    for _, _, _, content in vba_modules:
        decoded_content = content.decode('latin-1')
        lines = []
        if '\r\n' in decoded_content:
            lines = decoded_content.split('\r\n')
        else:
            lines = decoded_content.split('\n')
        if lines:
            name = lines[0].replace('Attribute VB_Name = ', '').strip('"')
            content = [line for line in lines[1:] if not (
                line.startswith('Attribute') and 'VB_' in line)]
            non_empty_lines_of_code = len([c for c in content if c])
            modules[name] = '\n'.join(content)
    return modules


if __name__ == '__main__':
    _, workbook1, workbook2, _, _, _, _ , _ = sys.argv
    
    path_workbook1 = os.path.join(os.getcwd(), workbook1)
    path_workbook2 = workbook2
    
    workbook1_modules = get_vba(path_workbook1)
    workbook2_modules = get_vba(path_workbook2)

    diffs = []
    for module1, vba1 in workbook1_modules.items():
        if module1 not in workbook2_modules:
            diffs.append({
                'a': '--- a/' + workbook1 + '/VBA/' + module1,
                'b': '+++ /dev/null',
                'diff': '\n'.join([Fore.RED + '-' + line for line in vba1.split('\n')])
            })
        elif vba1 != workbook2_modules[module1]:
            diffs.append({
                'a': '--- a/' + workbook1 + '/VBA/' + module1,
                'b': '+++ b/' + workbook1 + '/VBA/' + module1,
                'diff': '\n'.join([(Fore.RED if line.startswith('-') else (Fore.GREEN if line.startswith('+') else '')) + line.strip('\n') for line in list(unified_diff(workbook2_modules[module1].split('\n'), vba1.split('\n')))[2:]])
            })

    for module2, vba2 in workbook2_modules.items():
        if module2 not in workbook1_modules:
            diffs.append({
                'a': '--- /dev/null',
                'b': '+++ b/' + workbook2 + '/VBA/' + module2,
                'diff': '\n'.join(['+' + line for line in vba1.split('\n')])
            })


    colorama.init(strip=False)

    for diff in diffs:
        print(diff['a'])
        print(diff['b'])
        print(diff['diff'])
        print('')
