# モジュールなしで計算機を作ってみた
while True:
    line = input() 
    answer = 0.0  # float で初期化しておく
    index = 0     # 文字列のどの位置を読んでいるかを示すポインタ
    # +とか-とか保存しておく変数があると良さそう
    is_plus = True

    while index < len(line):
        # 整数部分の読み取り
        if line[index].isdigit():  # インデックス部分が数字だったらifの中に入る
            number = 0
            while index < len(line) and line[index].isdigit():  # 小数点 '.' が来るまで
                number = number * 10 + int(line[index])
                index += 1

            # 小数部分の読み取り
            if index < len(line) and line[index] == '.':  # 小数点 '.' が来たら
                index += 1
                decimal_point = 0.1  # 小数点 を導入する
                while index < len(line) and line[index].isdigit():  # 別の演算子が来るまで回す
                    number += int(line[index]) * decimal_point
                    decimal_point /= 10  # 0.01, 0.001, 0.0001,... としていく
                    index += 1

            if is_plus:
                answer += number
            else:
                answer -= number

        elif line[index] == '+':
            is_plus = True
            index += 1

        elif line[index] == '-':
            is_plus = False
            index += 1

        else:
            print('Invalid character found: ' + line[index])
            exit(1)

    print("answer = %f\n" % answer)