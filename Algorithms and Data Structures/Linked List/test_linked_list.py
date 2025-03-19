import unittest
from linked_list import List

class TestLinkedList(unittest.TestCase):

    def setUp(self):
        self.ll = List()
        self.ll.insert(10)
        self.ll.insert(20)
        self.ll.insert(30)

    def test_insert(self):
        # Test inserting elements at the beginning
        self.ll.insert(40)
        result = self.ll.to_list()
        self.assertEqual(result, [40, 30, 20, 10])  # 40 should be at the beginning

    def test_search(self):
        # Test searching for an element
        self.assertTrue(self.ll.search(20))  # 20 is in the list
        self.assertFalse(self.ll.search(100))  # 100 is not in the list

    def test_delete(self):
        # Test deleting an element
        self.ll.delete(20)  # Deleting node with value 20
        result = self.ll.to_list()
        self.assertEqual(result, [30, 10])  # 20 should no longer be in the list
        self.ll.delete(30)  # Deleting node with value 30
        result = self.ll.to_list()
        self.assertEqual(result, [10])  # 30 should no longer be in the list

    def test_traversal(self):
        # Test traversing the list
        result = self.ll.to_list()
        self.assertEqual(result, [30, 20, 10])  # Order should be preserved (from head to tail)

    def tearDown(self):
        del self.ll

if __name__ == '__main__':
    unittest.main()
