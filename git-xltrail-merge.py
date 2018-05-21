import sys
import difflib
import os
import shutil
import clr
clr.AddReference('xltrail-core')
from xltrail.core import Workbook 


def drop_inline_diffs(diff):
    r = []
    for t in diff:
        if not t.startswith('?'):
            r.append(t)
    return r


def three_way_merge(a, x, b, name):
    dxa = difflib.Differ()
    dxb = difflib.Differ()
    xa = drop_inline_diffs(dxa.compare(x, a))
    xb = drop_inline_diffs(dxb.compare(x, b))

    m = []
    index_a = 0
    index_b = 0
    had_conflict = 0

    while (index_a < len(xa)) and (index_b < len(xb)):
        # no changes or adds on both sides
        if (xa[index_a] == xb[index_b] and
            (xa[index_a].startswith('  ') or xa[index_a].startswith('+ '))):
            m.append(xa[index_a][2:])
            index_a += 1
            index_b += 1
            continue

        # removing matching lines from one or both sides
        if ((xa[index_a][2:] == xb[index_b][2:])
            and (xa[index_a].startswith('- ') or xb[index_b].startswith('- '))):
            index_a += 1
            index_b += 1
            continue

        # adding lines in A
        if xa[index_a].startswith('+ ') and xb[index_b].startswith('  '):
            m.append(xa[index_a][2:])
            index_a += 1
            continue

        # adding line in B
        if xb[index_b].startswith('+ ') and xa[index_a].startswith('  '):
            m.append(xb[index_b][2:])
            index_b += 1
            continue

        # conflict - list both A and B, similar to GNU's diff3
        m.append(f"<<<<<<< yours:{name}\n")
        while (index_a < len(xa)) and not xa[index_a].startswith('  '):
            m.append(xa[index_a][2:])
            index_a += 1
        m.append("=======\n")
        while (index_b < len(xb)) and not xb[index_b].startswith('  '):
            m.append(xb[index_b][2:])
            index_b += 1
        m.append(f">>>>>>> theirs:{name}\n")
        had_conflict = 1

    # append remining lines - there will be only either A or B
    for i in range(len(xa) - index_a):
        m.append(xa[index_a + i][2:])
    for i in range(len(xb) - index_b):
        m.append(xb[index_b + i][2:])

    return had_conflict, m


def merge_workbook(filename, x, a, b):
    # get file extension from original filename
    ext = filename.split('.')[-1]

    # add file extension
    x, x_ = f'{x}.{ext}', x  # ancestor of the conflicting workbook
    a, a_ = f'{a}.{ext}', a  #   current version of the conflicting file
    b, b_ = f'{b}.{ext}', b

    x = os.path.abspath(x)
    a = os.path.abspath(a)
    b = os.path.abspath(b)

    # aspose requires file extension
    os.rename(a_, a)
    os.rename(b_, b)
    os.rename(x_, x)

    wb_x = Workbook(x)
    wb_a = Workbook(a)
    wb_b = Workbook(b)

    # ignore 'Document' type; this is bound to a sheet/chart
    # as soon as sheets are implemented, we can lift the restriction
    vba_modules_a = [vba_module.name for vba_module in wb_a.vba_modules if vba_module.type != 'Document']
    vba_modules_b = [vba_module.name for vba_module in wb_b.vba_modules if vba_module.type != 'Document']

    modified_vba_modules = list(set(vba_modules_a) & set(vba_modules_b))
    added_vba_modules = list(set(vba_modules_b) - set(vba_modules_a))
    deleted_vba_modules = list(set(vba_modules_a) - set(vba_modules_b))

    # remove deleted VBA modules
    for name in deleted_vba_modules:
        wb_a.remove_vba_module(name)

    had_conflict = False
    # merge modified VBA modules
    for name in modified_vba_modules:
        vba_module_a = wb_a.get_vba_module(name)
        vba_module_b = wb_b.get_vba_module(name)
        if vba_module_a.digest != vba_module_b.digest:
            vba_module_x = wb_x.get_vba_module(name)
            # perform a 3-way merge
            conflict, merged = three_way_merge(
                x=vba_module_x.content.split('\n'),
                a=vba_module_a.content.split('\n'),
                b=vba_module_b.content.split('\n'),
                name=name)
            had_conflict = had_conflict or conflict
            merged = '\n'.join(merged)
            vba_module_a.content = merged
    
    # add added VBA modules
    for name in added_vba_modules:
        # get vba module by name
        vba_module = [m for m in wb_b.vba_modules if m.name == name][0]
        wb_a.add_vba_module(name, vba_module.type, vba_module.content)

    wb_a.save()

    # rename back into original filename, otherwise git won't like it
    os.rename(a, a_)
    os.rename(b, b_)
    os.rename(x, x_)

    if had_conflict:
        sys.exit(1)



if __name__ == '__main__':
    merge_workbook(*sys.argv[1:])