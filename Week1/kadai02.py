import sys
from score_checker import calculate_score

# 辞書と入力ファイルの読み込みとリスト化
def read_words(path):
    """
    Step1:
    ファイル path を開いて,
    1行ずつ strip() して空行を除外し,
    それらをリストに格納して返す関数
    """
    words = [] # 空のリストを作成
    with open(path) as  f:
        for line in f:
            line = line.strip()
            if line: # 空行を除外する
                words.append(line) # リストに追加
    # ファイルの内容をリストに格納して返す
    return words


# 文字列を文字カウント情報に変換する関数
# 例えば "hello" を受け取ったら {'h': 1, 'e': 1, 'l': 2, 'o': 1} を返す

def count_letters(word):
    """
    Step2:
    word の各文字をカウントし,
    [count('a'), count('b'), ..., count('z')] の形のリストを返す.
    """
    table = [0] * 26 # 26文字のアルファベットのカウント用リストを作成
    for c in word:
        idx = ord(c) - ord('a') # 'a' を 0, 'b' を 1, ..., 'z' を 25 に変換
        table[idx] += 1
    return table # カウント情報を渡す
# 今回大文字はこないので考慮しなくて大丈夫

# words.txt の単語リストに対し,
# 文字ごとのカウント (count_letters),
# その単語のスコア calculate_score) を予め計算しておき,
# [(word, count_letters(word), calculate_score(word))] の形のリストを返す関数

def modificated_dictionary(words):
    """
    Step3:
    words の各単語に対して count_letters と calculate_score を適用し,
    (単語, 文字カウント情報, スコア) のタプルのリストを返す.
    """
    entries = [] # 空のリストを作成
    for w in words:
        count = count_letters(w)
        score = calculate_score(w)
        entries.append((w, count, score))
    return entries # (単語, 文字カウント情報, スコア) のリストを返す

# ここまでが辞書の読み込みと前処理!!

# 次に, 入力文字列ファイルの文字列に対して,
# 辞書の単語が作れるかどうかを判定する関数

def judge_anagram(data_count, word_count):
    # data_count は入力文字列の文字カウント
    # word_count は辞書の単語の文字カウント

    for i in range(26):
        if word_count[i] > data_count[i]:
            return False
    return True
# 辞書の単語の文字カウントより入力文字列の文字カウントが
# 越えなければ True を返す

# これで入力文字列の文字から, 辞書内の単語が作れるかどうかが分かるようになった！

# 最後は, 辞書全体から作れる単語の中で最大スコアの単語を探す関数を作成

def find_max_score(data_count, dict_entries):
    """
    Step4:
    data_count を使って, dict_entries の中から作れる
    単語の中で最大スコアの単語を探す.
    """
    best_word = None
    best_score = 0
    for w, count, score in dict_entries:
        if judge_anagram(data_count, count) and score > best_score:
            best_score = score
            best_word = w
    return best_word
    
def main(data_file, answer_file):
    # 1) 辞書を読み込んで前処理
    valid_words  = read_words("words.txt")
    dict_entries = modificated_dictionary(valid_words)

    # 2) 入力ファイルを読み込み
    data_lines = read_words(data_file)

    # 3) 各行について最高スコア単語を探し、リスト化
    results = []
    for line in data_lines:
        data_count = count_letters(line)
        best = find_max_score(data_count, dict_entries)
        # 見つからなければ空行。それ以外は単語を書き出し
        results.append(best if best is not None else "")

    # 4) 出力ファイルに書き出し
    with open(answer_file, "w") as f:
        for w in results:
            f.write(w + "\n")

    print(f"-> Wrote {len(results)} answers to '{answer_file}'")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input_file> <output_file>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
