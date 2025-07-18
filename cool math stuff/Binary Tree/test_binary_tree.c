#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include "binary_tree.h"  // contains your BST functions and definitions

void test_insert_and_search() {
    BinarySearchTree* tree = create_bst();
    insert(tree, 10);
    insert(tree, 5);
    insert(tree, 15);
    insert(tree, 3);
    insert(tree, 7);
    insert(tree, 20);

    assert(search(tree, 10) == true);
    assert(search(tree, 5) == true);
    assert(search(tree, 20) == true);
    assert(search(tree, 100) == false);

    printf("test_insert_and_search passed.\n");
}

void test_delete() {
    BinarySearchTree* tree = create_bst();
    insert(tree, 10);
    insert(tree, 5);
    insert(tree, 15);

    delete(tree, 5);
    assert(search(tree, 5) == false);

    delete(tree, 10);
    assert(search(tree, 10) == false);

    printf("test_delete passed.\n");
}

void collect_inorder(Node* root, int* result, int* index) {
    if (root) {
        collect_inorder(root->left, result, index);
        result[(*index)++] = root->key;
        collect_inorder(root->right, result, index);
    }
}

void test_inorder_traversal() {
    BinarySearchTree* tree = create_bst();
    insert(tree, 10);
    insert(tree, 5);
    insert(tree, 15);
    insert(tree, 3);
    insert(tree, 7);

    int result[10];
    int index = 0;
    collect_inorder(tree->root, result, &index);

    int expected[] = {3, 5, 7, 10, 15};
    for (int i = 0; i < 5; i++) {
        assert(result[i] == expected[i]);
    }

    printf("test_inorder_traversal passed.\n");
}

int main() {
    test_insert_and_search();
    test_delete();
    test_inorder_traversal();

    printf("All tests passed.\n");
    return 0;
}
