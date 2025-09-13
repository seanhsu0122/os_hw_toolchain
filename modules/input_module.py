# modules/input_module.py

def get_question():
    question = input("請輸入你的問題：\n")
    return question

# # 可選：從檔案讀取
# def get_question_from_file(file_path):
#     with open(file_path, "r", encoding="utf-8") as f:
#         return f.read().strip()
