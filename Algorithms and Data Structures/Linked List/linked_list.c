// linked_list.c
#include <stdio.h>
#include <stdlib.h>
#include "linked_list.h"

Node* create_node(int data) {
    Node* new_node = (Node*) malloc(sizeof(Node));
    if (!new_node) {
        perror("Failed to allocate node");
        exit(1);
    }
    new_node->data = data;
    new_node->next = NULL;
    return new_node;
}

void insert(List* list, int value) {
    Node* new_node = create_node(value);
    new_node->next = list->head;
    list->head = new_node;
}

void delete(List* list, int key) {
    Node* temp = list->head;
    Node* prev = NULL;

    while (temp && temp->data != key) {
        prev = temp;
        temp = temp->next;
    }

    if (!temp) return; // Key not found

    if (prev) {
        prev->next = temp->next;
    } else {
        list->head = temp->next;
    }

    free(temp);
}

int search(List* list, int key) {
    Node* current = list->head;
    while (current) {
        if (current->data == key) return 1;
        current = current->next;
    }
    return 0;
}

int* to_array(List* list, int* size) {
    Node* current = list->head;
    int count = 0;

    // First pass: count
    while (current) {
        count++;
        current = current->next;
    }

    *size = count;
    int* arr = (int*) malloc(sizeof(int) * count);
    current = list->head;

    // Second pass: copy data
    for (int i = 0; i < count; i++) {
        arr[i] = current->data;
        current = current->next;
    }

    return arr;
}
