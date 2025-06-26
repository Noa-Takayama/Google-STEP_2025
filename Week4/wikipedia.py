# 課題 1, 2 のためのコード
import sys # 読み込みのために必要
import collections

class Wikipedia:

    # Initialize the graph of pages.
    def __init__(self, pages_file, links_file):

        # A mapping from a page ID (integer) to the page title.
        # For example, self.titles[1234] returns the title of the page whose
        # ID is 1234.
        self.titles = {}

        # A set of page links.
        # For example, self.links[1234] returns an array of page IDs linked
        # from the page whose ID is 1234.
        self.links = {}

        # Read the pages file into self.titles.
        with open(pages_file) as file:
            for line in file:
                (id, title) = line.rstrip().split(" ")
                id = int(id)
                assert not id in self.titles, id
                self.titles[id] = title
                self.links[id] = []
        print("Finished reading %s" % pages_file)

        # Read the links file into self.links.
        with open(links_file) as file:
            for line in file:
                (src, dst) = line.rstrip().split(" ")
                (src, dst) = (int(src), int(dst))
                assert src in self.titles, src
                assert dst in self.titles, dst
                self.links[src].append(dst)
        print("Finished reading %s" % links_file)
        print()


    # Example: Find the longest titles.
    def find_longest_titles(self):
        titles = sorted(self.titles.values(), key=len, reverse=True)
        print("The longest titles are:")
        count = 0
        index = 0
        while count < 15 and index < len(titles):
            if titles[index].find("_") == -1:
                print(titles[index])
                count += 1
            index += 1
        print()


    # Example: Find the most linked pages.
    def find_most_linked_pages(self):
        link_count = {}
        for id in self.titles.keys():
            link_count[id] = 0

        for id in self.titles.keys():
            for dst in self.links[id]:
                link_count[dst] += 1

        print("The most linked pages are:")
        link_count_max = max(link_count.values())
        for dst in link_count.keys():
            if link_count[dst] == link_count_max:
                print(self.titles[dst], link_count_max)
        print()


    # Homework #1: Find the shortest path.
    # 'start': A title of the start page.
    # 'goal': A title of the goal page.
    def find_shortest_path(self, start, goal):
        print(f"'{start}' から '{goal}' までの最短経路を探索します!:")

        # タイトルから ID を辿れるマップを作成する
        title_to_id = {title: id for id, title in self.titles.items()}

        # start と goal の ID をゲットする. 無い時にはエラーメッセージを出して終了する
        if start not in title_to_id or goal not in title_to_id:
            print("スタート, またはゴールのページが見つかりませんでした...orz")
            print()
            return
        
        start_id = title_to_id[start]
        goal_id = title_to_id[goal]

        # BFS のためのデータ構造を初期化する
        queue = collections.deque([start_id]) # 探索するページの ID を入れるキュー
        visited = {start_id}  # 訪問済みのページの ID を記録しておく. すでにスタートは訪問済み
        back_to_parents = {} # スタートに続きうる経路をゴールから辿るため, どこからきたのかを記録する

        # BFS の実装部分
        is_path_found = False # スタートからゴールまでの道が存在するかを判定する
        while queue:
            current_id = queue.popleft() # キューの先頭からページを取り出す
            
            # 現在いるページの ID がゴールの ID と一致すれば, 道が見つかったことになる！
            if current_id == goal_id:
                is_path_found = True
                break

            # 現在のページからリンクとして辿れるページを検索する
            for neighbor_id in self.links[current_id]:
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    back_to_parents[neighbor_id] = current_id # 親ページを記録
                    queue.append(neighbor_id) # キューにページを追加する

        # 経路の探索と出力部分
        if is_path_found:
            path = []
            current = goal_id
            while current != start_id: # スタートのページに戻るまで
                path.append(current)
                # back_to_parents にキーがあるか確認する
                if current not in back_to_parents:
                    print("経路の復元中にエラーが発生！")
                    return
                current = back_to_parents[current]
            path.append(start_id)
            path.reverse() # ゴールから辿っているから, 反転させてやる

            # ID のリストをタイトルのリストに変換して出力する部分
            path_titles = [self.titles[id] for id in path]
            print(" -> ".join(path_titles))
        else:
            print("残念！ 経路は見つかりませんでした")

        print()


    # Homework #2: Calculate the page ranks and print the most popular pages.
    def find_most_popular_pages(self):
        print("\nページランクの計算を開始します...")

        num_pages = len(self.titles)
        if num_pages == 0:
            print("ページがありません... orz")
            print()
            return

        # 1. パラメタの設定
        damping_factor = 0.85
        max_iterations = 100
        convergence_threshold_squared = 0.01 # ここはローカルにするのではなく, コマンドライン引数にできるともっとバリエーション豊富になる！！

        # 2. ページランクの初期化
        pagerank = {page_id: 1.0 for page_id in self.titles.keys()}

        # 3. ページランクの計算（反復）
        for i in range(max_iterations):
            print(f"反復計算 {i + 1} 回目...") # プログラムがどこまで反復しているか視覚化

            new_pagerank_from_links = {page_id: 0.0 for page_id in self.titles.keys()}
            dangling_sum = 0.0

            for page_id, rank in pagerank.items():
                outgoing_links = self.links[page_id]
                if not outgoing_links:
                    dangling_sum += rank
                else:
                    num_outgoing_links = len(outgoing_links)
                    contribution = rank / num_outgoing_links
                    for linked_id in outgoing_links:
                        new_pagerank_from_links[linked_id] += contribution
            
            change_squared = 0.0
            final_new_pagerank = {}

            for page_id in pagerank.keys():
                rank_from_links = new_pagerank_from_links[page_id]
                dangling_rank_share = dangling_sum / num_pages # 外に出してやると尚良い！
                new_rank = (1 - damping_factor) + damping_factor * (rank_from_links + dangling_rank_share)
                final_new_pagerank[page_id] = new_rank
                change_squared += (new_rank - pagerank[page_id]) ** 2

            pagerank = final_new_pagerank

            total_pagerank = sum(pagerank.values())
            print(f"  この反復後の合計ページランク: {total_pagerank:.4f} (目標値: {num_pages})") # 目標値と一致していることを確認
            print(f"  ランクの変化量 (二乗和): {change_squared:.4f}")

            if change_squared < convergence_threshold_squared:
                print(f"ランクが収束しました (変化量 < {convergence_threshold_squared}).")
                break
        else:
            print(f"最大反復回数 {max_iterations} に達しました !!")

        sorted_pages = sorted(pagerank.items(), key=lambda item: item[1], reverse=True)

        print("\n最も人気のページトップ 10 は...:")
        for i in range(min(10, len(sorted_pages))):
            page_id, rank = sorted_pages[i]
            print(f"{i+1:2d}. {self.titles[page_id]:<20} (Rank: {rank:.4f})")
        
        print()

    # Homework #3 (optional):
    # Search the longest path with heuristics.
    # 'start': A title of the start page.
    # 'goal': A title of the goal page.
    def find_longest_path(self, start, goal):
        print(f"'{start}' から '{goal}' までの（重複なし）最長経路を探索します...")

        # 0. タイトルからIDへの変換と存在チェック
        title_to_id = {title: id for id, title in self.titles.items()}
        if start not in title_to_id or goal not in title_to_id:
            print("スタートまたはゴールのページが見つかりませんでした。")
            print()
            return

        start_id = title_to_id[start]
        goal_id = title_to_id[goal]

        # ----------------------------------------------------------------
        # 1. ヒューリスティックの計算：ご提案の通り、ゴールからの距離を計算します
        # ----------------------------------------------------------------
        print("ヒューリスティック（ゴールからの距離）の計算を開始します...")
        # 逆引きリンク（dst -> src）を作成
        reversed_links = {id: [] for id in self.titles}
        for src_id, dst_ids in self.links.items():
            for dst_id in dst_ids:
                reversed_links[dst_id].append(src_id)

        # ゴールからBFSで各ノードへの最短距離を計算
        distances_from_goal = {goal_id: 0}
        queue = collections.deque([goal_id])
        
        while queue:
            current_id = queue.popleft()
            # 逆引きリンクを辿って、ゴールに到達できるページを探索
            for neighbor_id in reversed_links[current_id]:
                if neighbor_id not in distances_from_goal:
                    distances_from_goal[neighbor_id] = distances_from_goal[current_id] + 1
                    queue.append(neighbor_id)
        
        print("ヒューリスティックの計算が完了しました。")

        # ----------------------------------------------------------------
        # 2. バックトラッキングを用いた深さ優先探索（DFS）で最長経路を探索
        # ----------------------------------------------------------------
        # クラスの属性として最長経路を保存することで、再帰関数内で更新しやすくします
        self.longest_path_found = []

        # path は現在たどっている経路（IDのリスト）
        def dfs(current_path):
            current_id = current_path[-1]

            # 次の探索候補となる隣接ページをリストアップ
            neighbors_to_visit = []
            for neighbor_id in self.links[current_id]:
                # ゴールに到達した場合
                if neighbor_id == goal_id:
                    final_path = current_path + [goal_id]
                    # 現在見つかっている最長経路より長ければ更新
                    if len(final_path) > len(self.longest_path_found):
                        self.longest_path_found = final_path
                        # 途中経過を表示
                        print(f"新しい最長経路を発見 (長さ: {len(self.longest_path_found)})")
                    # ゴールに到達したので、この先は探索しない
                    continue

                # まだ訪問しておらず（重複がなく）、ゴールでもないページを候補に追加
                if neighbor_id not in current_path:
                    neighbors_to_visit.append(neighbor_id)

            # ヒューリスティックに基づいて隣接ページをソート
            # ゴールから遠い（distanceが大きい）ページを優先的に探索する
            # ゴールから到達不能なページは距離が計算できないため、優先度を最低(-1)にする
            neighbors_to_visit.sort(key=lambda nid: distances_from_goal.get(nid, -1), reverse=True)

            # 優先順位の高い（ゴールから遠い）ページから順に再帰的に探索
            for neighbor_id in neighbors_to_visit:
                dfs(current_path + [neighbor_id])

        # 探索開始
        print("最長経路の探索を開始します...(時間がかかる場合があります)")
        dfs([start_id])

        # ----------------------------------------------------------------
        # 3. 結果の出力
        # ----------------------------------------------------------------
        if not self.longest_path_found:
            print("残念ながら、経路は見つかりませんでした。")
        else:
            print("\n探索完了！見つかった最長経路は以下の通りです:")
            path_titles = [self.titles[id] for id in self.longest_path_found]
            print(" -> ".join(path_titles))
            print(f"経路の長さ: {len(self.longest_path_found)} ページ")
            
            # 念のため、パスが正しいかチェック
            self.assert_path(self.longest_path_found, start, goal)
            print("パスの正当性を確認しました。")
        
        print()

    def assert_path(self, path, start, goal):
        assert(start != goal)
        assert(len(path) >= 2)
        assert(self.titles[path[0]] == start)
        assert(self.titles[path[-1]] == goal)
        for i in range(len(path) - 1):
            assert(path[i + 1] in self.links[path[i]])


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: %s pages_file links_file" % sys.argv[0])
        exit(1)

    wikipedia = Wikipedia(sys.argv[1], sys.argv[2])
    # Example
    wikipedia.find_longest_titles()
    # Example
    wikipedia.find_most_linked_pages()
    # Homework #1
    wikipedia.find_shortest_path("渋谷", "小野妹子")
    wikipedia.find_shortest_path("渋谷", "パレートの法則")
    # Homework #2
    wikipedia.find_most_popular_pages()
    # Homework #3 (optional)
    wikipedia.find_longest_path("渋谷", "池袋")