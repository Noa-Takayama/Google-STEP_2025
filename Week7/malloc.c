//
// >>>> malloc challenge! <<<<
//
// Your task is to improve utilization and speed of the following malloc
// implementation.
// Initial implementation is the same as the one implemented in simple_malloc.c.
// For the detailed explanation, please refer to simple_malloc.c.

#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Free List Bin のための定数定義
#define NUM_BINS 10 // ビンの数を定義

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

// my_heap_t 構造体をビン分割用に変更
typedef struct my_heap_t {
  my_metadata_t *free_heads[NUM_BINS]; // ビンの数だけリストの先頭を持つ
  my_metadata_t dummies[NUM_BINS];     // ダミーもビンの数だけ用意
} my_heap_t;

//
// Static variables (DO NOT ADD ANOTHER STATIC VARIABLES!)
//
my_heap_t my_heap;

//
// Helper functions (feel free to add/remove/edit!)
//

// サイズから対応するビンのインデックスを返すヘルパー関数
static int get_bin_index(size_t size) {
  // 8バイトから4000バイトまでをカバーするように分割
  // 例: 8, 16, 32, 64, 128, 256, 512, 1024, 2048, それ以上
  if (size <= 16) return 0;
  if (size <= 32) return 1;
  if (size <= 64) return 2;
  if (size <= 128) return 3;
  if (size <= 256) return 4;
  if (size <= 512) return 5;
  if (size <= 1024) return 6;
  if (size <= 2048) return 7;
  if (size <= 4000) return 8;
  return 9; // 4000バイトより大きい場合 (今回は発生しないはず)
}


//
// Interfaces of malloc (DO NOT RENAME FOLLOWING FUNCTIONS!)
//

// This is called at the beginning of each challenge.
// 全てのビンを初期化するように変更
void my_initialize() {
  for (int i = 0; i < NUM_BINS; i++) {
    my_heap.free_heads[i] = &my_heap.dummies[i];
    my_heap.dummies[i].size = 0;
    my_heap.dummies[i].next = NULL;
  }
}

// my_malloc() is called every time an object is allocated.
// |size| is guaranteed to be a multiple of 8 bytes and meets 8 <= |size| <=
// 4000. You are not allowed to use any library functions other than
// mmap_from_system() / munmap_to_system().
void *my_malloc(size_t size) {
  // 1. 要求サイズに合うビンを探す
  int start_index = get_bin_index(size);
  my_metadata_t *metadata = NULL;
  my_metadata_t *prev = NULL;

  // 2. そのビンから、より大きいサイズのビンを順に探索
  for (int i = start_index; i < NUM_BINS; i++) {
    // 現在のビンで First-Fit を試す
    my_metadata_t *head = my_heap.free_heads[i];
    prev = NULL;
    // ダミーノードは metadata->size == 0 なので、それで判定
    while (head && (head->size < size || head->size == 0)) {
      prev = head;
      head = head->next;
    }
    if (head) { // 見つかった！
      metadata = head;
      break;
    }
  }

  // 5. どのビンにも適切な空きがなかった場合
  if (!metadata) {
    // OSから新しいメモリを確保
    size_t buffer_size = 4096;
    metadata = (my_metadata_t *)mmap_from_system(buffer_size);
    metadata->size = buffer_size - sizeof(my_metadata_t);
    metadata->next = NULL;
    // この新しいブロックは、後続の分割処理にそのまま渡す
    prev = NULL; // 新規ブロックなので prev はない
  }
  
  // 見つけた、あるいは新規確保したブロックをリストから外す
  if (prev) {
    prev->next = metadata->next;
  } else {
    // リストの先頭だったので、対応するビンのヘッドを更新
    int current_bin_index = get_bin_index(metadata->size);
    my_heap.free_heads[current_bin_index] = metadata->next;
  }
  metadata->next = NULL;

  // |ptr| is the beginning of the allocated object.
  void *ptr = metadata + 1;
  size_t remaining_size = metadata->size - size;

  // 4. ブロック分割と余りの処理
  if (remaining_size > sizeof(my_metadata_t)) {
    metadata->size = size;
    my_metadata_t *new_metadata = (my_metadata_t *)((char *)ptr + size);
    new_metadata->size = remaining_size - sizeof(my_metadata_t);
    
    // ★★★ 余りをサイズに合った正しいビンに戻す
    int new_index = get_bin_index(new_metadata->size);
    new_metadata->next = my_heap.free_heads[new_index];
    my_heap.free_heads[new_index] = new_metadata;
  }

  return ptr;
}

// This is called every time an object is freed.  You are not allowed to
// use any library functions other than mmap_from_system / munmap_to_system.
void my_free(void *ptr) {
  // Look up the metadata. The metadata is placed just prior to the object.
  my_metadata_t *metadata = (my_metadata_t *)ptr - 1;

  // 解放するブロックのサイズから、どのビンに入れるべきか決定
  int index = get_bin_index(metadata->size);

  // 対応するビンのフリーリストの先頭に追加
  metadata->next = my_heap.free_heads[index];
  my_heap.free_heads[index] = metadata;
}

// This is called at the end of each challenge.
void my_finalize() {
  // Nothing is here for now.
  // feel free to add something if you want!
}

void test() {
  // Implement here!
  assert(1 == 1); /* 1 is 1. That's always true! (You can remove this.) */
}