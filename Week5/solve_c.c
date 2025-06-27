#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <stdbool.h>
#include <limits.h>
#include <sys/time.h>

// 都市の座標を表す構造体
typedef struct {
    double x;
    double y;
} City;

// グローバル変数
City* cities = NULL;
int num_cities = 0;

// 関数プロトタイプ
void read_cities(const char* file_path);
void write_solution(const char* file_path, const int* route);
double calculate_distance(int city1_idx, int city2_idx);
double calculate_total_distance(const int* route);
int* nearest_neighbor_heuristic();
void local_search_2opt(int* route);
void double_bridge_kick(int* route);
int* iterated_local_search(int max_iterations, int time_limit_sec);

/**
 * @brief CSVファイルから都市の座標を読み込み、グローバル変数に格納する
 * @param file_path 入力CSVファイルのパス
 */
void read_cities(const char* file_path) {
    FILE* fp = fopen(file_path, "r");
    if (fp == NULL) {
        perror("Error opening input file");
        exit(EXIT_FAILURE);
    }

    char line[256];
    // ヘッダー行をスキップ
    if (fgets(line, sizeof(line), fp) == NULL) {
        fprintf(stderr, "Error: Input file is empty or unreadable.\n");
        fclose(fp);
        exit(EXIT_FAILURE);
    }

    // 都市の数を数える
    int count = 0;
    while (fgets(line, sizeof(line), fp) != NULL) {
        count++;
    }
    num_cities = count;

    // ファイルポインタを先頭に戻す(ヘッダーの後)
    rewind(fp);
    fgets(line, sizeof(line), fp);

    // 都市情報を格納するメモリを確保
    cities = (City*)malloc(num_cities * sizeof(City));
    if (cities == NULL) {
        perror("Failed to allocate memory for cities");
        fclose(fp);
        exit(EXIT_FAILURE);
    }
    
    // データを読み込む
    int i = 0;
    while (fgets(line, sizeof(line), fp) != NULL && i < num_cities) {
        if (sscanf(line, "%lf,%lf", &cities[i].x, &cities[i].y) == 2) {
            i++;
        }
    }
    fclose(fp);
}

/**
 * @brief 解（経路）をCSVファイルに書き込む
 * @param file_path 出力CSVファイルのパス
 * @param route 書き込む経路
 */
void write_solution(const char* file_path, const int* route) {
    FILE* fp = fopen(file_path, "w");
    if (fp == NULL) {
        perror("Error opening output file");
        exit(EXIT_FAILURE);
    }
    fprintf(fp, "index\n");
    for (int i = 0; i < num_cities; i++) {
        fprintf(fp, "%d\n", route[i]);
    }
    fclose(fp);
}

/**
 * @brief 2都市間のユークリッド距離を計算する
 * @param city1_idx 1つ目の都市のインデックス
 * @param city2_idx 2つ目の都市のインデックス
 * @return 2都市間の距離
 */
inline double calculate_distance(int city1_idx, int city2_idx) {
    double dx = cities[city1_idx].x - cities[city2_idx].x;
    double dy = cities[city1_idx].y - cities[city2_idx].y;
    return sqrt(dx * dx + dy * dy);
}

/**
 * @brief 経路全体の総距離を計算する
 * @param route 距離を計算する経路
 * @return 経路の総距離
 */
double calculate_total_distance(const int* route) {
    double total_dist = 0.0;
    for (int i = 0; i < num_cities; i++) {
        total_dist += calculate_distance(route[i], route[(i + 1) % num_cities]);
    }
    return total_dist;
}

/**
 * @brief 最近傍法で初期解を生成する
 * @return 生成された初期経路
 */
