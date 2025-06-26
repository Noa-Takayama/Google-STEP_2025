# 巡回セールスマン問題ソルバー (TSP Solver)

## 概要

Week5 では、巡回セールスマン問題（TSP）を実装した。実装には、強力なヒューリスティック手法である**反復局所探索法 (Iterated Local Search, ILS)** を用いた。

## アルゴリズム

今回の `solver_ils.py` は、以下のアルゴリズムを組み合わせて最適な巡回路を探索する。

-   **反復局所探索法 (Iterated Local Search, ILS)**
    -   局所探索が局所に集中しすぎることなく、探索空間を広く探索するためのメタヒューリスティックである。
-   **局所探索 (Local Search)**: **2-opt法**
    -   経路上の2本の辺を交換し、経路長が短くなる場合は更新する操作を繰り返すことで、解を改善する。
-   **摂動 (Perturbation / "Kick")**: **Double Bridge法**
    -   局所最適解から脱出するために、経路に意図的に大きな変更を加える操作である。4本の辺を交換するこの操作は、2-opt法では到達しにくい解へのジャンプを可能にするという。

## 使い方

### 必要なもの

-   Python 3

### 実行方法

1.  ターミナルを開き、以下のコマンドを実行する。

    ```bash
    # python solver_ils.py <入力ファイル> <出力ファイル>

    # 例: Challenge 4 (N=128) を解くならば
    python solver_ils.py input_4.csv output_4.csv
    ```

3.  実行後、同じディレクトリに結果ファイル（例: `output_4.csv`）が保存される。

### 全チャレンジの実行

以下のコマンドで、すべてのチャレンジ（0〜6）を連続して実行できる。

```bash
for i in {0..6}; do
    echo "--- Solving Challenge $i ---"
    python solver_ils.py "input_$i.csv" "output_$i.csv"
done

ただし、チャレンジ6は非常に時間がかかるので、注意が必要である。

手元のパソコンで行った結果を以下に記す。

チャレンジ	都市数 (N)	経路長 (Path Length)
Challenge 0	5	[3291.62]
Challenge 1	8	[3778.72]
Challenge 2	16	[4494.42]
Challenge 3	64	[8118.40]
Challenge 4	128	[10710.07]
Challenge 5	512	[20869.06]
Challenge 6	2048 [42216.73]
