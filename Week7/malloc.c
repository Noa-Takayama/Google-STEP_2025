//
// >>>> malloc challenge! <<<<
//
// Final Stable Version: Best-fit allocator with segregated free list bins,
// boundary-tag coalescing, and a robust prologue/epilogue heap structure.
//

#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/******************************************************************************
 * OS Interface Prototypes
 *****************************************************************************/
void *mmap_from_system(size_t size);
void munmap_to_system(void *ptr, size_t size);

/******************************************************************************
 * Constants and Macros
 *****************************************************************************/
#define NUM_BINS 11
// Allocate a single large heap area to simplify memory management and avoid
// complex heap extension logic, which was the source of previous errors.
#define HEAP_INIT_SIZE (1 << 18) // 256KB initial heap

/******************************************************************************
 * Type Definitions
 *****************************************************************************/
typedef struct my_metadata_t {
  size_t size; // LSB is the is_free flag
  struct my_metadata_t *next;
} my_metadata_t;

/******************************************************************************
 * Global Variables
 *****************************************************************************/
static my_metadata_t *bins[NUM_BINS];
static void *heap_start = NULL;

/******************************************************************************
 * Function Prototypes
 *****************************************************************************/
void my_free(void *ptr);
static void coalesce_and_add_to_list(my_metadata_t *header);

/******************************************************************************
 * Helper Functions for Metadata
 *****************************************************************************/
static inline size_t get_size(my_metadata_t *m) { return m->size & ~1UL; }
static inline bool is_free(my_metadata_t *m) { return m->size & 1UL; }

static inline void set_size_and_flag(my_metadata_t *hdr, size_t payload_size, bool free_flag) {
  hdr->size = payload_size | (free_flag ? 1UL : 0UL);
  my_metadata_t *ftr = (my_metadata_t *)((char *)(hdr + 1) + payload_size) - 1;
  ftr->size = hdr->size;
}

static inline my_metadata_t* get_next_header(my_metadata_t* hdr) {
  return (my_metadata_t*)((char*)(hdr + 1) + get_size(hdr));
}

static inline my_metadata_t* get_header_from_footer(my_metadata_t* ftr) {
  return (my_metadata_t *)((char *)ftr - get_size(ftr)) - 1;
}

/******************************************************************************
 * Bin and Free List Management
 *****************************************************************************/
static int get_bin_index(size_t size) {
  if (size <= 16) return 0;
  if (size <= 32) return 1;
  if (size <= 64) return 2;
  if (size <= 128) return 3;
  if (size <= 256) return 4;
  if (size <= 512) return 5;
  if (size <= 1024) return 6;
  if (size <= 2048) return 7;
  if (size <= 4000) return 8;
  if (size <= 8192) return 9;
  return 10;
}

static void add_to_bin(my_metadata_t *blk) {
  int idx = get_bin_index(get_size(blk));
  blk->next = bins[idx];
  bins[idx] = blk;
}

static void remove_from_bin(my_metadata_t *blk) {
  int idx = get_bin_index(get_size(blk));
  my_metadata_t **p = &bins[idx];
  while (*p && *p != blk) {
    p = &(*p)->next;
  }
  if (*p) {
    *p = blk->next;
  }
}

/******************************************************************************
 * Core Allocator Logic
 *****************************************************************************/
void my_initialize() {
  for (int i = 0; i < NUM_BINS; ++i) {
    bins[i] = NULL;
  }
  heap_start = NULL;
}

void *my_malloc(size_t size) {
  if (size == 0) return NULL;
  size_t required_payload = (size + 7) & ~7UL;

  // Initialize heap on first call
  if (heap_start == NULL) {
    heap_start = mmap_from_system(HEAP_INIT_SIZE);
    if (heap_start == (void*)-1) {
        heap_start = NULL;
        return NULL;
    }
    
    // Prologue block (header and footer)
    my_metadata_t* prologue = (my_metadata_t*)heap_start;
    set_size_and_flag(prologue, 0, false);

    // Initial free block
    my_metadata_t* initial_block = (my_metadata_t*)((char*)heap_start + 2 * sizeof(my_metadata_t));
    size_t initial_payload_size = HEAP_INIT_SIZE - 4 * sizeof(my_metadata_t);
    set_size_and_flag(initial_block, initial_payload_size, true);
    
    // Epilogue block (header only)
    my_metadata_t* epilogue_header = get_next_header(initial_block);
    epilogue_header->size = 0; // size 0, used
    
    add_to_bin(initial_block);
  }

  int start_bin = get_bin_index(required_payload);
  my_metadata_t *block = NULL;

  for (int i = start_bin; i < NUM_BINS; ++i) {
    my_metadata_t *current = bins[i];
    my_metadata_t *best_fit = NULL;
    while (current) {
      if (get_size(current) >= required_payload) {
        if (best_fit == NULL || get_size(current) < get_size(best_fit)) {
          best_fit = current;
        }
      }
      current = current->next;
    }
    if (best_fit) {
      block = best_fit;
      break;
    }
  }

  if (block == NULL) {
    return NULL; // Out of memory
  }

  remove_from_bin(block);
  size_t block_size = get_size(block);
  size_t remaining = block_size - required_payload;

  if (remaining >= 2 * sizeof(my_metadata_t) + 8) {
    set_size_and_flag(block, required_payload, false);
    my_metadata_t *split = get_next_header(block);
    set_size_and_flag(split, remaining - 2 * sizeof(my_metadata_t), true);
    coalesce_and_add_to_list(split);
  } else {
    set_size_and_flag(block, block_size, false);
  }
  return (void *)(block + 1);
}

void my_free(void *ptr) {
  if (ptr == NULL) return;
  my_metadata_t *header = (my_metadata_t *)ptr - 1;
  coalesce_and_add_to_list(header);
}

static void coalesce_and_add_to_list(my_metadata_t *header) {
  my_metadata_t *next_header = get_next_header(header);
  my_metadata_t *prev_footer = (my_metadata_t*)header - 1;
  
  bool prev_is_free = is_free(prev_footer);
  bool next_is_free = is_free(next_header);
  size_t size = get_size(header);

  if (prev_is_free && next_is_free) {
    my_metadata_t *prev_header = get_header_from_footer(prev_footer);
    remove_from_bin(prev_header);
    remove_from_bin(next_header);
    size += get_size(prev_header) + get_size(next_header) + 2 * sizeof(my_metadata_t);
    header = prev_header;
  } else if (prev_is_free) {
    my_metadata_t *prev_header = get_header_from_footer(prev_footer);
    remove_from_bin(prev_header);
    size += get_size(prev_header) + 2 * sizeof(my_metadata_t);
    header = prev_header;
  } else if (next_is_free) {
    remove_from_bin(next_header);
    size += get_size(next_header) + 2 * sizeof(my_metadata_t);
  }
  
  set_size_and_flag(header, size, true);
  add_to_bin(header);
}

void my_finalize() {}
void test() {}