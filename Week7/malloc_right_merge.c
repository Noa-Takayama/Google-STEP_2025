// free first bin + 右結合の実装

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

// is_freeフラグをサイズの下位1ビットに格納
typedef struct my_metadata_t {
  size_t size; // 下位1ビットはis_freeフラグとして使用
  struct my_metadata_t *next;
} my_metadata_t;

// my_heap_t 構造体はビン分割のまま
typedef struct my_heap_t {
  my_metadata_t *free_heads[NUM_BINS];
  my_metadata_t dummies[NUM_BINS];
} my_heap_t;

//
// Static variables (DO NOT ADD ANOTHER STATIC VARIABLES!)
//
my_heap_t my_heap;


//
// Function Prototypes (エラー解決のために追加)
//
void my_free(void *ptr);


//
// Helper functions
//

// メタデータから実際のサイズを取得（下位1ビットを無視）
static inline size_t get_size(my_metadata_t *metadata) {
  return metadata->size & ~1UL;
}

// メタデータにサイズとis_freeフラグを設定
static inline void set_size_and_flag(my_metadata_t *metadata, size_t size, bool is_free) {
  metadata->size = size | (is_free ? 1UL : 0UL);
}

// メタデータがフリーかどうかをチェック
static inline bool is_free(my_metadata_t *metadata) {
  return (metadata->size & 1UL) != 0;
}

// サイズから対応するビンのインデックスを返す
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
  return 9;
}

// 指定されたビンにフリーブロックを追加する
static void add_to_free_list(my_metadata_t *metadata) {
  size_t size = get_size(metadata);
  int index = get_bin_index(size);
  metadata->next = my_heap.free_heads[index];
  my_heap.free_heads[index] = metadata;
}

// フリーリストからブロックを削除する
static void remove_from_free_list(my_metadata_t *metadata) {
    size_t size = get_size(metadata);
    int index = get_bin_index(size);
    my_metadata_t *head = my_heap.free_heads[index];
    my_metadata_t *prev = NULL;

    while (head != metadata) {
        assert(head != NULL); // Should be found
        prev = head;
        head = head->next;
    }

    if (prev) {
        prev->next = head->next;
    } else {
        my_heap.free_heads[index] = head->next;
    }
}


//
// Interfaces of malloc (DO NOT RENAME FOLLOWING FUNCTIONS!)
//

void my_initialize() {
  for (int i = 0; i < NUM_BINS; i++) {
    my_heap.free_heads[i] = &my_heap.dummies[i];
    set_size_and_flag(&my_heap.dummies[i], 0, true);
    my_heap.dummies[i].next = NULL;
  }
}

void *my_malloc(size_t size) {
  int start_index = get_bin_index(size);
  my_metadata_t *metadata = NULL;

  // 最適なビンから順に探索
  for (int i = start_index; i < NUM_BINS; i++) {
    my_metadata_t *head = my_heap.free_heads[i];
    while (head) {
      if (is_free(head) && get_size(head) >= size) {
        metadata = head;
        goto block_found;
      }
      head = head->next;
    }
  }

  // どのビンにも空きがなかった場合
  {
    size_t buffer_size = 4096;
    my_metadata_t *new_chunk = (my_metadata_t *)mmap_from_system(buffer_size);
    set_size_and_flag(new_chunk, buffer_size - sizeof(my_metadata_t), false);
    
    // ヒープの終端を示すための番兵（sentinel）を配置
    my_metadata_t *sentinel = (my_metadata_t *)((char *)new_chunk + buffer_size - sizeof(my_metadata_t));
    set_size_and_flag(sentinel, 0, false);

    // 新しいチャンクを解放して、既存のフリーリスト管理と結合ロジックに任せる
    my_free(new_chunk + 1);
    return my_malloc(size); // 再度mallocを呼んで適切なブロックを取得
  }

block_found:
  // 見つけたブロックをフリーリストから削除
  remove_from_free_list(metadata);
  
  size_t block_size = get_size(metadata);
  size_t remaining_size = block_size - size;

  // ブロックの分割処理
  if (remaining_size > sizeof(my_metadata_t) + 8) { // 最小ブロックサイズ（メタデータ+8バイト）より大きい場合のみ分割
    set_size_and_flag(metadata, size, false); // 要求されたサイズに設定し、使用中にマーク
    
    my_metadata_t *new_metadata = (my_metadata_t *)((char *)(metadata + 1) + size);
    set_size_and_flag(new_metadata, remaining_size - sizeof(my_metadata_t), true);
    add_to_free_list(new_metadata); // 残りのブロックをフリーリストに追加
  } else {
    // 残りが小さい場合は分割せず、すべてを割り当てる
    set_size_and_flag(metadata, block_size, false);
  }

  return metadata + 1;
}

void my_free(void *ptr) {
  my_metadata_t *metadata = (my_metadata_t *)ptr - 1;
  set_size_and_flag(metadata, get_size(metadata), true); // まず空き状態にマーク

  // 右結合 (Forward Coalescing)
  my_metadata_t *next_block = (my_metadata_t *)((char *)ptr + get_size(metadata));
  if (is_free(next_block)) {
    // 次のブロックが空きなら、そのブロックをフリーリストから削除
    remove_from_free_list(next_block);
    
    // 現在のブロックと結合
    size_t new_size = get_size(metadata) + get_size(next_block) + sizeof(my_metadata_t);
    set_size_and_flag(metadata, new_size, true);
  }

  // 最終的な大きさのブロックをフリーリストに追加
  add_to_free_list(metadata);
}

void my_finalize() {
  // Nothing is here for now.
}

void test() {
  // Implement here!
  assert(1 == 1); /* 1 is 1. That's always true! (You can remove this.) */
}