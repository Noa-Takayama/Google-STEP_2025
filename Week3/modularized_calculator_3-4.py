import math

# 課題4: 絶対値, 小数の切り捨て, 四捨五入を追加実装してみよう！

def read_number(line, index):
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

def read_plus(line, index):
    token = {'type': 'PLUS'}
    return token, index + 1

def read_minus(line, index):
    token = {'type': 'MINUS'}
    return token, index + 1

def read_multiply(line, index):
    token = {'type': 'MULTIPLY'}
    return token, index + 1

def read_divide(line, index):
    token = {'type': 'DIVIDE'}
    return token, index + 1

def read_open_bracket(line, index):
    token = {'type': 'OPEN_BRACKET'}
    return token, index + 1

def read_close_bracket(line, index):
    token = {'type': 'CLOSE_BRACKET'}
    return token, index + 1

def tokenize(line):
    tokens = []
    index = 0
    # 括弧のリストを定義
    bracket_types = ['OPEN_BRACKET', 'ABS_OPEN_BRACKET', 'INT_OPEN_BRACKET', 'ROUND_OPEN_BRACKET']

    while index < len(line):
        token_to_append = []

        # 単独マイナスの処理
        # なんか, -5 とかの処理がうまくいかないことがあったので, 安定化のために入れてみました
        if line[index] == '-' and (not tokens or tokens[-1]['type'] in ['PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE'] + bracket_types):
            tokens.append({'type': 'NUMBER', 'number': 0})
            token, index = read_minus(line, index)
            token_to_append.append(token)

        # 課題4の追加実装!
        elif line[index:index+6] == 'round(':
            token_to_append.append({'type': 'ROUND_OPEN_BRACKET'})
            index += 6
        elif line[index:index+4] == 'abs(':
            token_to_append.append({'type': 'ABS_OPEN_BRACKET'})
            index += 4
        elif line[index:index+4] == 'int(':
            token_to_append.append({'type': 'INT_OPEN_BRACKET'})
            index += 4
        # 課題4の追加ここまで

        elif line[index].isdigit():
            token, index = read_number(line, index)
            token_to_append.append(token)
        elif line[index] == '+':
            token, index = read_plus(line, index)
            token_to_append.append(token)
        elif line[index] == '-':
            token, index = read_minus(line, index)
            token_to_append.append(token)
        elif line[index] == '*':
            token, index = read_multiply(line, index)
            token_to_append.append(token)
        elif line[index] == '/':
            token, index = read_divide(line, index)
            token_to_append.append(token)
        elif line[index] == '(':
            token, index = read_open_bracket(line, index)
            token_to_append.append(token)
        elif line[index] == ')':
            token, index = read_close_bracket(line, index)
            token_to_append.append(token)
        elif line[index].isspace():
            index += 1
            continue
        else:
            print('Invalid character found: ' + line[index])
            exit(1)
        
        tokens.extend(token_to_append)

    return tokens

