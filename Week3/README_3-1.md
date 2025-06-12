## 宿題1: 掛け算と割り算の関数実装!!

作成したコード名は, [`modularized_calculator.py`](modularized_calculator.py)です.

まず宿題1の要件は, 簡単電卓器に対し, 掛け算と割り算の機能を実装することです.

そのため, `read_multiply(line, index)` と `read_divide(line, index)` を追加実装しました.

さらに, 掛け算・割り算が足し算や引き算よりも先行するようにするため, `evaluate(tokens)` の部分に新しく `new_tokens` という新しいリストを作成しました.