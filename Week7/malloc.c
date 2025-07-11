// 左右結合とbestfitを組み合わせようとしたが、何度してもsegmentation faultが発生してしまったので断念

#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void *mmap_from_system(size_t size);
void munmap_to_system(void *ptr, size_t size);

#define CHUNK_SIZE 4096 // my_initializeで最初にOSから確保するヒープ領域のサイズ
#define MIN_BLOCK_PAYLOAD (8) // 最小のペイロードサイズ
#define MIN_BLOCK_SIZE (2 * sizeof(my_metadata_t) + MIN_BLOCK_PAYLOAD) // ヘッダ・フッタ・ペイロード

typedef struct my_metadata_t {
  size_t size; // LSB(最下位ビット)は「空きブロックか否か」のフラグとして使用
  struct my_metadata_t *next; // 空きブロックリスト（フリーリスト）を繋ぐためのポインタ
} my_metadata_t;

static my_metadata_t *free_list_head = NULL;

void my_free(void *ptr);
static my_metadata_t *coalesce(my_metadata_t *header);

static inline size_t get_size(my_metadata_t *m) { return m->size & ~1UL; }
static inline bool is_free(my_metadata_t *m) { return m->size & 1UL; }

static inline void set_size_and_flag(my_metadata_t *hdr, size_t payload_size, bool free_flag) {
  hdr->size = payload_size | (free_flag ? 1UL : 0UL);
  my_metadata_t *ftr = (my_metadata_t *)((char *)(hdr + 1) + payload_size) - 1;
  ftr->size = hdr->size;
}

// 次のブロックのヘッダのアドレス
static inline my_metadata_t* get_next_header(my_metadata_t* hdr) {
  return (my_metadata_t*)((char*)(hdr + 1) + get_size(hdr));
}

// 前のブロックのフッタのアドレス
static inline my_metadata_t* get_prev_footer(my_metadata_t* hdr) {
  return (my_metadata_t *)((char *)hdr - sizeof(my_metadata_t));
}

// フッタからヘッダのアドレス
static inline my_metadata_t* get_header_from_footer(my_metadata_t* ftr) {
  return (my_metadata_t *)((char *)ftr - get_size(ftr) - sizeof(my_metadata_t));
}

// フリーリスト操作
static void add_to_list(my_metadata_t *blk) {
  blk->next = free_list_head;
  free_list_head = blk;
}

static void remove_from_list(my_metadata_t *blk) {
  my_metadata_t **p = &free_list_head;
  while (*p && *p != blk) {
    p = &(*p)->next;
  }
  if (*p) {
    *p = blk->next;
  }
}

// 初期化
void my_initialize() {
  void* heap = mmap_from_system(CHUNK_SIZE);
  my_metadata_t* prologue = (my_metadata_t*)heap;
  set_size_and_flag(prologue, 0, false);

  my_metadata_t* epilogue = (my_metadata_t*)((char*)heap + CHUNK_SIZE - 2*sizeof(my_metadata_t));
  set_size_and_flag(epilogue, 0, false);

  free_list_head = (my_metadata_t*)((char*)prologue + 2*sizeof(my_metadata_t));
  size_t initial_payload = CHUNK_SIZE - 4*sizeof(my_metadata_t);
  set_size_and_flag(free_list_head, initial_payload, true);
  free_list_head->next = NULL;
}

// メモリ割り当て
void *my_malloc(size_t size) {
  if (size == 0) return NULL;
  size_t required_payload = (size + 7) & ~7UL;

  my_metadata_t *current = free_list_head;
  my_metadata_t *best_fit = NULL;

  while (current) {
    if (get_size(current) >= required_payload) {
      if (best_fit == NULL || get_size(current) < get_size(best_fit)) {
        best_fit = current;
      }
    }
    current = current->next;
  }

  if (best_fit == NULL) {
    return NULL;
  }

  // ここが一番処理が重い
  // なぜなら, best_fitを見つけた後に
  // best_fitをフリーリストから削除し、必要に応じて
  // best_fitを分割しているから
  // ここを二分探索などにして
  // 処理を高速化できるかもしれない
  remove_from_list(best_fit);
  size_t block_size = get_size(best_fit);
  size_t remaining = block_size - required_payload;

  if (remaining >= MIN_BLOCK_SIZE) {
    set_size_and_flag(best_fit, required_payload, false);
    my_metadata_t *split = get_next_header(best_fit);
    set_size_and_flag(split, remaining - 2 * sizeof(my_metadata_t), true);
    my_free(split + 1);
  } else {
    set_size_and_flag(best_fit, block_size, false);
  }

  return (void *)(best_fit + 1);
}

// メモリ解放
void my_free(void *ptr) {
  if (ptr == NULL) return;
  my_metadata_t *header = (my_metadata_t *)ptr - 1;
  my_metadata_t *coalesced_block = coalesce(header);
  add_to_list(coalesced_block);
}

// 左右結合
static my_metadata_t *coalesce(my_metadata_t *header) {
  my_metadata_t *next_header = get_next_header(header);
  my_metadata_t *prev_footer = get_prev_footer(header);

  bool prev_is_free = is_free(prev_footer);
  bool next_is_free = is_free(next_header);
  size_t size = get_size(header);

  if (prev_is_free && next_is_free) {
    my_metadata_t *prev_header = get_header_from_footer(prev_footer);
    remove_from_list(prev_header);
    remove_from_list(next_header);
    size += get_size(prev_header) + get_size(next_header) + 2 * sizeof(my_metadata_t);
    header = prev_header;
  } else if (prev_is_free) {
    my_metadata_t *prev_header = get_header_from_footer(prev_footer);
    remove_from_list(prev_header);
    size += get_size(prev_header) + 2 * sizeof(my_metadata_t);
    header = prev_header;
  } else if (next_is_free) {
    remove_from_list(next_header);
    size += get_size(next_header) + 2 * sizeof(my_metadata_t);
  }

  set_size_and_flag(header, size, true);
  return header;
}

void my_finalize() {}

void test() {}