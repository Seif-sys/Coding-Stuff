class Node:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None

class BinarySearchTree:
    def __init__(self):
        self.root = None

    def insert(self, key):
        def _insert(root, key):
            if not root:
                return Node(key)
            if key < root.key:
                root.left = _insert(root.left, key)
            elif key > root.key:
                root.right = _insert(root.right, key)
            return root

        self.root = _insert(self.root, key)

    def search(self, key):
        def _search(root, key):
            if not root or root.key == key:
                return root
            if key < root.key:
                return _search(root.left, key)
            return _search(root.right, key)

        return _search(self.root, key) is not None

    def delete(self, key):
        def _min_value_node(node):
            current = node
            while current.left:
                current = current.left
            return current

        def _delete(root, key):
            if not root:
                return root
            if key < root.key:
                root.left = _delete(root.left, key)
            elif key > root.key:
                root.right = _delete(root.right, key)
            else:
                # Node with only one child or no child
                if not root.left:
                    return root.right
                elif not root.right:
                    return root.left
                # Node with two children
                temp = _min_value_node(root.right)
                root.key = temp.key
                root.right = _delete(root.right, temp.key)
            return root

        self.root = _delete(self.root, key)

    def inorder(self):
        result = []
        def _inorder(root):
            if root:
                _inorder(root.left)
                result.append(root.key)
                _inorder(root.right)
        _inorder(self.root)
        return result
