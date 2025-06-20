# 課題1, 2 実装説明

## 課題1: 最短経路探索(`find_shortest_path`)

### アルゴリズム

この問題は, グラフにおけるノード間の最短経路を見つける問題であるため, **幅優先探索　(BFS: Breadth-First Search)** を使った.

### 実装の要点

1. **データ構造の初期化**
   
   以下の3つのデータ構造を使用した.
   * `queue` (`collections.deque`): 次に訪問すべきページIDを格納するキュー. FIFOの性質から, スタートに近いページから順に処理可能.

   * `visited` (`set`): すでに訪問した(=キューに追加)したページIDを記録する集合.

   * `back_to_parents` (`dict`): 経路を復元するための辞書. キーに「子ページID」, 値に「親ページID」を格納する.
   これにより, ゴールからスタートまで辿ることができる

   ```python
   # BFS のためのデータ構造の初期化
   queue = collections.deque([start.id])
   visited = {start.id}
   back_to_parents = {}

2.  **探索プロセス**
    
    キューが空になるまで、以下の処理を繰り返す.
    * キューからページを取り出す.

    * そのページがゴールであれば、探索を終了する.

    * そうでなければ、そのページからリンクされている全ての未訪問ページを `visited` に追加し、キューの末尾に追加. 同時に、`back_to_parents`に親子関係を記録する.

    ```python
    # 現在のページからリンクとして辿れるページを検索する
    for neighbor_id in self.links[current_id]:
        if neighbor_id not in visited:
            visited.add(neighbor_id)
            back_to_parents[neighbor_id] = current_id # 親ページを記録
            queue.append(neighbor_id) # キューにページを追加する
    ```

3.  **経路の復元**
    探索が成功した場合, `back_to_parents` 辞書をゴールからスタートに向かって遡ることで経路を復元する. 復元されたパスは逆順になっているため、最後に反転させて正しい順序の経路リストを生成する.

---


   