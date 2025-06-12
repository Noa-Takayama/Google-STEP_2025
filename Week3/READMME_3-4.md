## 宿題4: 絶対値・小数の切り捨て・四捨五入の機能がついた計算機を作成する!!

作成したコードは, [`modularized_calculator_3-4.py`](modularized_calculator_3-4.py)です.


四則演算に加え, 絶対値, 小数の切り捨て, 四捨五入の機能を追加した電卓プログラムです.


## 課題4: 新機能（絶対値・切り捨て・四捨五入）の実装

### 要件

新たに関数として, 絶対値・小数の切り捨て・四捨五入を計算できるようにしました.

- **絶対値**: `abs(-2.2)` → `2.2`
- **小数切り捨て**: `int(1.55)` → `1`
- **四捨五入**: `round(1.55)` → `2`

> **⚠️ `round()` 関数の注意点 ⚠️**
> 
> このプログラムの四捨五入は, Pythonの組み込み関数 `round()` の仕様に基づいています.
> これは, 一般的な「.5は常に切り上げる」という四捨五入とは異なり、「**偶数への丸め**」（銀行家の丸め）という方式を採用しているそうです. 私たちが考える四捨五入とはちょっと挙動が違いますが, 間違いではないので安心してください😮‍💨
> 
> 丸める対象の数値がちょうど `.5` の場合, 最も近い**偶数**の整数に丸めるというルールだそうです.
> 
> 具体例：
> * `round(-4.4)` → `-4` (単純に近い整数)
> * `round(-4.5)` → `-4` (候補の-4と-5のうち、偶数である-4が選ばれる)
> * `round(-5.5)` → `-6` (候補の-5と-6のうち、偶数である-6が選ばれる)

---

### 実装のポイント

課題4の大きな変更点として、**`abs`や`int`といった関数を、特別な種類の括弧として扱う**があげられます. これにより、既存の括弧の処理ロジックを拡張する形で、綺麗に新機能を追加できました.

#### 1. 新しい「括弧」の仲間たちを定義

まず, 通常の括弧 `(` と, 新しく追加した関数 `abs(`, `int(`, `round(` を同じ**括弧の仲間**としてグループ化しました. これにより, 後のコードで「このトークンは括弧ですか？」というチェックが非常にシンプルになりました.

```python
# evaluate関数内
# 括弧のリストを定義
bracket_types = ['OPEN_BRACKET', 'ABS_OPEN_BRACKET', 'INT_OPEN_BRACKET', 'ROUND_OPEN_BRACKET']
```

#### 2. 関数を演算子スタックに積む

数式を左から順に見ていくメインループで `abs(` のような関数トークンが来た場合, 通常の `(` と全く同じように, `operators`（演算子）スタックに積みます.

これは「今から`abs`の計算が始まるよ」という合図をスタックに置いておくイメージです.

```python
# evaluate関数 メインループ内
elif token['type'] in bracket_types:
    operators.append(token['type'])
```

#### 3. 関数を実行する

計算ロジックの中心である `apply_op` 関数と, それを呼び出す `CLOSE_BRACKET` の処理が実装のキモとなります.

##### `apply_op` 関数の拡張

`apply_op` 関数の中に, 新たに関数を処理する専用ブロックを追加しました. `operators` スタックから取り出した演算子が `ABS_OPEN_BRACKET` (つまり, 絶対値を取る合図) などであった場合, `values` スタックから数値を**1つだけ**取り出し, 対応するPythonの関数で計算し, 結果を `values` スタックに戻します.

```python
def apply_op():
    op = operators.pop()
    # ▼▼▼▼▼ 課題4で追加した部分 ▼▼▼▼▼
    # 関数（単項演算子）の処理
    if op in ['ABS_OPEN_BRACKET', 'INT_OPEN_BRACKET', 'ROUND_OPEN_BRACKET']:
        val = values.pop() # 計算対象の数値を1つ取り出す
        if op == 'ABS_OPEN_BRACKET': values.append(abs(val))
        elif op == 'INT_OPEN_BRACKET': values.append(math.trunc(val))
        elif op == 'ROUND_OPEN_BRACKET': values.append(round(val))
        return # 関数の処理はここで終わり
    # ▲▲▲▲▲ 課題4で追加した部分 ▲▲▲▲▲
    
    # 二項演算子の処理 (元からあった部分)
    # ...
```

##### 閉じ括弧 `)` での関数実行

この `apply_op()` は, 閉じ括弧 `)` が来たときに呼び出されます.

閉じ括弧が来ると, まずその括弧の中の計算をすべて行います. その後、対応する開き括弧を取り出し, **それがただの `(` ではなかった場合**（つまり `abs(` などだった場合）, それは関数呼び出しだと判断し, `apply_op()` を呼び出して関数を実行します.

```python
# evaluate関数 メインループ内
elif token['type'] == 'CLOSE_BRACKET':
    # まず括弧の中身を全部計算する (例: 0-5 を計算して -5 にする)
    while operators[-1] not in bracket_types:
        apply_op()
    
    # 対応する開き括弧を取り出す
    opening_bracket = operators.pop()

    # ▼▼▼▼▼ 課題4で追加した部分 ▼▼▼▼▼
    # もし、ただの '(' じゃなくて 'abs(' だったら…
    if opening_bracket != 'OPEN_BRACKET':
        operators.append(opening_bracket) # もう一度スタックに戻して
        apply_op()                       # 関数を適用！
    # ▲▲▲▲▲ 課題4で追加した部分 ▲▲▲▲▲
```

#### 4. （優先順位の調整）

上記のロジックを正しく動作させるため、2つの重要な調整を行っています.

1.  **優先度の設定**: `abs(` などの関数を、括弧と同じように優先度が最低の `0` に設定しています. 

これにより、`+` や `*` などの演算子よりも先に絶対値や小数の切り捨てが行われないようにします.

    ```python
    def priority(op_type):
        if op_type in ['MULTIPLY', 'DIVIDE']: return 2
        if op_type in ['PLUS', 'MINUS']: return 1
        return 0 # 関数や括弧は優先度が一番低い
    ```

2.  **演算子ループの条件**: `+` や `*` などの通常の演算子を処理するループに,「スタックの一番上が括弧（や関数）ではないこと」という条件を追加しました. 

これは `5 * abs(-2)` のような式で, `*` が `abs(` を計算しようとするのを防ぐ目的です.

    ```python
    # evaluate関数 メインループ内
    else: # 通常の演算子
        while operators and operators[-1] not in bracket_types and priority(operators[-1]) >= priority(token['type']):
            apply_op()
        operators.append(token['type'])
    ```

---

以上の実装により, これまでの課題で作った既存の四則演算の関数を大きく変えることなく, 新しい関数機能を柔軟に追加することができました.