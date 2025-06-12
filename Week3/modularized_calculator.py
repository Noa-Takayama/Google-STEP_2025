#! /usr/bin/python3

def read_number(line, index): # 入力された数式 line の中のある位置 index から数字を読み取る関数
    number = 0
    while index < len(line) and line[index].isdigit():
        number = number * 10 + int(line[index])
        index += 1
    if index < len(line) and line[index] == '.':
        index += 1
        decimal = 0.1
        while index < len(line) and line[index].isdigit():
            number += int(line[index]) * decimal
            decimal /= 10
            index += 1
    token = {'type': 'NUMBER', 'number': number}
    return token, index


def read_plus(line, index): # 入力された数式 line の中のある位置 index から '+' を読み取る関数
    token = {'type': 'PLUS'}
    return token, index + 1


def read_minus(line, index): # 入力された数式 line の中のある位置 index から '-' を読み取る関数
    token = {'type': 'MINUS'}
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
        else: # それ以外の数字が来たら
            print('Invalid character found: ' + line[index]) # エラーメッセージを出力して終了
            exit(1)
        tokens.append(token)
    return tokens # 最終的に, 作成したトークンを順番に並べたリストを返す. 
    
    
"""例えば, "1+2-3.5" という数式を入力した場合,
[{'type': 'NUMBER', 'number': 1}, {'type': 'PLUS'}, {'type': 'NUMBER', 'number': 2}, {'type': 'MINUS'}, {'type': 'NUMBER', 'number': 3.5}
のようなリストが返されることになる"""


def evaluate(tokens): # ここが tokenize 関数で作られたトークンから, 実際の計算を行う関数
    answer = 0
    tokens.insert(0, {'type': 'PLUS'}) # 最初の数字が正の数であることを明確にする. これをしないと, 最初の数字が負の数だった場合に計算がうまくいかない
    index = 1 # トークンの最初は '+' なので, 1 から始める
    # トークンのリストを順番に見ていく
    while index < len(tokens): # トークンのリストの最後まで
        if tokens[index]['type'] == 'NUMBER': # トークンの種類が 'NUMBER' だったら
            if tokens[index - 1]['type'] == 'PLUS': # 直前のトークンが '+' だったら
                answer += tokens[index]['number'] # 現在のトークンの数字を answer に足す
            elif tokens[index - 1]['type'] == 'MINUS': # 直前のトークンが '-' だったら
                answer -= tokens[index]['number'] # 現在のトークンの数字を answer から引く
            else:
                print('Invalid syntax')
                exit(1)
        index += 1
    return answer


def test(line): # テスト用の関数. 入力された数式 line をトークンに分解して計算し, 期待する結果と比較する
    tokens = tokenize(line)
    # tokenize と evaluate 関数を使って計算した結果 actual_answer と, Python の eval 関数を使って計算した結果 expected_answer を比較する
    actual_answer = evaluate(tokens) 
    expected_answer = eval(line)
    if abs(actual_answer - expected_answer) < 1e-8: # 計算結果が期待値とほぼ等しいかどうかを確認する
        # ほぼ等しい場合は PASS と表示
        print("PASS! (%s = %f)" % (line, expected_answer))
    else: # ほぼ等しくない場合は FAIL と表示
        print("FAIL! (%s should be %f but was %f)" % (line, expected_answer, actual_answer))


# Add more tests to this function :)
def run_test():
    print("==== Test started! ====")
    test("1+2")
    test("1.0+2.1-3")
    print("==== Test finished! ====\n")

run_test()

while True:
    print('> ', end="")
    line = input()
    tokens = tokenize(line)
    answer = evaluate(tokens)
    print("answer = %f\n" % answer)
