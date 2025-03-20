#ifndef LINKED_LIST_H
#define LINKED_LIST_H

typedef struct Node {
    int data;
    struct Node* next;
} Node;

typedef struct {
    Node* head;
} List;

Node* create_node(int data);
void insert(List* list, int value);
void delete(List* list, int key);
int search(List* list, int key);
int* to_array(List* list, int* size);

#endif
