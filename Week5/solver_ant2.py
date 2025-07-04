import csv
import math
import random
import sys
import time

def read_cities(file_path):
    """
    CSVファイルから都市の座標を読み込む関数
    """
    cities = []
    with open(file_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # ヘッダー行をスキップ
        for row in reader:
            cities.append((float(row[0]), float(row[1])))
    return cities

def write_solution(file_path, route):
    """
    解（経路）をCSVファイルに書き込む関数
    """
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['index'])
        for city_index in route:
            writer.writerow([city_index])

class TSPSolver:
    """
    反復局所探索法と焼きなまし法を組み合わせたTSPソルバー
    """
    def __init__(self, cities, time_limit_sec=60, initial_temp=10.0, cooling_rate=0.9995):
        self.cities = cities
        self.num_cities = len(cities)
        self.time_limit_sec = time_limit_sec
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.distance_matrix = self._create_distance_matrix()
        self.start_time = None

    def _create_distance_matrix(self):
        """
        都市間の距離行列を事前に計算する
        """
        print("  - Calculating distance matrix...")
        matrix = [[0.0] * self.num_cities for _ in range(self.num_cities)]
        for i in range(self.num_cities):
            for j in range(i, self.num_cities):
                dist = math.hypot(self.cities[i][0] - self.cities[j][0], 
                                  self.cities[i][1] - self.cities[j][1])
                matrix[i][j] = matrix[j][i] = dist
        print("  - Distance matrix created.")
        return matrix

    def _calculate_total_distance(self, route):
        """
        距離行列を使って経路の総距離を計算する
        """
        total_dist = 0
        for i in range(self.num_cities):
            from_city = route[i]
            to_city = route[(i + 1) % self.num_cities]
            total_dist += self.distance_matrix[from_city][to_city]
        return total_dist

    def _nearest_neighbor_heuristic(self):
        """
        最近傍法で初期解を生成する
        """
        unvisited = set(range(self.num_cities))
        current_city = random.choice(list(unvisited)) # ランダムな都市から開始
        unvisited.remove(current_city)
        route = [current_city]
        
        while unvisited:
            nearest_city = min(unvisited, key=lambda city: self.distance_matrix[current_city][city])
            unvisited.remove(nearest_city)
            route.append(nearest_city)
            current_city = nearest_city
        return route

    def _local_search_2opt(self, route):
        """
        2-opt法による局所探索。高速化のため、距離の差分計算を用いる。
        """
        current_route = route[:]
        improved = True
        while improved:
            improved = False
            for i in range(self.num_cities - 1):
                for j in range(i + 2, self.num_cities):
                    # 時間制限チェック
                    if time.time() - self.start_time > self.time_limit_sec:
                        return current_route

                    # 辺 (i, i+1) と (j, j_next) を (i, j) と (i+1, j_next) に組み替える
                    i_next = (i + 1) % self.num_cities
                    j_next = (j + 1) % self.num_cities
                    
                    # 現在の辺の長さを取得
                    c1 = current_route[i]
                    c2 = current_route[i_next]
                    c3 = current_route[j]
                    c4 = current_route[j_next]

                    original_dist = self.distance_matrix[c1][c2] + self.distance_matrix[c3][c4]
                    new_dist = self.distance_matrix[c1][c3] + self.distance_matrix[c2][c4]

                    if new_dist < original_dist:
                        current_route[i_next:j+1] = reversed(current_route[i_next:j+1])
                        improved = True
                        break # 内側のループを抜けて、再度最初から探索
                if improved:
                    break # 外側のループを抜けて、再度最初から探索
        return current_route

    def _double_bridge_kick(self, route):
        """
        Double Bridge操作による摂動(kick)。経路を4つに分割し、入れ替える。
        """
        kicked_route = route[:]
        indices = sorted(random.sample(range(1, self.num_cities), 4))
        p1, p2, p3, p4 = indices
        
        # 4-opt (Double Bridge)
        new_route = kicked_route[:p1] + kicked_route[p3:p4] + \
                    kicked_route[p2:p3] + kicked_route[p1:p2] + \
                    kicked_route[p4:]
        return new_route

    def solve(self):
        """
        ILSとSAを組み合わせてTSPを解くメインの実行関数
        """
        self.start_time = time.time()
        
        # 1. 初期化
        print("[Phase 1] Creating initial solution...")
        # 最近傍法で初期解を生成
        initial_route = self._nearest_neighbor_heuristic()
        
        # 2-optで初期解をさらに改善
        print("[Phase 2] Performing initial local search...")
        current_route = self._local_search_2opt(initial_route)
        current_dist = self._calculate_total_distance(current_route)
        
        best_route = current_route[:]
        best_dist = current_dist
        
        print(f"Initial Best Distance: {best_dist:.2f}\n")

        # 2. 反復局所探索
        print("[Phase 3] Starting Iterated Local Search with Simulated Annealing...")
        iteration = 0
        temperature = self.initial_temp
        
        while time.time() - self.start_time < self.time_limit_sec:
            iteration += 1
            
            # 摂動 (Perturbation)
            kicked_route = self._double_bridge_kick(current_route)
            
            # 局所探索 (Local Search)
            new_route = self._local_search_2opt(kicked_route)
            new_dist = self._calculate_total_distance(new_route)
            
            # 受容判定 (Acceptance Criterion) - 焼きなまし法
            delta = new_dist - current_dist
            
            if delta < 0: # 改善された場合
                current_route = new_route[:]
                current_dist = new_dist
                if new_dist < best_dist:
                    best_route = new_route[:]
                    best_dist = new_dist
                    print(f"  Iter {iteration:>4}: Found new best! Dist: {best_dist:<12.2f} (Temp: {temperature:.2e}) 🎉")
            elif random.random() < math.exp(-delta / temperature): # 悪化したが、確率で受容
                current_route = new_route[:]
                current_dist = new_dist
                print(f"  Iter {iteration:>4}: Accepted worse.  Dist: {current_dist:<12.2f} (Temp: {temperature:.2e})")
            else:
                # No improvement
                if iteration % 20 == 0: # 定期的に進捗を表示
                     print(f"  Iter {iteration:>4}: No improvement.  Best: {best_dist:<12.2f} (Temp: {temperature:.2e})")


            # 温度を更新
            temperature *= self.cooling_rate

        elapsed_time = time.time() - self.start_time
        print(f"\nILS finished in {elapsed_time:.2f} seconds.")
        print(f"Final Best Distance: {best_dist:.2f}")
        return best_route

# メイン関数
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python solve_ils_pro.py <input_file> <output_file>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    cities_data = read_cities(input_file)
    num_cities = len(cities_data)
    print(f"Solving TSP for {num_cities} cities from '{input_file}'...")
    
    # 問題の規模に応じて実行時間を設定
    if num_cities < 100:
        time_limit = 30  # 30秒
    elif num_cities < 500:
        time_limit = 180 # 3分
    else:
        time_limit = 60000 # 10000分

    print(f"Setting time limit to {time_limit} seconds.\n")

    # ソルバーをインスタンス化して実行
    solver = TSPSolver(cities_data, time_limit_sec=time_limit)
    best_route = solver.solve()

    # 結果をファイルに書き込み
    write_solution(output_file, best_route)
    print(f"\nBest route saved to '{output_file}'.")

    # 最終的な距離を検証
    final_distance = solver._calculate_total_distance(best_route)
    print(f"Final validated distance: {final_distance:.4f}")
