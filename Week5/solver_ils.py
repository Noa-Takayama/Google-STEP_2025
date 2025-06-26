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

def local_search_2opt(route, cities):
    """
    2-opt法による局所探索。改善がなくなるまで繰り返す。
    """
    current_route = route[:]
    num_cities = len(current_route)
    improved = True
    while improved:
        improved = False
        for i in range(num_cities - 1):
            for j in range(i + 2, num_cities):
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
    return current_route

def double_bridge_kick(route):
    """
    Double Bridge操作による摂動(kick)。
    経路を4つのセグメントに分割し、並べ替える。
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
    
    # 1. 初期化
    x_0 = list(range(num_cities))
    random.shuffle(x_0)
    
    x_best = local_search_2opt(x_0, cities)
    best_dist = calculate_total_distance(x_best, cities)
    print(f"Initial Best Distance: {best_dist:.2f}")

    # 2. 反復
    for i in range(max_iterations):
        if time.time() - start_time > time_limit:
            print(f"\nTime limit of {time_limit} seconds reached.")
            break
            
        x_kicked = double_bridge_kick(x_best)
        x_new = local_search_2opt(x_kicked, cities)
        new_dist = calculate_total_distance(x_new, cities)
        
        if new_dist < best_dist:
            x_best = x_new
            best_dist = new_dist
            print(f"Iteration {i+1}: New best solution found! Distance: {best_dist:.2f}")
        else:
            if (i + 1) % 10 == 0:
                print(f"Iteration {i+1}: No improvement. Current best: {best_dist:.2f}")

    print(f"\nILS finished. Final Best Distance: {best_dist:.2f}")
    return x_best

# メイン関数
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python solve_ils.py <input_file> <output_file>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    cities = read_cities(input_file)
    num_cities = len(cities)
    print(f"Solving TSP for {num_cities} cities from '{input_file}'...")
    
    # 都市数に応じたパラメータ設定
    if num_cities < 100:
        iterations = 200
        time_limit_sec = 30
    elif num_cities < 500:
        iterations = 100
        time_limit_sec = 180 # 3分
    else:
        iterations = 50
        time_limit_sec = 600 # 10分

    best_route = iterated_local_search(cities, max_iterations=iterations, time_limit=time_limit_sec)

    write_solution(output_file, best_route)
    print(f"Best route saved to '{output_file}'.")

    final_distance = calculate_total_distance(best_route, cities)
    print(f"Final validated distance: {final_distance}")