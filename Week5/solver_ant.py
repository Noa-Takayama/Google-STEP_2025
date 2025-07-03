# 蟻コロニー最適化(ACO)を用いてTSP（巡回セールスマン問題）を解く

import csv
import math
import random
import sys
import time
import threading

def read_cities(file_path):
    """
    CSVファイルから都市の座標を読み込む関数
    """
    cities = []
    with open(file_path, 'r', newline='') as f:
        reader = csv.reader(f)
        next(reader)  # ヘッダー行をスキップ
        for row in reader:
            cities.append((float(row[0]), float(row[1])))
    return cities

def write_solution(file_path, route):
    """
    解（経路）をCSVファイルに書き込む関数
    """
    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['index'])
        for city_index in route:
            writer.writerow([city_index])

def calculate_distance(city1, city2):
    """
    2都市間のユークリッド距離を計算する
    """
    return math.hypot(city1[0] - city2[0], city1[1] - city2[1])

def calculate_total_distance(route, cities):
    """
    経路全体の総距離を計算する
    """
    total_dist = 0
    num_cities = len(route)
    for i in range(num_cities):
        from_city = cities[route[i]]
        to_city = cities[route[(i + 1) % num_cities]]
        total_dist += calculate_distance(from_city, to_city)
    return total_dist

class AntColonyOptimizer:
    """
    アリコロニー最適化(ACO)でTSPを解くクラス
    """
    def __init__(self, cities, n_ants, n_iterations, alpha, beta, evaporation_rate, pheromone_deposit_weight=1.0):
        self.cities = cities
        self.n_cities = len(cities)
        self.n_ants = n_ants
        self.n_iterations = n_iterations
        self.alpha = alpha  # フェロモンの影響度
        self.beta = beta    # ヒューリスティック情報（距離）の影響度
        self.evaporation_rate = evaporation_rate # フェロモンの蒸発率
        self.pheromone_deposit_weight = pheromone_deposit_weight # フェロモンの堆積量

        # 距離行列とフェロモン行列を初期化
        self.distances = self._calculate_all_distances()
        # フェロモンは微小な初期値で初期化
        self.pheromones = [[1.0 / (self.n_cities * self.n_cities) for _ in range(self.n_cities)] for _ in range(self.n_cities)]
        
        self.best_route = None
        self.best_distance = float('inf')
        self.stop_event = threading.Event()

    def _calculate_all_distances(self):
        """
        全都市間の距離行列を事前に計算しておく
        """
        distances = [[0.0] * self.n_cities for _ in range(self.n_cities)]
        for i in range(self.n_cities):
            for j in range(i, self.n_cities):
                dist = calculate_distance(self.cities[i], self.cities[j])
                distances[i][j] = distances[j][i] = dist
        return distances

    def run(self):
        """
        ACOアルゴリズムのメインループを実行する
        """
        print("[Phase 1] Starting Ant Colony Optimization...")
        start_time = time.time()

        for i in range(self.n_iterations):
            if self.stop_event.is_set():
                print("\nOptimization stopped by user.")
                break

            ant_routes = []
            for _ in range(self.n_ants):
                ant_routes.append(self._construct_solution())

            self._update_pheromones(ant_routes)

            # 現在の世代での最良解を見つける
            current_best_ant_distance = float('inf')
            current_best_ant_route = None
            for route in ant_routes:
                dist = calculate_total_distance(route, self.cities)
                if dist < current_best_ant_distance:
                    current_best_ant_distance = dist
                    current_best_ant_route = route
            
            # 全体での最良解を更新
            if current_best_ant_distance < self.best_distance:
                self.best_distance = current_best_ant_distance
                self.best_route = current_best_ant_route
                print(f"\rIteration {i+1}/{self.n_iterations} | 🎉 New Best Distance: {self.best_distance:.2f}{' '*20}")
            else:
                progress_msg = f"Iteration {i+1}/{self.n_iterations} | Current Best: {self.best_distance:.2f}"
                sys.stdout.write(f"\r{progress_msg:<80}")
                sys.stdout.flush()
        
        elapsed_time = time.time() - start_time
        print(f"\n[Phase 2] ACO finished in {elapsed_time:.2f} seconds.")
        print(f"Final Best Distance: {self.best_distance:.2f}")
        return self.best_route

    def _construct_solution(self):
        """
        一匹のアリが解（経路）を構築する
        """
        route = []
        unvisited = set(range(self.n_cities))
        
        # ランダムな都市からスタート
        start_city = random.choice(list(unvisited))
        route.append(start_city)
        unvisited.remove(start_city)
        
        current_city = start_city
        while unvisited:
            next_city = self._select_next_city(current_city, unvisited)
            route.append(next_city)
            unvisited.remove(next_city)
            current_city = next_city
            
        return route

    def _select_next_city(self, current_city, unvisited):
        """
        確率的に次の都市を選択する
        """
        probabilities = []
        total_prob = 0.0

        for city in unvisited:
            # 距離が0の場合は微小な値を設定して0で割ることを防ぐ
            distance = self.distances[current_city][city]
            if distance == 0:
                heuristic_info = 1.0 / 1e-9
            else:
                heuristic_info = 1.0 / distance
            
            pheromone = self.pheromones[current_city][city]
            
            # フェロモンとヒューリスティック情報を組み合わせて確率を計算
            prob = (pheromone ** self.alpha) * (heuristic_info ** self.beta)
            probabilities.append((city, prob))
            total_prob += prob

        # 確率が0の場合はランダムに選ぶ
        r = random.uniform(0, total_prob)
        upto = 0.0
        for city, prob in probabilities:
            if upto + prob >= r:
                return city
            upto += prob
        
        # 万が一のためのフォールバック　
        # フォールバックとは、確率計算で何らかの理由で選択できなかった場合に備えるもの
        return probabilities[-1][0]


    def _update_pheromones(self, ant_routes):
        """
        フェロモンを更新する（蒸発と堆積）
        """
        # 1. 蒸発
        for i in range(self.n_cities):
            for j in range(self.n_cities):
                self.pheromones[i][j] *= (1.0 - self.evaporation_rate)

        # 2. 堆積
        # 各アリの経路に対してフェロモンを貯める
        for route in ant_routes:
            route_distance = calculate_total_distance(route, self.cities)
            pheromone_to_add = self.pheromone_deposit_weight / route_distance
            
            for i in range(self.n_cities):
                from_city = route[i]
                to_city = route[(i + 1) % self.n_cities]
                self.pheromones[from_city][to_city] += pheromone_to_add
                self.pheromones[to_city][from_city] += pheromone_to_add