int* nearest_neighbor_heuristic() {
    int* route = (int*)malloc(num_cities * sizeof(int));
    bool* visited = (bool*)calloc(num_cities, sizeof(bool));
    if (route == NULL || visited == NULL) {
        perror("Failed to allocate memory for NN heuristic");
        exit(EXIT_FAILURE);
    }

    route[0] = 0; // 0番目の都市からスタート
    visited[0] = true;
    int current_city_idx = 0;

    for (int i = 1; i < num_cities; i++) {
        double min_dist = -1.0;
        int nearest_city_idx = -1;
        for (int j = 0; j < num_cities; j++) {
            if (!visited[j]) {
                double dist = calculate_distance(current_city_idx, j);
                if (nearest_city_idx == -1 || dist < min_dist) {
                    min_dist = dist;
                    nearest_city_idx = j;
                }
            }
        }
        route[i] = nearest_city_idx;
        visited[nearest_city_idx] = true;
        current_city_idx = nearest_city_idx;
    }

    free(visited);
    return route;
}

/**
 * @brief 経路の一部を逆順にする
 * @param route 経路
 * @param start 開始インデックス
 * @param end 終了インデックス
 */
void reverse_segment(int* route, int start, int end) {
    while (start < end) {
        int temp = route[start];
        route[start] = route[end];
        route[end] = temp;
        start++;
        end--;
    }
}

/**
 * @brief 2-opt法による局所探索。1秒ごとに進捗を表示する。
 * @param route 改善対象の経路 (この経路は直接変更される)
 */
void local_search_2opt(int* route) {
    bool improved = true;
    struct timeval last_update_time, current_time;
    gettimeofday(&last_update_time, NULL);

    while (improved) {
        improved = false;
        for (int i = 0; i < num_cities - 1; i++) {
            for (int j = i + 1; j < num_cities; j++) {
                // --- 1秒ごとの進捗表示ロジック ---
                gettimeofday(&current_time, NULL);
                double time_diff = (current_time.tv_sec - last_update_time.tv_sec) + 
                                   (current_time.tv_usec - last_update_time.tv_usec) / 1e6;
                if (time_diff > 1.0) {
                    printf("\r    -> 2-opt search in progress... (Checking node i=%d/%d)", i, num_cities);
                    fflush(stdout);
                    last_update_time = current_time;
                }
                // --- 進捗表示ロジックここまで ---
                
                // 元の辺: (i, i+1) と (j, j_next)
                double original_dist = calculate_distance(route[i], route[(i + 1) % num_cities]) + 
                                       calculate_distance(route[j], route[(j + 1) % num_cities]);
                // 新しい辺: (i, j) と (i+1, j_next)
                double new_dist = calculate_distance(route[i], route[j]) + 
                                  calculate_distance(route[(i + 1) % num_cities], route[(j + 1) % num_cities]);

                if (new_dist < original_dist) {
                    reverse_segment(route, (i + 1) % num_cities, j);
                    improved = true;
                    // 改善が見つかったら、ループを最初からやり直す
                    goto next_improvement_search;
                }
            }
        }
    next_improvement_search:;
    }
    printf("\r    -> 2-opt search finished.                                          \n");
    fflush(stdout);
}


/**
 * @brief Double Bridge操作による摂動(kick)。
 * @param route 摂動を加える経路
 */
void double_bridge_kick(int* route) {
    if (num_cities < 4) return; // 4都市未満では実行不可

    int* temp_route = (int*)malloc(num_cities * sizeof(int));
    if (temp_route == NULL) {
        perror("Failed to allocate memory for kick");
        return;
    }

    int p1 = 1 + (rand() % (num_cities / 4));
    int p2 = p1 + 1 + (rand() % (num_cities / 4));
    int p3 = p2 + 1 + (rand() % (num_cities / 4));

    int current = 0;
    // seg1 (0 to p1-1)
    for (int i = 0; i < p1; i++) temp_route[current++] = route[i];
    // seg4 (p3 to num_cities-1)
    for (int i = p3; i < num_cities; i++) temp_route[current++] = route[i];
    // seg3 (p2 to p3-1)
    for (int i = p2; i < p3; i++) temp_route[current++] = route[i];
    // seg2 (p1 to p2-1)
    for (int i = p1; i < p2; i++) temp_route[current++] = route[i];
    
    memcpy(route, temp_route, num_cities * sizeof(int));
    free(temp_route);
}


