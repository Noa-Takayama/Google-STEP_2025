//
// >>>> malloc challenge! <<<<
//
// 安定版: Best-fit アロケータ（単一フリーリスト、完全な左右結合機能付き）
//

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
// 新しいブロックを作るには、ヘッダ、フッタ、最小ペイロードが必要
#define MIN_BLOCK_SIZE (2 * sizeof(my_metadata_t) + MIN_BLOCK_PAYLOAD)

// メモリブロックの情報を管理する構造体（ヘッダとして使用）
typedef struct my_metadata_t {
  size_t size; // LSB(最下位ビット)は「空きブロックか否か」のフラグとして使用
  struct my_metadata_t *next; // 空きブロックリスト（フリーリスト）を繋ぐためのポインタ
} my_metadata_t;


// フリーリストの先頭を指すポインタ。ここから空きブロックを辿る。
static my_metadata_t *free_list_head = NULL;


// 関数プロトタイプ宣言

void my_free(void *ptr);
static my_metadata_t *coalesce(my_metadata_t *header);


// sizeフィールドからフラグビットを無視して、純粋なペイロードサイズを取得する
static inline size_t get_size(my_metadata_t *m) { return m->size & ~1UL; }

// sizeフィールドのフラグビットをチェックして、ブロックが空き状態か判定する
static inline bool is_free(my_metadata_t *m) { return m->size & 1UL; }

// ブロックのヘッダとフッタに、サイズと状態（空き/使用中）を書き込む
static inline void set_size_and_flag(my_metadata_t *hdr, size_t payload_size, bool free_flag) {
  // ヘッダに情報を書き込む
  hdr->size = payload_size | (free_flag ? 1UL : 0UL);
  // フッタはペイロードの終端の直前にある。同じ情報を書き込む。
  my_metadata_t *ftr = (my_metadata_t *)((char *)(hdr + 1) + payload_size) - 1;
  ftr->size = hdr->size;
}

// あるブロックのヘッダから、物理的に次のブロックのヘッダのアドレスを計算する
static inline my_metadata_t* get_next_header(my_metadata_t* hdr) {
  return (my_metadata_t*)((char*)(hdr + 1) + get_size(hdr));
}

// あるブロックのヘッダから、物理的に前のブロックのフッタのアドレスを計算する
static inline my_metadata_t* get_prev_footer(my_metadata_t* hdr) {
  return (my_metadata_t*)hdr - 1;
}

// あるブロックのフッタから、そのブロックのヘッダのアドレスを計算する（左結合に必須）
static inline my_metadata_t* get_header_from_footer(my_metadata_t* ftr) {
  return (my_metadata_t *)((char *)ftr - get_size(ftr)) - 1;
}


// フリーリスト操作

// 指定されたブロックをフリーリストの先頭に追加する
static void add_to_list(my_metadata_t *blk) {
  blk->next = free_list_head;
  free_list_head = blk;
}

// 指定されたブロックをフリーリストから削除する
static void remove_from_list(my_metadata_t *blk) {
  my_metadata_t **p = &free_list_head;
  while (*p && *p != blk) {
    p = &(*p)->next;
  }
  if (*p) {
    *p = blk->next;
  }
}


// アロケータのコアロジック

// チャレンジ開始時に一度だけ呼ばれる初期化関数
void my_initialize() {
  // OSから最初のヒープ領域を確保する
  void* heap = mmap_from_system(CHUNK_SIZE);
  
  // プロローグ(Prologue): ヒープの開始地点に配置する番兵ブロック。
  my_metadata_t* prologue = (my_metadata_t*)heap;
  set_size_and_flag(prologue, 0, false); // サイズ0、使用中としてマーク

  // エピローグ(Epilogue): ヒープの終端に配置する番兵ブロック。
  my_metadata_t* epilogue = (my_metadata_t*)((char*)heap + CHUNK_SIZE - 2*sizeof(my_metadata_t));
  set_size_and_flag(epilogue, 0, false); // サイズ0、使用中としてマーク
  
  // プロローグとエピローグの間が、最初の巨大な空きブロックとなる
  free_list_head = (my_metadata_t*)((char*)prologue + 2*sizeof(my_metadata_t));
  size_t initial_payload = CHUNK_SIZE - 4*sizeof(my_metadata_t);
  set_size_and_flag(free_list_head, initial_payload, true);
  free_list_head->next = NULL;
}

