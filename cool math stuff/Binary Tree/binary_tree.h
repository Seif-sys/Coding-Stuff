#ifndef BINARY_TREE_H
#define BINARY_TREE_H

#include <stdbool.h>

typedef struct Node {
    int key;
    struct Node* left;
    struct Node* right;
} Node;

typedef struct {
    Node* root;
} BinarySearchTree;

BinarySearchTree* create_bst();
Node* create_node(int key);
void insert(BinarySearchTree* bst, int key);
bool search(BinarySearchTree* bst, int key);
void delete(BinarySearchTree* bst, int key);
void inorder(BinarySearchTree* bst);

#endif
