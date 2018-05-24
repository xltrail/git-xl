from unittest import TestCase
from merge import Merge3


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
