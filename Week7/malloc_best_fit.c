//
// Best-fit allocator based on the simple first-fit implementation.
// Features:
// - Single free list
// - Best-fit search strategy
// - No coalescing
// - No bins
//

#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

//
// Interfaces to get memory pages from OS
//
void *mmap_from_system(size_t size);
void munmap_to_system(void *ptr, size_t size);

//
// Struct definitions
//
typedef struct my_metadata_t {
  size_t size;
  struct my_metadata_t *next;
} my_metadata_t;

typedef struct my_heap_t {
  my_metadata_t *free_head;
  my_metadata_t dummy;
} my_heap_t;

//
// Static variables
//
my_heap_t my_heap;

//
// Helper functions
//
void my_add_to_free_list(my_metadata_t *metadata) {
  assert(!metadata->next);
  metadata->next = my_heap.free_head;
  my_heap.free_head = metadata;
}

void my_remove_from_free_list(my_metadata_t *metadata, my_metadata_t *prev) {
  if (prev) {
    prev->next = metadata->next;
  } else {
    my_heap.free_head = metadata->next;
  }
  metadata->next = NULL;
}

//
// Interfaces of malloc
//
void my_initialize() {
  my_heap.free_head = &my_heap.dummy;
  my_heap.dummy.size = 0;
  my_heap.dummy.next = NULL;
}

void *my_malloc(size_t size) {
  my_metadata_t *best_fit = NULL;
  my_metadata_t *best_fit_prev = NULL;
  my_metadata_t *current = my_heap.free_head;
  my_metadata_t *prev = NULL;

  // Best-fit: Find the smallest free slot that the object fits.
  while (current) {
    if (current->size >= size) {
      if (best_fit == NULL || current->size < best_fit->size) {
        best_fit = current;
        best_fit_prev = prev;
      }
    }
    prev = current;
    current = current->next;
  }

  my_metadata_t *metadata = best_fit;
  prev = best_fit_prev;

  if (!metadata) {
    // There was no free slot available.
    size_t buffer_size = 4096;
    my_metadata_t *new_chunk = (my_metadata_t *)mmap_from_system(buffer_size);
    new_chunk->size = buffer_size - sizeof(my_metadata_t);
    new_chunk->next = NULL;
    my_add_to_free_list(new_chunk);
    // Try my_malloc() again.
    return my_malloc(size);
  }

  void *ptr = metadata + 1;
  size_t remaining_size = metadata->size - size;
  my_remove_from_free_list(metadata, prev);

  if (remaining_size > sizeof(my_metadata_t)) {
    metadata->size = size;
    my_metadata_t *new_metadata = (my_metadata_t *)((char *)ptr + size);
    new_metadata->size = remaining_size - sizeof(my_metadata_t);
    new_metadata->next = NULL;
    my_add_to_free_list(new_metadata);
  }
  return ptr;
}

void my_free(void *ptr) {
  my_metadata_t *metadata = (my_metadata_t *)ptr - 1;
  my_add_to_free_list(metadata);
}

void my_finalize() {
  // Nothing to do.
}

void test() {
  // This function must exist for the linker.
}