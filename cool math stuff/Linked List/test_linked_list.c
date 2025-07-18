#include <stdio.h>
#include <stdlib.h>
#include "linked_list.h"

void print_list(List* list) {
    int size;
    int* arr = to_array(list, &size);
    printf("List: ");
    for (int i = 0; i < size; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
    free(arr);
}

int main() {
    List my_list = {NULL};

    // Insert elements
    insert(&my_list, 10);
    insert(&my_list, 20);
    insert(&my_list, 30);
    printf("After insertions:\n");
    print_list(&my_list); // Should be 30 20 10

    // Search
    printf("Search 20: %s\n", search(&my_list, 20) ? "Found" : "Not Found");
    printf("Search 5: %s\n", search(&my_list, 5) ? "Found" : "Not Found");

    // Delete element
    delete(&my_list, 20);
    printf("After deleting 20:\n");
    print_list(&my_list); // Should be 30 10

    // Delete non-existing
    delete(&my_list, 100); // Should do nothing
    printf("After trying to delete 100:\n");
    print_list(&my_list); // Still 30 10

    return 0;
}
