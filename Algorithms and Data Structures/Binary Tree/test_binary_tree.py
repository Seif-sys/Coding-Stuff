import unittest
from binary_tree import BinarySearchTree

class TestBinaryTree(unittest.TestCase):

    def setUp(self):
        self.tree = BinarySearchTree()
        self.tree.insert(10)
        self.tree.insert(5)
        self.tree.insert(15)
        self.tree.insert(3)
        self.tree.insert(7)

    def test_insert(self):
        # Test inserting elements into the binary tree
        self.tree.insert(20)
        self.assertTrue(self.tree.search(20))  
        self.assertFalse(self.tree.search(100))  

    def test_search(self):
        # Test searching for an element
        self.assertTrue(self.tree.search(10))  
        self.assertFalse(self.tree.search(100))  

    def test_delete(self):
        # Test deleting a node
        self.tree.delete(5)  
        self.assertFalse(self.tree.search(5))  
        self.tree.delete(10)  
        self.assertFalse(self.tree.search(10))  

    def test_in_order_traversal(self):
        # Test in-order traversal (should return sorted order of inserted nodes)
        result = self.tree.inorder()
        self.assertEqual(result, [3, 5, 7, 10, 15])  

    def tearDown(self):
        del self.tree

if __name__ == '__main__':
    unittest.main()