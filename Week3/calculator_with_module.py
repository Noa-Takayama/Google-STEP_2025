# モジュール化した電卓プログラムを作ってみた!
# モジュール化しているとしていないとで, どのくらいわかりやすいかな？？

def readNumber(line, index): # 数字を読み取る関数
    number = 0
    while index < len(line) and line[index].isdigit():
        number = number * 10 + int(line[index])
        index += 1
    if line[index] == '.':
        (decimal, index) = readDecimal(line, index + 1)
        number += decimal
    token = {'type': 'NUMBER', 'number': number}
    return token, index

def readDecimal(line, index): # 小数部分を読み取る関数
    number = 0
    decimal = 0.1
    while index < len(line) and line[index].isdigit():
        number += int(line[index]) * decimal
        decimal *= 0.1
        index += 1
    return number, index

def readPlus(line, index):
    token = {'type': 'PLUS'}
    return token, index + 1

def readMinus(line, index):
    token = {'type': 'MINUS'}
    return token, index + 1

def tokenize(line): # 字句に分解する関数
    tokens = []
    index = 0
    while index < len(line):
        if line[index].isdigit():
            (token, index) = readNumber(line, index)
        elif line[index] == '+':
            (token, index) = readPlus(line, index)
        elif line[index] == '-':
            (token, index) = readMinus(line, index)
        else:
            print('Invalid character found: ' + line[index])
            exit(1)
        tokens.append(token)
    return tokens

def evaluate(tokens): # 字句の並びを計算
    answer = 0
    tokens.insert(0, {'type': 'PLUS'})  # Insert a dummy '+' token
    index = 1
    while index < len(tokens):
        if tokens[index]['type'] == 'NUMBER':
            if tokens[index - 1]['type'] == 'PLUS':
                answer += tokens[index]['number']
            if tokens[index - 1]['type'] == 'MINUS':
                answer -= tokens[index]['number']
            else:
                print('Invalid syntax')
        index += 1
    return answer

while True:
    line = input()
    tokens = tokenize(line)
    answer = evaluate(tokens)
    print("answer = %d\n" % answer) # # 出力は整数にしておく
