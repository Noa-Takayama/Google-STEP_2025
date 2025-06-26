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

def nearest_neighbor_heuristic(cities):
    """
    最近傍法で初期解を生成する
    """
    num_cities = len(cities)
    unvisited = set(range(num_cities))
    route = []
    
    current_city = 0
    unvisited.remove(current_city)
    route.append(current_city)
    
    while unvisited:
        nearest_city = min(unvisited, key=lambda city: calculate_distance(cities[current_city], cities[city]))
        unvisited.remove(nearest_city)
        route.append(nearest_city)
        current_city = nearest_city
        
    return route

# どのくらい計算が進んでいるのかをターミナル上に表示. わからないと気が狂いそう
def local_search_2opt(route, cities):
    """
    2-opt法による局所探索。1秒ごとに進捗を表示する。
    """
    current_route = route[:]
    num_cities = len(current_route)
    improved = True
    last_update_time = time.time()

    while improved:
        improved = False
        for i in range(num_cities - 1):
            for j in range(i + 2, num_cities):
                # --- 1秒ごとの進捗表示ロジック ---
                current_time = time.time()
                if current_time - last_update_time > 1.0:
                    progress_msg = f"    -> 2-opt search in progress... (Checking node i={i}/{num_cities})"
                    sys.stdout.write(f"\r{progress_msg:<80}")
                    sys.stdout.flush()
                    last_update_time = current_time
                # --- 進捗表示ロジックここまで ---
                
                j_next = (j + 1) % num_cities
                original_dist = calculate_distance(cities[current_route[i]], cities[current_route[i+1]]) \
                              + calculate_distance(cities[current_route[j]], cities[current_route[j_next]])
                new_dist = calculate_distance(cities[current_route[i]], cities[current_route[j]]) \
                         + calculate_distance(cities[current_route[i+1]], cities[current_route[j_next]])

                if new_dist < original_dist:
                    current_route[i+1:j+1] = reversed(current_route[i+1:j+1])
                    improved = True
                    break
            if improved:
                break
    
    sys.stdout.write("\r    -> 2-opt search finished.                                          \n")
    sys.stdout.flush()
    return current_route

def double_bridge_kick(route):
    """
    Double Bridge操作による摂動(kick)。
    """
    kicked_route = route[:]
    num_cities = len(kicked_route)
    indices = sorted(random.sample(range(num_cities), 4))
    p1, p2, p3, p4 = indices
    seg1 = kicked_route[:p1]
    seg2 = kicked_route[p1:p2]
    seg3 = kicked_route[p2:p3]
    seg4 = kicked_route[p3:p4]
    seg5 = kicked_route[p4:]
    new_route = seg1 + seg4 + seg3 + seg2 + seg5
    return new_route

def iterated_local_search(cities, max_iterations=100, time_limit=60):
    """
    反復局所探索法(ILS)を実行する
    """
    num_cities = len(cities)
    start_time = time.time()
    
    # 1. 初期化 (最近傍法を使用)
    print("[Phase 1] Creating initial route with Nearest Neighbor Heuristic...")
    x_0 = nearest_neighbor_heuristic(cities)
    
    # 2-optで初期解をさらに改善
    print("[Phase 2] Performing initial local search (This may take a long time)...")
    x_best = local_search_2opt(x_0, cities) # ここで1秒ごとの進捗が表示される
    best_dist = calculate_total_distance(x_best, cities)
    print(f"Initial Best Distance: {best_dist:.2f}\n")

    # 2. 反復　ずっとコードを回し続けていて, 終わりが来なくて気が狂いそうだったので現状どこまで計算が進んでいるのかを教えてもらう
    print("[Phase 3] Starting Iterated Local Search main loop...")
    for i in range(max_iterations):
        print(f"--- ILS Iteration {i+1}/{max_iterations} ---")
        if time.time() - start_time > time_limit:
            print(f"Time limit of {time_limit} seconds reached.")
            break
            
        print("  - Perturbing solution (Double Bridge Kick)...")
        x_kicked = double_bridge_kick(x_best)
        
        print("  - Running local search on the new route...")
        x_new = local_search_2opt(x_kicked, cities) # ここでも1秒ごとの進捗が表示される
        new_dist = calculate_total_distance(x_new, cities)
        
        if new_dist < best_dist:
            x_best = x_new
            best_dist = new_dist
            print(f"  -> 🎉 New best solution found! Distance: {best_dist:.2f}\n") # おめでとう🥳
        else:
            print(f"  -> No improvement. Current best: {best_dist:.2f}\n") # 改善されないのなら現状の最高スコアを吐き出す

    print(f"ILS finished. Final Best Distance: {best_dist:.2f}")
    return x_best

# メイン関数
if __name__ == "__main__":
    if len(sys.argv) != 3: # コマンドライン引数が 3 つ未満だったら
        print("Usage: python solve_ils.py <input_file> <output_file>")
        sys.exit(1) # エラーが吐かれたら, 使い方の説明も書いておく
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    cities = read_cities(input_file)
    num_cities = len(cities)
    print(f"Solving TSP for {num_cities} cities from '{input_file}'...")
    
    if num_cities < 100:
        iterations = 5000 # もっと回せば、 N = 128あたりまでは多分理論値までいけるんじゃない？
        time_limit_sec = 300
    elif num_cities < 500:
        iterations = 10000
        time_limit_sec = 18000000
    else:
        iterations = 5000 # もっと回せばいいじゃん

        time_limit_sec = 3000000 # もっと長く回せばいいじゃん

    best_route = iterated_local_search(cities, max_iterations=iterations, time_limit=time_limit_sec)

    write_solution(output_file, best_route)
    print(f"Best route saved to '{output_file}'.")

    final_distance = calculate_total_distance(best_route, cities)
    print(f"Final validated distance: {final_distance}")