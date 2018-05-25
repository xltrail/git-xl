from unittest import TestCase
from merge import Merge3, merge3_lists


class TestThreeWayListMerge(TestCase):
    
    def test_added_deleted(self):
        x = ['Module1']
        a = ['Module1', 'Module2']
        b = ['Module1', 'Module3']
        added, deleted, maybe_modified = merge3_lists(a=a, b=b, x=x)
        self.assertEqual(added, ['Module3'])
        self.assertEqual(deleted, [])
        self.assertEqual(maybe_modified, ['Module1'])

    def test_deleted_modified(self):
        x = ['Module1', 'Module2']
        a = ['Module1']
        b = ['Module1', 'Module2']
        added, deleted, maybe_modified = merge3_lists(a=a, b=b, x=x)
        self.assertEqual(added, [])
        self.assertEqual(deleted, [])
        self.assertEqual(maybe_modified, ['Module1', 'Module2'])


class TestThreeWayMerge(TestCase):


    def test_conflict(self):
        a = ['Option Explicit', "'test1", 'Sub test()', '    Debug.Print "hello1"', 'End Sub']
        b = ['Option Explicit', 'Function test()', '    Debug.Print "hello1"', '    test = "test"', 'End Function']
        x = ['Option Explicit', 'Sub test()', '    Debug.Print "hello1"', 'End Sub']
        m3 = Merge3(a=a, b=b, base=x)
        self.assertTrue(m3.is_conflicted())
        self.assertEqual(
            ['Option Explicit', '<<<<<<< ours\n', "'test1", 'Sub test()', '=======\n', 'Function test()', '>>>>>>> theirs\n', '    Debug.Print "hello1"', '    test = "test"', 'End Function'],
            [x for x in m3.merge_lines(name_a='ours', name_b='theirs')]
        )
