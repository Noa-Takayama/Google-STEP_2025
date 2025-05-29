from re import match
import sys
import bisect # 二分探索用のモジュール

def load_dictionary(dict_path):
    """
    Step1:
    辞書ファイルを読み込み, 各単語を(ソートした文字列, 素の単語) のタプルにしてリスト化し,
    ソートされた文字列でソートして返す.
    """

    new_dictionary = [] # (ソートした文字列, 元の単語) のタプルを格納する新しい辞書
    with open(dict_path) as f:
        for line in f:
            word = line.strip() # 単語の前後の空白を削除
            if word:
                key = ''.join(sorted(word)) # 単語をソートしてキーを作成
                new_dictionary.append((key, word))
        new_dictionary.sort(key=lambda x: x[0]) # ソートした文字列でソート
    return new_dictionary

def find_anagrams(word,dictionary):
    """
    Step2:
    二分探索で, new_dictionary から与えられた単語のアナグラムを探す.
    見つかれば元の単語 word をかえし, 見つからなければ Not Found を返す.
    """

    sorted_word = ''.join(sorted(word)) # 単語をソートしてキーを作成
    # 辞書からアナグラムを探す
    i = bisect.bisect_left(dictionary, (sorted_word, '')) # ソートした文字列で二分探索
    
    if i < len(dictionary) and dictionary[i][0] == sorted_word:
        return dictionary[i][1] # アナグラムが見つかった場合は元の単語を返す
    else:
        return None
    
def main():
    if len(sys.argv) != 3:
        print("Usage: python kadai01.py <dictionary_file> <test_word_file1")
        sys.exit(1)
    dict_path = sys.argv[1] # 辞書ファイルのパス
    input_path = sys.argv[2] # テスト用の単語ファイルのパス

    # 辞書を読み込んでソート済み new_dictionary を作成
    new_dictionary = load_dictionary(dict_path)

    # 入力ファイルを一行ずつ処理
    with open(input_path) as f:
        for raw in f:
            word = raw.strip()
            if not word:
                continue # 空行はスキップ
            # アナグラムを探して結果を出力
            sorted_word = ''.join(sorted(word)) # ソートした文字列を作成
            result = find_anagrams(word, new_dictionary)
            if result is not None:
                print(result)
            else:
                print("Not Found")

if __name__ == "__main__":
    main()