/**
 * @brief 反復局所探索法(ILS)を実行する
 * @param max_iterations 最大反復回数
 * @param time_limit_sec 実行時間制限（秒）
 * @return 最適化された最終経路
 */
int* iterated_local_search(int max_iterations, int time_limit_sec) {
    time_t start_time = time(NULL);

    // 1. 初期化 (最近傍法を使用)
    printf("[Phase 1] Creating initial route with Nearest Neighbor Heuristic...\n");
    int* x_0 = nearest_neighbor_heuristic();

    // 2-optで初期解をさらに改善
    printf("[Phase 2] Performing initial local search (This may take a long time)...\n");
    local_search_2opt(x_0);
    
    int* x_best = (int*)malloc(num_cities * sizeof(int));
    if (x_best == NULL) {
        perror("Failed to allocate memory for x_best");
        exit(EXIT_FAILURE);
    }
    memcpy(x_best, x_0, num_cities * sizeof(int));
    free(x_0); // x_0は不要になったので解放

    double best_dist = calculate_total_distance(x_best);
    printf("Initial Best Distance: %.2f\n\n", best_dist);

    // 2. 反復
    printf("[Phase 3] Starting Iterated Local Search main loop...\n");
    for (int i = 0; i < max_iterations; i++) {
        printf("--- ILS Iteration %d/%d ---\n", i + 1, max_iterations);
        if (time(NULL) - start_time > time_limit_sec) {
            printf("Time limit of %d seconds reached.\n", time_limit_sec);
            break;
        }

        // 現在の最良解をコピーして摂動を加える
        int* x_kicked = (int*)malloc(num_cities * sizeof(int));
        if (x_kicked == NULL) {
            perror("Failed to allocate memory for x_kicked");
            break;
        }
        memcpy(x_kicked, x_best, num_cities * sizeof(int));
        
        printf("  - Perturbing solution (Double Bridge Kick)...\n");
        double_bridge_kick(x_kicked);

        printf("  - Running local search on the new route...\n");
        local_search_2opt(x_kicked);
        
        double new_dist = calculate_total_distance(x_kicked);

        if (new_dist < best_dist) {
            free(x_best); // 古い最良解を解放
            x_best = x_kicked; // 新しい最良解に更新
            best_dist = new_dist;
            printf("  -> 🎉 New best solution found! Distance: %.2f\n\n", best_dist);
        } else {
            printf("  -> No improvement. Current best: %.2f\n\n", best_dist);
            free(x_kicked); // 改善しなかったので解放
        }
    }

    printf("ILS finished. Final Best Distance: %.2f\n", best_dist);
    return x_best;
}

/**
 * @brief メイン関数
 */
int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <input_file> <output_file>\n", argv[0]);
        return 1;
    }

    srand(time(NULL)); // 乱数のシードを設定

    char* input_file = argv[1];
    char* output_file = argv[2];

    read_cities(input_file);
    printf("Solving TSP for %d cities from '%s'...\n", num_cities, input_file);

    int iterations;
    int time_limit_sec;

    // 都市数に応じてパラメータを調整
    if (num_cities < 100) {
        iterations = 5000;
        time_limit_sec = 300;
    } else if (num_cities < 500) {
        iterations = 100000;
        time_limit_sec = 1800; // 30分
    } else {
        iterations = 50000;
        time_limit_sec = 36000; // 10時間
    
    }
    
    int* best_route = iterated_local_search(iterations, time_limit_sec);

    write_solution(output_file, best_route);
    printf("Best route saved to '%s'.\n", output_file);

    double final_distance = calculate_total_distance(best_route);
    printf("Final validated distance: %f\n", final_distance);

    // メモリ解放
    free(cities);
    free(best_route);

    return 0;
}
