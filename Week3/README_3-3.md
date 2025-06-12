## 宿題3: 括弧にも対応した計算機を作る!!

作成したコード名は, [`modularized_calculator_3-3.py`](modularized_calculator_3-3.py)です.

宿題3の要件は, 括弧が最も演算として最優先されるようにする, ということです.

そのため, 新たに `read_multiply(line, index)` と `read_divide(line, index)` 関数を実装することで,
入力された数式 line の中のある位置 index から '(' と ')'　を読み取れるようにしました.

課題1,2と比較したときに, 最も変更点が多いのは関数 `evaluate(tokens)` です.

