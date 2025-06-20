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

## 課題2: ページランク計算 (`find_most_popular_pages`)

### アルゴリズム

グラフ内のページについて, ページランクを計算し, その上位10ページを出力するアルゴリズムを実装した. 

「多くのページからリンクされているページは重要」「各ページは自身のランクを, リンク先のページにルールに基づいて分配する」という法則に従い, この分配と更新のプロセスが収束するまで繰り返す.

### 実装の要点

1.  **初期化**
    計算開始時、全てのページに均等なランクを割り当てます。今回はシンプルに `1.0` を初期値としました。これにより、ページランクの合計値は常にページ総数と一致し、計算過程での検証が容易になります。

    ```python
    # 2. ページランクの初期化
    pagerank = {page_id: 1.0 for page_id in self.titles.keys()}
    ```

2.  **ランクの反復計算**
    ループ処理の中で、現在のランク値に基づいて新しいランク値を計算する.
    * **ランクの分配**: 各ページは、自身の持つランク(`rank`)を外部リンク数(`num_outgoing_links`)で割り,各リンク先ページに均等に分配(`contribution`)する.

        ```python
        contribution = rank / num_outgoing_links
        for linked_id in outgoing_links:
            new_pagerank_from_links[linked_id] += contribution
        ```

    * **Dangling Nodeの処理**: 外部リンクを一つも持たないページ（Dangling Node）は, ランクをどこにも分配できない. これを防ぐため, Dangling Nodeが持つランクは一旦 `dangling_sum` に集計し, 次のステップで全ページに均等に再分配する.

    * **更新式**: 新しいページランクは, ダンピングファクター `d` (今回は0.85) を用いて以下の式で計算する.
        `new_rank = (1 - d) + d * (リンク経由で得たランク + Dangling Nodeから再分配されたランク)`
        `(1 - d)` の部分は, どのページからでも一定確率で遷移してくる「ランダムジャンプ」を表し, どのページも最低限のランクを持つことを保証してくれる.

3.  **収束判定**
    計算を無限に続けないため, ランク値の変化が十分に小さくなった時点で計算を打ち切る. 今回は「前回と今回のランク値の差の二乗和」を計算し, その値が予め定めた閾値 (`0.01`) を下回った場合に「収束した」と判断した.

    ```python
    # ランクの変化量 (二乗和)を計算
    change_squared += (new_rank - pagerank[page_id]) ** 2
    
    # ...
    
    # 収束条件をチェック
    if change_squared < convergence_threshold_squared:
        print(f"ランクが収束しました...")
        break
    ```