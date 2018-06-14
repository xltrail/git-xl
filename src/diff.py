import sys
import os
import shutil
import colorama
import clr
from difflib import unified_diff
from colorama import Fore, Back, Style, init

clr.AddReference('xltrail-core')
from xltrail.core import Workbook 


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

    path_workbook_a = os.path.abspath(workbook_a) if workbook_a != 'nul' else None
    path_workbook_b = os.path.abspath(workbook_b) if workbook_b != 'nul' else None

    workbook_a = Workbook(path_workbook_a) if path_workbook_a is not None else None
    workbook_b = Workbook(path_workbook_b) if path_workbook_b is not None else None

    diffs = []

    # sheets
    a_sheets = {} if workbook_a is None else dict([(i.name, i) for i in workbook_a.worksheets])
    b_sheets = {} if workbook_b is None else dict([(i.name, i) for i in workbook_b.worksheets])

    for a_name, a_sheet in a_sheets.items():
        if a_name not in b_sheets:
            diffs.append({
                'a': '--- /dev/null',
                'b': '+++ b/' + workbook_name + '/Worksheets/' + a_name,
                'diff': Fore.GREEN + '+' + str(a_sheet.cells.Count) + ' cell' + ('' if a_sheet.cells.Count == 1 else 's')
            })
        elif a_sheet.digest != b_sheets[a_name].digest:
            b_sheet = b_sheets[a_name]
            diffs.append({
                'a': '--- a/' + workbook_name + '/Worksheets/' + a_name,
                'b': '+++ b/' + workbook_name + '/Worksheets/' + a_name,
                'diff': Fore.RED + '-' + str(b_sheet.cells.Count) + ' cell' + ('' if b_sheet.cells.Count == 1 else 's') + '\n' + Fore.GREEN + '+' + str(a_sheet.cells.Count) + ' cell' + ('' if a_sheet.cells.Count == 1 else 's')
            })

    for b_name, b_sheet in b_sheets.items():
        if b_name not in a_sheets:
            diffs.append({
                'a': '--- b/' + workbook_name + '/Worksheet/' + b_name,
                'b': '+++ /dev/null',
                'diff': Fore.RED + '-' + str(b_sheet.cells.Count) + ' cell' + ('' if b_sheet.cells.Count == 1 else 's')
            })


    # VBA modules
    a_modules = {} if workbook_a is None else dict([(m.name, m) for m in workbook_a.vba_modules])
    b_modules = {} if workbook_b is None else dict([(m.name, m) for m in workbook_b.vba_modules])
    for module_a, vba_a in a_modules.items():
        if module_a not in b_modules:
            diffs.append({
                'a': '--- /dev/null',
                'b': '+++ b/' + workbook_name + '/VBA/' + vba_a.type + '/' + module_a,
                'diff': '\n'.join([Fore.GREEN + '+' + line for line in vba_a.content.split('\n')])
            })
        elif vba_a.digest != b_modules[module_a].digest:
            diffs.append({
                'a': '--- a/' + workbook_name + '/VBA/' + vba_a.type + '/' + module_a,
                'b': '+++ b/' + workbook_name + '/VBA/' + vba_a.type + '/' + module_a,
                'diff': '\n'.join([(Fore.RED if line.startswith('-') else (Fore.GREEN if line.startswith('+') else (Fore.CYAN if line.startswith('@') else ''))) + line.strip('\n') for line in list(unified_diff(b_modules[module_a].content.split('\n'), vba_a.content.split('\n'), n=numlines))[2:]])
            })

    for module_b, vba_b in b_modules.items():
        if module_b not in a_modules:
            diffs.append({
                'a': '--- b/' + workbook_name + '/VBA/' + vba_b.type + '/' + module_b,
                'b': '+++ /dev/null',
                'diff': '\n'.join([Fore.RED + '-' + line for line in vba_b.content.split('\n')])
            })


    colorama.init(strip=False)

    print(Style.BRIGHT + 'diff --xltrail ' + 'a/' + workbook_name + ' b/' + workbook_name)
    for diff in diffs:
        print(Style.BRIGHT + diff['a'])
        print(Style.BRIGHT + diff['b'])
        print(diff['diff'])
        print('')
