#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct Node {
    int key;
    struct Node* left;
    struct Node* right;
} Node;

typedef struct {
    Node* root;
} BinarySearchTree;

Node* create_node(int key) {
    Node* new_node = (Node*)malloc(sizeof(Node));
    new_node->key = key;
    new_node->left = NULL;
    new_node->right = NULL;
    return new_node;
}

BinarySearchTree* create_bst() {
    BinarySearchTree* bst = (BinarySearchTree*)malloc(sizeof(BinarySearchTree));
    bst->root = NULL;
    return bst;
}

Node* insert_node(Node* root, int key) {
    if (root == NULL) return create_node(key);
    if (key < root->key)
        root->left = insert_node(root->left, key);
    else if (key > root->key)
        root->right = insert_node(root->right, key);
    return root;
}

void insert(BinarySearchTree* bst, int key) {
    bst->root = insert_node(bst->root, key);
}

bool search_node(Node* root, int key) {
    if (root == NULL) return false;
    if (key == root->key) return true;
    if (key < root->key)
        return search_node(root->left, key);
    return search_node(root->right, key);
}

bool search(BinarySearchTree* bst, int key) {
    return search_node(bst->root, key);
}

Node* min_value_node(Node* node) {
    Node* current = node;
    while (current && current->left != NULL)
        current = current->left;
    return current;
}

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

void delete(BinarySearchTree* bst, int key) {
    bst->root = delete_node(bst->root, key);
}

void inorder_node(Node* root) { //helper function for inorder
    if (root != NULL) {
        inorder_node(root->left);
        printf("%d ", root->key);
        inorder_node(root->right);
    }
}

void inorder(BinarySearchTree* bst) {
    inorder_node(bst->root);
    printf("\n");
}

