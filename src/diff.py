import sys
import os
from difflib import unified_diff

import colorama
from oletools.olevba3 import VBA_Parser
from colorama import Fore, Back, Style, init


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
    if not 8 <= len(sys.argv) <= 9:
        print('Unexpected number of arguments')
        sys.exit(0)

    if len(sys.argv) == 8:
        _, workbook_name, workbook_b, _, _, workbook_a, _ , _ = sys.argv
        numlines = 3
    if len(sys.argv) == 9:
        _, numlines, workbook_name, workbook_b, _, _, workbook_a, _, _ = sys.argv
        numlines = int(numlines)

    path_workbook_a = os.path.abspath(workbook_a) if workbook_a != 'nul' and workbook_a != '/dev/null' else None
    path_workbook_b = os.path.abspath(workbook_b) if workbook_b != 'nul' and workbook_b != '/dev/null' else None

    workbook_a_modules = get_vba(path_workbook_a)
    workbook_b_modules = {} if workbook_b == 'nul' else get_vba(path_workbook_b)

    diffs = []
    for module_a, vba_a in workbook_a_modules.items():
        if module_a not in workbook_b_modules:
            diffs.append({
                'a': '--- /dev/null',
                'b': '+++ b/' + workbook_name + '/VBA/' + module_a,
                'diff': '\n'.join([Fore.GREEN + '+' + line for line in vba_a.split('\n')])
            })
        elif vba_a != workbook_b_modules[module_a]:
            diffs.append({
                'a': '--- a/' + workbook_name + '/VBA/' + module_a,
                'b': '+++ b/' + workbook_name + '/VBA/' + module_a,
                'diff': '\n'.join([(Fore.RED if line.startswith('-') else (Fore.GREEN if line.startswith('+') else (Fore.CYAN if line.startswith('@') else ''))) + line.strip('\n') for line in list(unified_diff(workbook_b_modules[module_a].split('\n'), vba_a.split('\n'), n=numlines))[2:]])
            })

    for module_b, vba_b in workbook_b_modules.items():
        if module_b not in workbook_a_modules:
            diffs.append({
                'a': '--- b/' + workbook_name + '/VBA/' + module_b,
                'b': '+++ /dev/null',
                'diff': '\n'.join([Fore.RED + '-' + line for line in vba_b.split('\n')])
            })


    colorama.init(strip=False)

    print(Style.BRIGHT + 'diff --xl ' + 'a/' + workbook_name + ' b/' + workbook_name)
    for diff in diffs:
        print(Style.BRIGHT + diff['a'])
        print(Style.BRIGHT + diff['b'])
        print(diff['diff'])
        print('')
