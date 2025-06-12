## 宿題3: 括弧にも対応した計算機を作る!!

作成したコード名は, [`modularized_calculator_3-3.py`](modularized_calculator_3-3.py)です.

宿題3の要件は, 括弧が最も演算として最優先されるようにする, ということです.

そのため, 新たに `read_multiply(line, index)` と `read_divide(line, index)` 関数を実装することで,
入力された数式 line の中のある位置 index から '(' と ')'　を読み取れるようにしました.

課題1,2と比較したときに, 最も変更点が多いのは関数 `evaluate(tokens)` です.

まず新たに, `priority_for_operator(token_type)` 関数を組み込みました.

これは, 演算子の優先順位を決定するための関数です.

`evaluate` 関数内では, 数値を保存するスタックとして `values` を, 演算子を保存するスタックとして `operators` を定めています.

## `modularized_calculator_3-3.py` より抜粋

```python
elif token['type'] in ['PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE']:
    while operators and precedence(operators[-1]) >= priority_for_operator(token['type']):
        # ...演算子スタックから演算子を取り出して計算する処理...
    operators.append(token['type'])

