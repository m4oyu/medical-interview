import logging
import os

# ログディレクトリが存在しない場合は作成
log_directory = "./logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# ログファイルのパス
log_file = os.path.join(log_directory, "application.log")
debug_file = os.path.join(log_directory, "debug.log")

# ロガーを取得
logger = logging.getLogger("MyAppLogger")
logger.setLevel(logging.DEBUG)  # ロガーの最低レベルをDEBUGに設定

# INFOレベル以上のログをファイルに出力するハンドラ
file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter("%(message)s"))

# DEBUGレベル以上のログをファイルに出力するハンドラ
debug_handler = logging.FileHandler(debug_file, mode="a", encoding="utf-8")
debug_handler.setLevel(logging.DEBUG)
debug_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)

# コンソールにログを出力するハンドラ
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("%(message)s"))

# ハンドラをロガーに追加
logger.addHandler(file_handler)
logger.addHandler(debug_handler)
logger.addHandler(console_handler)

# 特定のライブラリのDEBUGログを無効にする
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