# 使い方のエラー処理も含めて、メイン関数を定義
def main():
    if len(sys.argv) != 3:
        print("Usage: python solve_aco.py <input_file> <output_file>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    cities = read_cities(input_file)
    num_cities = len(cities)
    print(f"Solving TSP for {num_cities} cities from '{input_file}' using ACO...")

    # 各種パラメータの設定
    if num_cities < 100:
        n_ants = 20
        n_iterations = 100
    elif num_cities < 500:
        n_ants = 300
        n_iterations = 1000
    else:
        n_ants = 50       # アリの数
        n_iterations = 500  # 世代数（イテレーション）
    
    alpha = 1.0               # フェロモンの影響度
    beta = 5.0                # 距離の影響度
    evaporation_rate = 0.5    # フェロモン蒸発率

    # 適宜いじる

    aco = AntColonyOptimizer(
        cities,
        n_ants=n_ants,
        n_iterations=n_iterations,
        alpha=alpha,
        beta=beta,
        evaporation_rate=evaporation_rate
    )
    
    try:
        best_route = aco.run()
        if best_route:
            write_solution(output_file, best_route)
            print(f"Best route saved to '{output_file}'.")
            final_distance = calculate_total_distance(best_route, cities)
            print(f"Final validated distance: {final_distance}")
        else:
            print("No solution was found.")

    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Saving the best route found so far...")
        aco.stop_event.set()
        if aco.best_route:
            write_solution(output_file, aco.best_route)
            print(f"Best route found so far saved to '{output_file}'.")
            final_distance = calculate_total_distance(aco.best_route, cities)
            print(f"Distance: {final_distance}")
        else:
            print("No solution found to save.")

if __name__ == "__main__":
    main()
