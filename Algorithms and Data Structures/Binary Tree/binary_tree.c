#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

// Node definition
typedef struct Node {
    int key;
    struct Node* left;
    struct Node* right;
} Node;

// BinarySearchTree definition
typedef struct {
    Node* root;
} BinarySearchTree;

// Create a new node
Node* create_node(int key) {
    Node* new_node = (Node*)malloc(sizeof(Node));
    new_node->key = key;
    new_node->left = NULL;
    new_node->right = NULL;
    return new_node;
}

// Initialize the BST
BinarySearchTree* create_bst() {
    BinarySearchTree* bst = (BinarySearchTree*)malloc(sizeof(BinarySearchTree));
    bst->root = NULL;
    return bst;
}

// Insert helper
Node* insert_node(Node* root, int key) {
    if (root == NULL) return create_node(key);
    if (key < root->key)
        root->left = insert_node(root->left, key);
    else if (key > root->key)
        root->right = insert_node(root->right, key);
    return root;
}

// Insert into BST
void insert(BinarySearchTree* bst, int key) {
    bst->root = insert_node(bst->root, key);
}

// Search helper
bool search_node(Node* root, int key) {
    if (root == NULL) return false;
    if (key == root->key) return true;
    if (key < root->key)
        return search_node(root->left, key);
    return search_node(root->right, key);
}

// Search in BST
bool search(BinarySearchTree* bst, int key) {
    return search_node(bst->root, key);
}

// Find minimum node
Node* min_value_node(Node* node) {
    Node* current = node;
    while (current && current->left != NULL)
        current = current->left;
    return current;
}

// Delete helper
Node* delete_node(Node* root, int key) {
    if (root == NULL) return root;

    if (key < root->key) {
        root->left = delete_node(root->left, key);
    } else if (key > root->key) {
        root->right = delete_node(root->right, key);
    } else {
        // Node with only one child or no child
        if (root->left == NULL) {
            Node* temp = root->right;
            free(root);
            return temp;
        }
        else if (root->right == NULL) {
            Node* temp = root->left;
            free(root);
            return temp;
        }

        // Node with two children
        Node* temp = min_value_node(root->right);
        root->key = temp->key;
        root->right = delete_node(root->right, temp->key);
    }
    return root;
}

// Delete from BST
void delete(BinarySearchTree* bst, int key) {
    bst->root = delete_node(bst->root, key);
}

// Inorder traversal helper
void inorder_node(Node* root) {
    if (root != NULL) {
        inorder_node(root->left);
        printf("%d ", root->key);
        inorder_node(root->right);
    }
}

// Inorder traversal
void inorder(BinarySearchTree* bst) {
    inorder_node(bst->root);
    printf("\n");
}

