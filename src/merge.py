from __future__ import absolute_import

import sys
import difflib
import os
import time
import shutil
import clr
import patiencediff

# clr
clr.AddReference('xltrail-core')
from xltrail.core import Workbook



# This is a version of unified_diff which only adds a factory parameter
# so that you can override the default SequenceMatcher
# this has been submitted as a patch to python
def unified_diff(a, b, fromfile='', tofile='', fromfiledate='',
                 tofiledate='', n=3, lineterm='\n',
                 sequencematcher=None):
    r"""
    Compare two sequences of lines; generate the delta as a unified diff.

    Unified diffs are a compact way of showing line changes and a few
    lines of context.  The number of context lines is set by 'n' which
    defaults to three.

    By default, the diff control lines (those with ---, +++, or @@) are
    created with a trailing newline.  This is helpful so that inputs
    created from file.readlines() result in diffs that are suitable for
    file.writelines() since both the inputs and outputs have trailing
    newlines.

    For inputs that do not have trailing newlines, set the lineterm
    argument to "" so that the output will be uniformly newline free.

    The unidiff format normally has a header for filenames and modification
    times.  Any or all of these may be specified using strings for
    'fromfile', 'tofile', 'fromfiledate', and 'tofiledate'.  The modification
    times are normally expressed in the format returned by time.ctime().

    Example:

    >>> for line in unified_diff('one two three four'.split(),
    ...             'zero one tree four'.split(), 'Original', 'Current',
    ...             'Sat Jan 26 23:30:50 1991', 'Fri Jun 06 10:20:52 2003',
    ...             lineterm=''):
    ...     print line
    --- Original Sat Jan 26 23:30:50 1991
    +++ Current Fri Jun 06 10:20:52 2003
    @@ -1,4 +1,4 @@
    +zero
     one
    -two
    -three
    +tree
     four
    """
    if sequencematcher is None:
        sequencematcher = difflib.SequenceMatcher

    if fromfiledate:
        fromfiledate = '\t' + str(fromfiledate)
    if tofiledate:
        tofiledate = '\t' + str(tofiledate)

    started = False
    for group in sequencematcher(None,a,b).get_grouped_opcodes(n):
        if not started:
            yield '--- %s%s%s' % (fromfile, fromfiledate, lineterm)
            yield '+++ %s%s%s' % (tofile, tofiledate, lineterm)
            started = True
        i1, i2, j1, j2 = group[0][1], group[-1][2], group[0][3], group[-1][4]
        yield "@@ -%d,%d +%d,%d @@%s" % (i1+1, i2-i1, j1+1, j2-j1, lineterm)
        for tag, i1, i2, j1, j2 in group:
            if tag == 'equal':
                for line in a[i1:i2]:
                    yield ' ' + line
                continue
            if tag == 'replace' or tag == 'delete':
                for line in a[i1:i2]:
                    yield '-' + line
            if tag == 'replace' or tag == 'insert':
                for line in b[j1:j2]:
                    yield '+' + line


def unified_diff_files(a, b, sequencematcher=None):
    """Generate the diff for two files.
    """
    # Should this actually be an error?
    if a == b:
        return []
    if a == '-':
        file_a = sys.stdin
        time_a = time.time()
    else:
        file_a = open(a, 'rb')
        time_a = os.stat(a).st_mtime

    if b == '-':
        file_b = sys.stdin
        time_b = time.time()
    else:
        file_b = open(b, 'rb')
        time_b = os.stat(b).st_mtime

    # TODO: Include fromfiledate and tofiledate
    return unified_diff(file_a.readlines(), file_b.readlines(),
                        fromfile=a, tofile=b,
                        sequencematcher=sequencematcher)


def intersect(ra, rb):
    """Given two ranges return the range where they intersect or None.

    >>> intersect((0, 10), (0, 6))
    (0, 6)
    >>> intersect((0, 10), (5, 15))
    (5, 10)
    >>> intersect((0, 10), (10, 15))
    >>> intersect((0, 9), (10, 15))
    >>> intersect((0, 9), (7, 15))
    (7, 9)
    """
    # preconditions: (ra[0] <= ra[1]) and (rb[0] <= rb[1])

    sa = max(ra[0], rb[0])
    sb = min(ra[1], rb[1])
    if sa < sb:
        return sa, sb
    else:
        return None


