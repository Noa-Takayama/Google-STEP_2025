# 課題4: 絶対値, 小数の切り捨て, 四捨五入を追加実装してみよう！

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

def read_multiply(line, index): # 入力された数式 line の中のある位置 index から '*' を読み取る関数
    token = {'type': 'MULTIPLY'}
    return token, index + 1

def read_divide(line, index): # 入力された数式 line の中のある位置 index から '/' を読み取る関数
    token = {'type': 'DIVIDE'}
    return token, index + 1

def read_open_bracket(line, index): # 入力された数式 line の中のある位置 index から '(' を読み取る関数
    token = {'type': 'OPEN_BRACKET'}
    return token, index +1

def read_close_bracket(line, index): # 入力された数式 line の中のある位置 index から ')' を読み取る関数
    token = {'type': 'CLOSE_BRACKET'}
    return token, index + 1

def tokenize(line): # 入力された数式全体をトークンに分解する中心的な役割を果たしている
    tokens = []
    index = 0
    while index < len(line): 
        if line[index].isdigit(): 
            (token, index) = read_number(line, index) 
        elif line[index] == '+': 
            (token, index) = read_plus(line, index)
        elif line[index] == '-':
            (token, index) = read_minus(line, index) 
        elif line[index] == '*': 
            (token, index) = read_multiply(line, index) 
        elif line[index] == '/': 
            (token, index) = read_divide(line, index) 
        elif line[index] == '(': 
            (token,index) = read_open_bracket(line, index) 
        elif line[index] == ')': 
            (token, index) = read_close_bracket(line, index) 
        else: 
            print('Invalid character found: ' + line[index]) 
            exit(1)
        tokens.append(token)
    return tokens 

def evaluate(tokens):
    def priority_for_operator(token_type):
        if token_type in ['MULTIPLY', 'DIVIDE']: # 掛け算と割り算は優先度が高い
            return 2
        elif token_type in ['PLUS', 'MINUS']: # 足し算と引き算は優先度が低い
            return 1
        else: # 括弧は優先度が最も高い
            return 0

    values = [] # 数字を保存するスタック
    operators = [] # 演算子を保存するスタック
    index = 0 
    while index < len(tokens): 
        token = tokens[index] 
        if token['type'] == 'NUMBER': 
            values.append(token['number']) # 数字を values スタックにプッシュする
        elif token['type'] == 'OPEN_BRACKET': 
            operators.append(token['type']) # 演算子スタックに 'OPEN_BRACKET' をプッシュする
        elif token['type'] == 'CLOSE_BRACKET': 
            while operators[-1] != 'OPEN_BRACKET':
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
            operators.pop() 
        elif token['type'] in ['PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE']:
            while operators and priority_for_operator(operators[-1]) >= priority_for_operator(token['type']):
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
                        raise ZeroDivisionError("0 で割ることはできません !") # 0 で割る場合はエラーを出す
                    values.append(left_operand / right_operand)
            operators.append(token['type']) 
        index += 1

    while operators: 
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
                raise ZeroDivisionError("0 で割ることはできません !")
            values.append(left_operand / right_operand)

    return values[0]


def test(line): 
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
    test("(1+2)*3")
    test("3*(4+5)/9")
    test("(3.0+4*(2-1))/5")
    test("((10/2)+5)*2")
    test("10+(5*(6-3))")
    test("(1+2)*(3-1)")
    test("10/(2+3)")
    test("12.5*(2+3.5)/5")
    print("==== Test finished! ====\n")

run_test()

while True:
    print('> ', end="")
    line = input()
    tokens = tokenize(line)
    answer = evaluate(tokens)
    print("answer = %f\n" % answer)