def evaluate(tokens):
    values = []
    operators = []
    # 括弧のリストを定義
    bracket_types = ['OPEN_BRACKET', 'ABS_OPEN_BRACKET', 'INT_OPEN_BRACKET', 'ROUND_OPEN_BRACKET']

    def priority(op_type):
        if op_type in ['MULTIPLY', 'DIVIDE']: return 2 # 掛け算・割り算は一番優先度が高い
        if op_type in ['PLUS', 'MINUS']: return 1 # 足し算・引き算はその次に優先度が高い
        return 0 # 絶対値だったり, 切り捨て, 四捨五入は優先度が一番低い!

    def apply_op():
        op = operators.pop()
        # 関数（単項演算子）の処理
        if op in ['ABS_OPEN_BRACKET', 'INT_OPEN_BRACKET', 'ROUND_OPEN_BRACKET']:
            val = values.pop()
            if op == 'ABS_OPEN_BRACKET': values.append(abs(val))
            elif op == 'INT_OPEN_BRACKET': values.append(math.trunc(val)) # 負数も正しく切り捨てるためにtrunc
            elif op == 'ROUND_OPEN_BRACKET': values.append(round(val))
            return
        
        # 二項演算子の処理
        right = values.pop()
        left = values.pop()
        if op == 'PLUS': values.append(left + right)
        elif op == 'MINUS': values.append(left - right)
        elif op == 'MULTIPLY': values.append(left * right)
        elif op == 'DIVIDE':
            if right == 0: raise ZeroDivisionError("0 で割ることはできません！")
            values.append(left / right)

    for token in tokens:
        if token['type'] == 'NUMBER':
            values.append(token['number'])
        elif token['type'] in bracket_types:
            operators.append(token['type'])
        elif token['type'] == 'CLOSE_BRACKET':
            while operators[-1] not in bracket_types:
                apply_op()
            opening_bracket = operators.pop()
            # 関数呼び出しの場合、関数を適用する
            if opening_bracket != 'OPEN_BRACKET':
                operators.append(opening_bracket)
                apply_op()
        else: # 通常の演算子
            # ### ここが最重要修正点 ###
            # 括弧は演算子ではないので、スタックからポップしないように条件を追加
            while operators and operators[-1] not in bracket_types and priority(operators[-1]) >= priority(token['type']):
                apply_op()
            operators.append(token['type'])

    while operators:
        apply_op()

    return values[0]


def test(line):
    # test関数はevalを使う元のバージョンのまま
    # `int(-2.9)` のようなPythonと挙動が異なるテストは手動で検証が必要
    # ここでは、元の課題のテストケースが通ることを優先
    if line == "int(-2.9)": # Pythonのint(-2.9)は-2になるので、手動でテスト
        expected_answer = -2
        tokens = tokenize(line)
        actual_answer = evaluate(tokens)
        if actual_answer == expected_answer:
            print("テスト成功! (%s = %f)" % (line, float(expected_answer)))
        else:
            print("テスト失敗! (%s != %f, 実際の答えは %f)" % (line, float(expected_answer), actual_answer))
        return

    tokens = tokenize(line)
    actual_answer = None
    try:
        actual_answer = evaluate(tokens)
        expected_answer = eval(line)
        if abs(actual_answer - expected_answer) < 1e-8:
            print("テスト成功! (%s = %f)" % (line, expected_answer))
        else:
            print("テスト失敗! (%s != %f, 実際の答えは %f)" % (line, expected_answer, actual_answer))
    except ZeroDivisionError:
        print("テスト成功! (%s = inf)" % line)
    except Exception as e:
        print(f"Error during evaluation of '{line}': {e}")


def run_test():
    print("==== Test started! ====")
    test("1+2")
    test("1.0+2.1-3")
    test("3.0+4*2-1/5")
    test("10/2*3")
    test("1+2*3-4/2")
    test("5*6/3")
    test("7-8*0.5+10/2")
    test("1/0")
    test("(1+2)*3")
    test("3*(4+5)/9")
    test("(3.0+4*(2-1))/5")
    test("((10/2)+5)*2")
    test("10+(5*(6-3))")
    test("(1+2)*(3-1)")
    test("10/(2+3)")
    test("12.5*(2+3.5)/5")

    # 課題4の追加テスト
    test("abs(-5)") # 絶対値のテスト
    test("abs(3.14)")

    test("int(3.9)") # 小数の切り捨てのテスト
    test("int(-2.9)") 

    test("round(3.5)") # 四捨五入のテスト
    test("round(3.4)")
    test("round(-4.4)")
    test("round(-4.5)") # pythonでは-4.5は-4に四捨五入される
    # 複合テスト
    test("abs(-3.5) + int(2.9) - round(4.5)")
    test("abs(0) + int(4.0) - round(-0.5)")
    print("==== Test finished! ====\n")

run_test()

while True:
    print('> ', end="")
    line = input()
    if line.lower() in ['exit', 'quit']:
        break
    try:
        tokens = tokenize(line)
        answer = evaluate(tokens)
        print("answer = %f\n" % answer)
    except Exception as e:
        print(f"エラー: {e}\n")