// メモリ割り当て関数
void *my_malloc(size_t size) {
  if (size == 0) return NULL;
  // 要求サイズを8の倍数に切り上げる
  size_t required_payload = (size + 7) & ~7UL;

  my_metadata_t *current = free_list_head;
  my_metadata_t *best_fit = NULL;
  
  // Best-fit探索: 要求サイズを満たす空きブロックの中で、最もサイズの小さいものを探す
  while (current) {
    if (get_size(current) >= required_payload) {
      if (best_fit == NULL || get_size(current) < get_size(best_fit)) {
        best_fit = current;
      }
    }
    current = current->next;
  }

  // このシンプルな実装ではヒープを拡張しない。空きがなければNULLを返す。
  if (best_fit == NULL) {
    return NULL;
  }

  // 見つけた最適なブロックをフリーリストから削除
  remove_from_list(best_fit);
  size_t block_size = get_size(best_fit);
  size_t remaining = block_size - required_payload;

  // もし残りの領域が新しいブロックを作れるほど大きいなら、ブロックを分割する
  if (remaining >= MIN_BLOCK_SIZE) {
    // best_fitブロックを要求サイズに縮小し、「使用中」としてマーク
    set_size_and_flag(best_fit, required_payload, false);
    // 残りの領域を新しい空きブロックとして設定
    my_metadata_t *split = get_next_header(best_fit);
    set_size_and_flag(split, remaining - 2 * sizeof(my_metadata_t), true);
    // 分割してできた新しい空きブロックをmy_freeに渡す（これにより自動で結合処理も行われる）
    my_free(split + 1);
  } else {
    // 残りが小さい場合は分割せず、ブロック全体を割り当てる
    set_size_and_flag(best_fit, block_size, false);
  }
  
  // ユーザーに返すのは、ヘッダの直後にあるペイロード領域の先頭アドレス
  return (void *)(best_fit + 1);
}

// メモリ解放関数
void my_free(void *ptr) {
  if (ptr == NULL) return;
  // ユーザーから渡されたポインタから、ヘッダのアドレスを取得
  my_metadata_t *header = (my_metadata_t *)ptr - 1;
  // 左右のブロックと結合し、最終的な大きさのブロックをフリーリストに戻す
  my_metadata_t *coalesced_block = coalesce(header);
  add_to_list(coalesced_block);
}

// 左右の空きブロックを結合する関数
static my_metadata_t *coalesce(my_metadata_t *header) {
  my_metadata_t *next_header = get_next_header(header);
  my_metadata_t *prev_footer = get_prev_footer(header);
  
  // 前後のブロックが空き状態かチェック
  bool prev_is_free = is_free(prev_footer);
  bool next_is_free = is_free(next_header);
  size_t size = get_size(header);

  // 4つのケースに応じて結合処理を行う
  if (prev_is_free && next_is_free) { // ケース4: 前後とも空き
    my_metadata_t *prev_header = get_header_from_footer(prev_footer);
    remove_from_list(prev_header);
    remove_from_list(next_header);
    size += get_size(prev_header) + get_size(next_header) + 2 * sizeof(my_metadata_t);
    header = prev_header;
  } else if (prev_is_free) { // ケース3: 前のみ空き
    my_metadata_t *prev_header = get_header_from_footer(prev_footer);
    remove_from_list(prev_header);
    size += get_size(prev_header) + 2 * sizeof(my_metadata_t);
    header = prev_header;
  } else if (next_is_free) { // ケース2: 後のみ空き
    remove_from_list(next_header);
    size += get_size(next_header) + 2 * sizeof(my_metadata_t);
  }
  // ケース1 (前後とも使用中) の場合は、何もしない
  
  // 最終的な大きさでヘッダとフッタを更新
  set_size_and_flag(header, size, true);
  return header;
}

// チャレンジ終了時に呼ばれる
void my_finalize() {}

// main.cから呼び出されるため、定義が必要
void test() {}