def compare_range(a, astart, aend, b, bstart, bend):
    """Compare a[astart:aend] == b[bstart:bend], without slicing.
    """
    if (aend-astart) != (bend-bstart):
        return False
    for ia, ib in zip(range(astart, aend), range(bstart, bend)):
        if a[ia] != b[ib]:
            return False
    else:
        return True




class Merge3:
    """3-way merge of texts.

    Given BASE, OTHER, THIS, tries to produce a combined text
    incorporating the changes from both BASE->OTHER and BASE->THIS.
    All three will typically be sequences of lines."""

    def __init__(self, base, a, b, is_cherrypick=False, allow_objects=False):
        """Constructor.

        :param base: lines in BASE
        :param a: lines in A
        :param b: lines in B
        :param is_cherrypick: flag indicating if this merge is a cherrypick.
            When cherrypicking b => a, matches with b and base do not conflict.
        :param allow_objects: if True, do not require that base, a and b are
            plain Python strs.  Also prevents BinaryFile from being raised.
            Lines can be any sequence of comparable and hashable Python
            objects.
        """
        self.base = base
        self.a = a
        self.b = b
        self.is_cherrypick = is_cherrypick

    def merge_lines(self,
                    name_a=None,
                    name_b=None,
                    name_base=None,
                    start_marker='<<<<<<<',
                    mid_marker='=======',
                    end_marker='>>>>>>>',
                    base_marker=None,
                    reprocess=False):
        """Return merge in cvs-like form.
        """
        newline = '\n'
        if len(self.a) > 0:
            if self.a[0].endswith('\r\n'):
                newline = '\r\n'
            elif self.a[0].endswith('\r'):
                newline = '\r'
        if base_marker and reprocess:
            raise ValueError('cannot reprocess and show base')
        if name_a:
            start_marker = start_marker + ' ' + name_a
        if name_b:
            end_marker = end_marker + ' ' + name_b
        if name_base and base_marker:
            base_marker = base_marker + ' ' + name_base
        merge_regions = self.merge_regions()
        if reprocess is True:
            merge_regions = self.reprocess_merge_regions(merge_regions)
        for t in merge_regions:
            what = t[0]
            if what == 'unchanged':
                for i in range(t[1], t[2]):
                    yield self.base[i]
            elif what == 'a' or what == 'same':
                for i in range(t[1], t[2]):
                    yield self.a[i]
            elif what == 'b':
                for i in range(t[1], t[2]):
                    yield self.b[i]
            elif what == 'conflict':
                yield start_marker + newline
                for i in range(t[3], t[4]):
                    yield self.a[i]
                if base_marker is not None:
                    yield base_marker + newline
                    for i in range(t[1], t[2]):
                        yield self.base[i]
                yield mid_marker + newline
                for i in range(t[5], t[6]):
                    yield self.b[i]
                yield end_marker + newline
            else:
                raise ValueError(what)

    def merge_annotated(self):
        """Return merge with conflicts, showing origin of lines.

        Most useful for debugging merge.
        """
        for t in self.merge_regions():
            what = t[0]
            if what == 'unchanged':
                for i in range(t[1], t[2]):
                    yield 'u | ' + self.base[i]
            elif what == 'a' or what == 'same':
                for i in range(t[1], t[2]):
                    yield what[0] + ' | ' + self.a[i]
            elif what == 'b':
                for i in range(t[1], t[2]):
                    yield 'b | ' + self.b[i]
            elif what == 'conflict':
                yield '<<<<\n'
                for i in range(t[3], t[4]):
                    yield 'A | ' + self.a[i]
                yield '----\n'
                for i in range(t[5], t[6]):
                    yield 'B | ' + self.b[i]
                yield '>>>>\n'
            else:
                raise ValueError(what)

    def merge_groups(self):
        """Yield sequence of line groups.  Each one is a tuple:

        'unchanged', lines
             Lines unchanged from base

        'a', lines
             Lines taken from a

        'same', lines
             Lines taken from a (and equal to b)

        'b', lines
             Lines taken from b

        'conflict', base_lines, a_lines, b_lines
             Lines from base were changed to either a or b and conflict.
        """
        for t in self.merge_regions():
            what = t[0]
            if what == 'unchanged':
                yield what, self.base[t[1]:t[2]]
            elif what == 'a' or what == 'same':
                yield what, self.a[t[1]:t[2]]
            elif what == 'b':
                yield what, self.b[t[1]:t[2]]
            elif what == 'conflict':
                yield (what,
                       self.base[t[1]:t[2]],
                       self.a[t[3]:t[4]],
                       self.b[t[5]:t[6]])
            else:
                raise ValueError(what)
    
    def is_conflicted(self):
        return sum([1 if t[0] == 'conflict' else 0 for t in self.merge_regions()])

    def merge_regions(self):
        """Return sequences of matching and conflicting regions.

        This returns tuples, where the first value says what kind we
        have:

        'unchanged', start, end
             Take a region of base[start:end]

        'same', astart, aend
             b and a are different from base but give the same result

        'a', start, end
             Non-clashing insertion from a[start:end]

        Method is as follows:

        The two sequences align only on regions which match the base
        and both descendents.  These are found by doing a two-way diff
        of each one against the base, and then finding the
        intersections between those regions.  These "sync regions"
        are by definition unchanged in both and easily dealt with.

        The regions in between can be in any of three cases:
        conflicted, or changed on only one side.
        """

        # section a[0:ia] has been disposed of, etc
        iz = ia = ib = 0

        for zmatch, zend, amatch, aend, bmatch, bend in self.find_sync_regions():
            matchlen = zend - zmatch
            # invariants:
            #   matchlen >= 0
            #   matchlen == (aend - amatch)
            #   matchlen == (bend - bmatch)
            len_a = amatch - ia
            len_b = bmatch - ib
            len_base = zmatch - iz
            # invariants:
            # assert len_a >= 0
            # assert len_b >= 0
            # assert len_base >= 0

            #print 'unmatched a=%d, b=%d' % (len_a, len_b)

            if len_a or len_b:
                # try to avoid actually slicing the lists
                same = compare_range(self.a, ia, amatch,
                                     self.b, ib, bmatch)

                if same:
                    yield 'same', ia, amatch
                else:
                    equal_a = compare_range(self.a, ia, amatch,
                                            self.base, iz, zmatch)
                    equal_b = compare_range(self.b, ib, bmatch,
                                            self.base, iz, zmatch)
                    if equal_a and not equal_b:
                        yield 'b', ib, bmatch
                    elif equal_b and not equal_a:
                        yield 'a', ia, amatch
                    elif not equal_a and not equal_b:
                        if self.is_cherrypick:
                            for node in self._refine_cherrypick_conflict(
                                                    iz, zmatch, ia, amatch,
                                                    ib, bmatch):
                                yield node
                        else:
                            yield 'conflict', iz, zmatch, ia, amatch, ib, bmatch
                    else:
                        raise AssertionError("can't handle a=b=base but unmatched")

                ia = amatch
                ib = bmatch
            iz = zmatch

            # if the same part of the base was deleted on both sides
            # that's OK, we can just skip it.

            if matchlen > 0:
                # invariants:
                # assert ia == amatch
                # assert ib == bmatch
                # assert iz == zmatch

                yield 'unchanged', zmatch, zend
                iz = zend
                ia = aend
                ib = bend

    def _refine_cherrypick_conflict(self, zstart, zend, astart, aend, bstart, bend):
        """When cherrypicking b => a, ignore matches with b and base."""
        # Do not emit regions which match, only regions which do not match
        matches = patiencediff.PatienceSequenceMatcher(None,
            self.base[zstart:zend], self.b[bstart:bend]).get_matching_blocks()
        last_base_idx = 0
        last_b_idx = 0
        last_b_idx = 0
        yielded_a = False
        for base_idx, b_idx, match_len in matches:
            conflict_z_len = base_idx - last_base_idx
            conflict_b_len = b_idx - last_b_idx
            if conflict_b_len == 0: # There are no lines in b which conflict,
                                    # so skip it
                pass
            else:
                if yielded_a:
                    yield ('conflict',
                           zstart + last_base_idx, zstart + base_idx,
                           aend, aend, bstart + last_b_idx, bstart + b_idx)
                else:
                    # The first conflict gets the a-range
                    yielded_a = True
                    yield ('conflict', zstart + last_base_idx, zstart +
                    base_idx,
                           astart, aend, bstart + last_b_idx, bstart + b_idx)
            last_base_idx = base_idx + match_len
            last_b_idx = b_idx + match_len
        if last_base_idx != zend - zstart or last_b_idx != bend - bstart:
            if yielded_a:
                yield ('conflict', zstart + last_base_idx, zstart + base_idx,
                       aend, aend, bstart + last_b_idx, bstart + b_idx)
            else:
                # The first conflict gets the a-range
                yielded_a = True
                yield ('conflict', zstart + last_base_idx, zstart + base_idx,
                       astart, aend, bstart + last_b_idx, bstart + b_idx)
        if not yielded_a:
            yield ('conflict', zstart, zend, astart, aend, bstart, bend)

    def reprocess_merge_regions(self, merge_regions):
        """Where there are conflict regions, remove the agreed lines.

        Lines where both A and B have made the same changes are
        eliminated.
        """
        for region in merge_regions:
            if region[0] != "conflict":
                yield region
                continue
            type, iz, zmatch, ia, amatch, ib, bmatch = region
            a_region = self.a[ia:amatch]
            b_region = self.b[ib:bmatch]
            matches = patiencediff.PatienceSequenceMatcher(
                    None, a_region, b_region).get_matching_blocks()
            next_a = ia
            next_b = ib
            for region_ia, region_ib, region_len in matches[:-1]:
                region_ia += ia
                region_ib += ib
                reg = self.mismatch_region(next_a, region_ia, next_b,
                                           region_ib)
                if reg is not None:
                    yield reg
                yield 'same', region_ia, region_len+region_ia
                next_a = region_ia + region_len
                next_b = region_ib + region_len
            reg = self.mismatch_region(next_a, amatch, next_b, bmatch)
            if reg is not None:
                yield reg

    @staticmethod
    def mismatch_region(next_a, region_ia,  next_b, region_ib):
        if next_a < region_ia or next_b < region_ib:
            return 'conflict', None, None, next_a, region_ia, next_b, region_ib

    def find_sync_regions(self):
        """Return a list of sync regions, where both descendents match the base.

        Generates a list of (base1, base2, a1, a2, b1, b2).  There is
        always a zero-length sync region at the end of all the files.
        """

        ia = ib = 0
        amatches = patiencediff.PatienceSequenceMatcher(
                None, self.base, self.a).get_matching_blocks()
        bmatches = patiencediff.PatienceSequenceMatcher(
                None, self.base, self.b).get_matching_blocks()
        len_a = len(amatches)
        len_b = len(bmatches)

        sl = []

        while ia < len_a and ib < len_b:
            abase, amatch, alen = amatches[ia]
            bbase, bmatch, blen = bmatches[ib]

            # there is an unconflicted block at i; how long does it
            # extend?  until whichever one ends earlier.
            i = intersect((abase, abase+alen), (bbase, bbase+blen))
            if i:
                intbase = i[0]
                intend = i[1]
                intlen = intend - intbase

                # found a match of base[i[0], i[1]]; this may be less than
                # the region that matches in either one
                # assert intlen <= alen
                # assert intlen <= blen
                # assert abase <= intbase
                # assert bbase <= intbase

                asub = amatch + (intbase - abase)
                bsub = bmatch + (intbase - bbase)
                aend = asub + intlen
                bend = bsub + intlen

                # assert self.base[intbase:intend] == self.a[asub:aend], \
                #       (self.base[intbase:intend], self.a[asub:aend])
                # assert self.base[intbase:intend] == self.b[bsub:bend]

                sl.append((intbase, intend,
                           asub, aend,
                           bsub, bend))
            # advance whichever one ends first in the base text
            if (abase + alen) < (bbase + blen):
                ia += 1
            else:
                ib += 1

        intbase = len(self.base)
        abase = len(self.a)
        bbase = len(self.b)
        sl.append((intbase, intbase, abase, abase, bbase, bbase))

        return sl

    def find_unconflicted(self):
        """Return a list of ranges in base that are not conflicted."""
        am = patiencediff.PatienceSequenceMatcher(
                None, self.base, self.a).get_matching_blocks()
        bm = patiencediff.PatienceSequenceMatcher(
                None, self.base, self.b).get_matching_blocks()

        unc = []

        while am and bm:
            # there is an unconflicted block at i; how long does it
            # extend?  until whichever one ends earlier.
            a1 = am[0][0]
            a2 = a1 + am[0][2]
            b1 = bm[0][0]
            b2 = b1 + bm[0][2]
            i = intersect((a1, a2), (b1, b2))
            if i:
                unc.append(i)

            if a2 < b2:
                del am[0]
            else:
                del bm[0]

        return unc

