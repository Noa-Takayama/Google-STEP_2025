# 課題3: 括弧付きに対応した計算機を作成しよう!

def read_number(line, index): # 入力された数式 line の中のある位置 index から数字を読み取る関数
    number = 0
    while index < len(line) and line[index].isdigit(): # インデックス部分を数字が続く限り読み取る
        number = number * 10 + int(line[index])
        index += 1
    # 小数点 '.' が来たら小数部分を読み取る
    if index < len(line) and line[index] == '.':
        index += 1
        decimal = 0.1
        while index < len(line) and line[index].isdigit():
            number += int(line[index]) * decimal
            decimal /= 10 # 0.1, 0.01, 0.001,... としていく
            index += 1
    token = {'type': 'NUMBER', 'number': number} # 読み取った数字をトークンとして保存する
    # {'type': 'NUMBER', 'number': 123.456} というトークンが作成される
    return token, index # index も返すことで, 次にどこから読み取るかを示すことができる.

def read_plus(line, index): # 入力された数式 line の中のある位置 index から '+' を読み取る関数
    token = {'type': 'PLUS'}
    return token, index + 1

def read_minus(line, index): # 入力された数式 line の中のある位置 index から '-' を読み取る関数
    token = {'type': 'MINUS'}
    return token, index + 1

def read_multiply(line, index): # 入力された数式 line の中のある位置 index から '*' を読み取る関数
    token = {'type': 'MULTIPLY'}
    return token, index + 1

def read_divide(line, index): # 入力された数式 line の中のある位置 index から '/' を読み取る関数
    token = {'type': 'DIVIDE'}
    return token, index + 1

# 課題3: 括弧付きに対応した計算機を作成しよう!のための関数
def read_open_bracket(line, index): # 入力された数式 line の中のある位置 index から '(' を読み取る関数
    token = {'type': 'OPEN_BRACKET'}
    return token, index +1

def read_close_bracket(line, index): # 入力された数式 line の中のある位置 index から ')' を読み取る関数
    token = {'type': 'CLOSE_BRACKET'}
    return token, index + 1
# ここまでが課題3のために追加した関数

def tokenize(line): # 入力された数式全体をトークンに分解する中心的な役割を果たしている
    tokens = []
    index = 0
    while index < len(line): # 数式の最初から最後まで
        if line[index].isdigit(): # インデックス部分が数字だったら
            (token, index) = read_number(line, index) # read_number 関数を呼び出す
        elif line[index] == '+': # インデックス部分が '+' だったら
            (token, index) = read_plus(line, index) # read_plus 関数を呼び出す
        elif line[index] == '-': # インデックス部分が '-' だったら
            (token, index) = read_minus(line, index) # read_minus 関数を呼び出す
        elif line[index] == '*': # インデックス部分が '*' だったら
            (token, index) = read_multiply(line, index) # read_multiply 関数を呼び出す
        elif line[index] == '/': # インデックス部分が '/' だったら
            (token, index) = read_divide(line, index) # read_divide 関数を呼び出す
        
        # ここが課題3のために追加した部分
        elif line[index] == '(': # インデックス部分が '(' だったら
            (token,index) = read_open_bracket(line, index) # read_open_bracket 関数を呼び出す
        elif line[index] == ')': # インデックス部分が ')' だったら
            (token, index) = read_close_bracket(line, index) # read_close_bracket 関数を呼び出す
        # ここまでが追加部分
        
        else: # それ以外の数字が来たら
            print('Invalid character found: ' + line[index]) # エラーメッセージを出力して終了
            exit(1)
        tokens.append(token)
    return tokens # 最終的に, 作成したトークンを順番に並べたリストを返す. 


# 課題3のために, 一番変更点が多いのが evaluate 関数
# 括弧がある場合, 括弧内を最優先で計算する必要がある.
# そして, 括弧がない場合は, 掛け算と割り算が先行して計算されるように調整する.

