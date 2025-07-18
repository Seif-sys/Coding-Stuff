#include "avl.h"

int getHeight(AVLNode* node) {
    return (node == NULL) ? 0 : node->height;
}
int getBalanceFactor(AVLNode* node) {
    return (node == NULL) ? 0 : getHeight(node->left) - getHeight(node->right);
}
AVLNode* createNode(int key) {
    AVLNode* newNode = (AVLNode*) malloc(sizeof(AVLNode));
    newNode->key = key;
    newNode->left = newNode->right = NULL;
    newNode->height = 1;
    return newNode;
}

AVLNode* rightRotate(AVLNode* y) {
    AVLNode* x = y->left;
    AVLNode* T2 = x->right;

    x->right = y;
    y->left = T2;

    y->height = 1 + ((getHeight(y->left) > getHeight(y->right)) ? getHeight(y->left) : getHeight(y->right));
    x->height = 1 + ((getHeight(x->left) > getHeight(x->right)) ? getHeight(x->left) : getHeight(x->right));

    return x;
}

AVLNode* leftRotate(AVLNode* x) {
    AVLNode* y = x->right;
    AVLNode* T2 = y->left;

    y->left = x;
    x->right = T2;

    x->height = 1 + ((getHeight(x->left) > getHeight(x->right)) ? getHeight(x->left) : getHeight(x->right));
    y->height = 1 + ((getHeight(y->left) > getHeight(y->right)) ? getHeight(y->left) : getHeight(y->right));

    return y;
}

AVLNode* insert(AVLNode* root, int key) {
    if (root == NULL)
        return createNode(key);

    if (key < root->key)
        root->left = insert(root->left, key);
    else if (key > root->key)
        root->right = insert(root->right, key);
    else
        return root; 

    root->height = 1 + ((getHeight(root->left) > getHeight(root->right)) ? getHeight(root->left) : getHeight(root->right));

    int balance = getBalanceFactor(root);

    if (balance > 1 && key < root->left->key) 
        return rightRotate(root);
    if (balance < -1 && key > root->right->key) 
        return leftRotate(root);
    if (balance > 1 && key > root->left->key) { 
        root->left = leftRotate(root->left);
        return rightRotate(root);
    }
    if (balance < -1 && key < root->right->key) { 
        root->right = rightRotate(root->right);
        return leftRotate(root);
    }

    return root;
}

AVLNode* minValueNode(AVLNode* node) {
    AVLNode* current = node;
    while (current->left != NULL)
        current = current->left;
    return current;
}

AVLNode* deleteNode(AVLNode* root, int key) {
    if (root == NULL)
        return root;

    if (key < root->key)
        root->left = deleteNode(root->left, key);
    else if (key > root->key)
        root->right = deleteNode(root->right, key);
    else {
        if (root->left == NULL || root->right == NULL) {
            AVLNode* temp = root->left ? root->left : root->right;
            free(root);
            return temp;
        }
        AVLNode* temp = minValueNode(root->right);
        root->key = temp->key;
        root->right = deleteNode(root->right, temp->key);
    }

    root->height = 1 + ((getHeight(root->left) > getHeight(root->right)) ? getHeight(root->left) : getHeight(root->right));

    int balance = getBalanceFactor(root);

    if (balance > 1 && getBalanceFactor(root->left) >= 0) 
        return rightRotate(root);
    if (balance > 1 && getBalanceFactor(root->left) < 0) { 
        root->left = leftRotate(root->left);
        return rightRotate(root);
    }
    if (balance < -1 && getBalanceFactor(root->right) <= 0) 
        return leftRotate(root);
    if (balance < -1 && getBalanceFactor(root->right) > 0) { 
        root->right = rightRotate(root->right);
        return leftRotate(root);
    }

    return root;
}

int search(AVLNode* root, int key) {
    if (root == NULL)
        return 0;
    if (root->key == key)
        return 1;
    return (key < root->key) ? search(root->left, key) : search(root->right, key);
}

void inorderTraversal(AVLNode* root) {
    if (root != NULL) {
        inorderTraversal(root->left);
        printf("%d ", root->key);
        inorderTraversal(root->right);
    }
}

void freeTree(AVLNode* root) {
    if (root != NULL) {
        freeTree(root->left);
        freeTree(root->right);
        free(root);
    }
}

//TODO: Comment and create a test unit for AVL