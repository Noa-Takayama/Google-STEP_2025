#! /usr/bin/python3

# token とは、プログラムの中で使われる最小の意味を持つ単位のこと

def read_number(line, index): # 入力された数式 line の中のある位置 index から数字を読み取る関数
    number = 0
    while index < len(line) and line[index].isdigit(): # インデックス部分を数字が続く限り読み取る
        # 例えば, "123" という文字列が与えられた場合,
        # 1 のとき number = 0 * 10 + 1 = 1
        # 2 のとき number = 1 * 10 + 2 = 12
        # 3 のとき number = 12 * 10 + 3 = 123
        # というように, 数字を一つずつ読み取っていく
        number = number * 10 + int(line[index])
        index += 1
    # 小数点 '.' が来たら小数部分を読み取る
    if index < len(line) and line[index] == '.':
        index += 1
        decimal = 0.1
        while index < len(line) and line[index].isdigit():
            # 例えば, "123.456" という文字列が与えられた場合,
            # 4 のとき number = 0 + 4 * 0.1 = 0.4
            # 5 のとき number = 0.4 + 5 * 0.01 = 0.45
            # 6 のとき number = 0.45 + 6 * 0.001 = 0.456
            # というように, 小数部分を一つずつ読み取っていく
            number += int(line[index]) * decimal
            decimal /= 10 # 0.1, 0.01, 0.001,... としていく
            index += 1
    token = {'type': 'NUMBER', 'number': number} # 読み取った数字をトークンとして保存する
    # 例えば, "123.456" という文字列が与えられた場合,
    # {'type': 'NUMBER', 'number': 123.456} というトークンが作成される
    return token, index # index も返すことで, 次にどこから読み取るかを示すことができる.
# read_number 関数により,
# トークンと次の読み取り位置を返すことができる.
# 例えば, "123.456" という文字列が与えられた場合,
# read_number 関数は {'type': 'NUMBER', 'number': 123.456} というトークンと, 次の読み取り位置を返すことになる
# これにより, 数式をトークンに分解することができるようになる!


def read_plus(line, index): # 入力された数式 line の中のある位置 index から '+' を読み取る関数
    token = {'type': 'PLUS'}
    return token, index + 1


def read_minus(line, index): # 入力された数式 line の中のある位置 index から '-' を読み取る関数
    token = {'type': 'MINUS'}
    return token, index + 1

# 宿題1: 掛け算と割り算を追加してみよう!

def read_multiply(line, index): # 入力された数式 line の中のある位置 index から '*' を読み取る関数
    token = {'type': 'MULTIPLY'}
    return token, index + 1

def read_divide(line, index): # 入力された数式 line の中のある位置 index から '/' を読み取る関数
    token = {'type': 'DIVIDE'}
    return token, index + 1


def tokenize(line): # 入力された数式全体をトークンに分解する中心的な役割を果たしている
    tokens = []
    index = 0
    while index < len(line): # 数式の最初から最後まで
        if line[index].isdigit(): # インデックス部分が数字だったら
            (token, index) = read_number(line, index) # 数字を読み取る read_number 関数を呼び出す
        elif line[index] == '+': # インデックス部分が '+' だったら
            (token, index) = read_plus(line, index) # '+' を読み取る read_plus 関数を呼び出す
        elif line[index] == '-': # インデックス部分が '-' だったら
            (token, index) = read_minus(line, index) # '-' を読み取る read_minus 関数を呼び出す

        # 宿題1: 掛け算と割り算を追加してみよう!
        elif line[index] == '*': # インデックス部分が '*' だったら
            (token, index) = read_multiply(line, index) # '*' を読み取る read_multiply 関数を呼び出す
        elif line[index] == '/': # インデックス部分が '/' だったら
            (token, index) = read_divide(line, index) # '/' を読み取る read_divide 関数を呼び出す
        
        else: # それ以外の数字が来たら
            print('Invalid character found: ' + line[index]) # エラーメッセージを出力して終了
            exit(1)
        tokens.append(token)
    return tokens # 最終的に, 作成したトークンを順番に並べたリストを返す. 
    
    
"""例えば, "1+2-3.5" という数式を入力した場合,
[{'type': 'NUMBER', 'number': 1}, {'type': 'PLUS'}, {'type': 'NUMBER', 'number': 2}, {'type': 'MINUS'}, {'type': 'NUMBER', 'number': 3.5}
のようなリストが返されることになる"""


def evaluate(tokens): # ここが tokenize 関数で作られたトークンから, 実際の計算を行う関数
    # 1回目の評価: 掛け算と割り算が先行するようにする!
    new_tokens = [] # 新しいトークンのリストを作成
    index = 0 # トークンの最初から
    while index < len(tokens): # トークンのリストの最後まで
        token = tokens[index] # 現在のトークンを取得
        if token['type'] == 'NUMBER': # トークンの種類が 'NUMBER' だったら
            new_tokens.append(token) # 新しいトークンのリストに追加する

        # 宿題1: 掛け算の処理の追加
        elif token['type'] == 'MULTIPLY': # トークンの種類が 'MULTIPLY' だったら
            # 直前の数値と次の数値を掛ける
            left_number = new_tokens.pop() # 新しいトークンのリストから直前の数値を取り出す
            index += 1 # 次のトークンに進む
            right_number = tokens[index] # 次のトークンを取得
            result = left_number['number'] * right_number['number'] # 直前の数値と次の数値を掛ける
            new_tokens.append({'type': 'NUMBER', 'number': result})
        # 宿題1: 割り算の処理の追加
        elif token['type'] == 'DIVIDE': # トークンの種類が 'DIVIDE' だったら
            # 直前の数値を次の数値で割る
            left_number = new_tokens.pop()
            index += 1
            right_number = tokens[index]
            if right_number['number'] == 0: # 0で割る場合はエラーが出るようにする   
                print(" 0 で割ることはできません !")
                exit(1)
            result = left_number['number'] / right_number['number']
            new_tokens.append({'type': 'NUMBER', 'number': result})
        else: # トークンの種類が 'PLUS' または 'MINUS' だったら
            new_tokens.append(token) # 新しいトークンのリストにそのまま追加する
        index += 1
    
    # 2回目の評価: '+' と '-' の計算を行う
    answer = 0
    new_tokens.insert(0, {'type': 'PLUS'}) # 最初の数字が正の数であることを明確にする. これをしないと, 最初の数字が負の数だった場合に計算がうまくいかない
    index = 1 # トークンの最初は '+' なので, 1 から始める
    # トークンのリストを順番に見ていく
    while index < len(new_tokens): # トークンのリストの最後まで
        if new_tokens[index]['type'] == 'NUMBER': # トークンの種類が 'NUMBER' だったら
            if new_tokens[index - 1]['type'] == 'PLUS': # 直前のトークンが '+' だったら
                answer += new_tokens[index]['number'] # 現在のトークンの数字を answer に足す
            elif new_tokens[index - 1]['type'] == 'MINUS': # 直前のトークンが '-' だったら
                answer -= new_tokens[index]['number'] # 現在のトークンの数字を answer から引く
            else:
                print('Invalid syntax')
                exit(1)
        index += 1
    return answer


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
    print("==== Test finished! ====\n")

run_test()

while True:
    print('> ', end="")
    line = input()
    tokens = tokenize(line)
    answer = evaluate(tokens)
    print("answer = %f\n" % answer)