def merge3_lists(a, b, x):
    b_added = list(set(b) - set(x))
    b_deleted = list(set(x) - set(b))
    maybe_modified = list(sorted(set(b) & set(x)))

    added = []
    deleted = []

    for name in b_deleted:
        if name in a:
            deleted.append(name)
    
    for name in b_added:
        if name in a:
            maybe_modified.append(name)
        else:
            added.append(name)
    
    maybe_modified = sorted(list(set(maybe_modified)))
    added = sorted(added)
    deleted = sorted(deleted)
    return added, deleted, maybe_modified



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
    vba_modules_x = [vba_module.name for vba_module in wb_x.vba_modules if vba_module.type != 'Document']

    # perform 3-way list merge
    added, deleted, maybe_modified = merge3_lists(a=vba_modules_a, b=vba_modules_b, x=vba_modules_x)

    # remove deleted VBA modules
    for name in deleted:
        vba_module = [m for m in wb_a.vba_modules if m.name == name][0]
        print(f'--- a/{filename}/VBA/{vba_module.type}/{name}')
        wb_a.remove_vba_module(name)

    # add VBA modules
    for name in added:
        vba_module = [m for m in wb_b.vba_modules if m.name == name][0]
        wb_a.add_vba_module(name, vba_module.type, vba_module.content)
        print(f'+++ b/{filename}/VBA/{vba_module.type}/{name}')

    conflict = False
    # merge modified VBA modules
    for name in maybe_modified:
        vba_module_a = wb_a.get_vba_module(name)
        vba_module_b = wb_b.get_vba_module(name)

        digest_a = vba_module_a.digest if vba_module_a else ''
        digest_b = vba_module_b.digest if vba_module_b else ''

        if digest_a != digest_b:
            vba_module_x = wb_x.get_vba_module(name)
            content_a = vba_module_a.content.split('\n') if vba_module_a else []
            content_b = vba_module_b.content.split('\n') if vba_module_b else []
            content_x = vba_module_x.content.split('\n') if vba_module_x else []
            # perform a 3-way merge
            m3 = Merge3(
                a=content_a,
                b=content_b,
                base=content_x)
            is_conflicted = m3.is_conflicted()
            conflict = conflict or is_conflicted
            merged = '\n'.join([line for line in m3.merge_lines(name_a=f'{name}:ours', name_b=f'{name}:theirs')])
            modify_delete_conflict = False
            if vba_module_a:
                vba_module_a.content = merged
            else:
                modify_delete_conflict = True
                wb_a.add_vba_module(name, vba_module_b.type, merged)
            m = wb_a.get_vba_module(name)
            if is_conflicted:
                if modify_delete_conflict:
                    print(f'CONFLICT (VBA modify/delete): {filename}/VBA/{m.type}/{m.name} deleted in one branch and modified in other branch')
                else:
                    print(f'CONFLICT (VBA content): Merge conflict in {filename}/VBA/{m.type}/{m.name}')
            else:
                print(f'--- a/{filename}/VBA/{m.type}/{m.name} +++ b/{filename}/VBA/{m.type}/{m.name}')

    wb_a.save()

    # rename back into original filename, otherwise git won't like it
    os.rename(a, a_)
    os.rename(b, b_)
    os.rename(x, x_)

    if conflict:
        sys.exit(1)



if __name__ == '__main__':
    merge_workbook(*sys.argv[1:])