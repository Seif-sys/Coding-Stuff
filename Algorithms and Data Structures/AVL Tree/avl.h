#include <stdio.h>
#include <stdlib.h>

typedef struct AVLNode {
    int key;
    struct AVLNode* left;
    struct AVLNode* right;
    int height;
} AVLNode;

AVLNode* insert(AVLNode* root, int key);
AVLNode* deleteNode(AVLNode* root, int key);
int search(AVLNode* root, int key);
void inorderTraversal(AVLNode* root);
void freeTree(AVLNode* root);