def evaluate(tokens):
    def precedence(token_type):
        if token_type in ['MULTIPLY', 'DIVIDE']: # 掛け算と割り算は優先度が高い
            return 2
        elif token_type in ['PLUS', 'MINUS']: # 足し算と引き算は優先度が低い
            return 1
        else: # 括弧は優先度が最も高い
            return 0

    values = [] # 数字を保存するスタック
    operators = [] # 演算子を保存するスタック
    index = 0 # トークンの最初から
    while index < len(tokens): # トークンのリストの最後まで
        token = tokens[index] # 現在のトークンを取得する変数
        if token['type'] == 'NUMBER': # トークンの種類が 'NUMBER' だったら
            values.append(token['number']) # 数字を values スタックにプッシュする
        elif token['type'] == 'OPEN_BRACKET': # トークンの種類が 'OPEN_BRACKET' だったら
            operators.append(token['type']) # 演算子スタックに 'OPEN_BRACKET' をプッシュする
        elif token['type'] == 'CLOSE_BRACKET': # トークンの種類が 'CLOSE_BRACKET' だったら
            while operators[-1] != 'OPEN_BRACKET': # 開き括弧が再び出てくるまで, 括弧部分が存在することになる!!!!
                operator = operators.pop()
                right_operand = values.pop()
                left_operand = values.pop()
                if operator == 'PLUS':
                    values.append(left_operand + right_operand)
                elif operator == 'MINUS':
                    values.append(left_operand - right_operand)
                elif operator == 'MULTIPLY':
                    values.append(left_operand * right_operand)
                elif operator == 'DIVIDE':
                    if right_operand == 0:
                        print("0 で割ることはできません !")
                        exit(1)
                    values.append(left_operand / right_operand)
            operators.pop() # 対応する OPEN_BRACKET をポップ
        elif token['type'] in ['PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE']:
            while operators and precedence(operators[-1]) >= precedence(token['type']):
                operator = operators.pop() # 演算子スタックから演算子をポップ
                right_operand = values.pop() # 数字スタックから右辺の値をポップ
                left_operand = values.pop() # 数字スタックから左辺の値をポップ
                # 例えば, 'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE' のいずれかの演算子が来た場合
                # 演算子に応じて計算を行う
                if operator == 'PLUS':
                    values.append(left_operand + right_operand)
                elif operator == 'MINUS':
                    values.append(left_operand - right_operand)
                elif operator == 'MULTIPLY':
                    values.append(left_operand * right_operand)
                elif operator == 'DIVIDE':
                    if right_operand == 0:
                        print("0 で割ることはできません !")
                        exit(1)
                    values.append(left_operand / right_operand)
            operators.append(token['type']) # 演算子をスタックにプッシュする"
        index += 1

    while operators: # 演算子スタックに残っている演算子がある限り
        operator = operators.pop()
        right_operand = values.pop()
        left_operand = values.pop()
        if operator == 'PLUS':
            values.append(left_operand + right_operand)
        elif operator == 'MINUS':
            values.append(left_operand - right_operand)
        elif operator == 'MULTIPLY':
            values.append(left_operand * right_operand)
        elif operator == 'DIVIDE':
            if right_operand == 0:
                print("0 で割ることはできません !")
                exit(1)
            values.append(left_operand / right_operand)

    return values[0]


def test(line): # テスト用の関数. 入力された数式 line をトークンに分解して計算し, 期待する結果と比較する
    tokens = tokenize(line)
    # tokenize と evaluate 関数を使って計算した結果 actual_answer と, Python の eval 関数を使って計算した結果 expected_answer を比較する
    actual_answer = evaluate(tokens)
    try:
        expected_answer = eval(line) # Python の eval 関数を使って計算する
        if abs(actual_answer - expected_answer) < 1e-8:
            print("テスト成功! (%s = %f)" % (line, expected_answer)) # テストが成功した場合のメッセージ
        else:
            print("テスト失敗! (%s != %f, 実際の答えは %f)" % (line, expected_answer, actual_answer))
    except ZeroDivisionError: # 0 で割った場合のエラー処理を追加する
        if abs(actual_answer) == float('inf'): # 実際の答えが無限大であったら
            print("テスト成功! (%s = inf)" % line)
        else:
            print("テスト失敗! (%s != inf, 実際の答えは %f)" % (line, actual_answer))
    except Exception as e: # その他のエラーが発生した場合
        print(f"Error during evaluation of '{line}': {e}")

# Add more tests to this function :)
def run_test():
    print("==== Test started! ====")
    test("1+2")
    test("1.0+2.1-3")
    test("3.0+4*2-1/5") # 掛け算と割り算が先行することを確認する
    test("10/2*3") # 割り算が掛け算よりも先に計算されることを確認する
    test("1+2*3-4/2") # 掛け算と割り算が先行することを確認する
    test("5*6/3")
    test("7-8*0.5+10/2")
    test("1/0") # 0 で割る場合のテスト 「0で割ることはできません !」と表示されることを確認する

    # 課題3のために追加したテスト
    test("(1+2)*3")
    test("3*(4+5)/9")
    test("(3.0 + 4 * (2 - 1)) / 5")
    test("((10/2) + 5) * 2")
    test("10 + (5 * (6 - 3))")
    test("(1+2)*(3-1)")
    test("10/(2+3)")
    test("12.5 * (2 + 3.5) / 5")
    print("==== Test finished! ====\n")

run_test()

while True:
    print('> ', end="")
    line = input()
    tokens = tokenize(line)
    answer = evaluate(tokens)
    print("answer = %f\n" % answer)
