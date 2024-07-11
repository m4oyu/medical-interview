import logging
import os

# ログディレクトリが存在しない場合は作成
log_directory = "./logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# ログファイルのパス
log_file = os.path.join(log_directory, "application.log")

# ログ設定
logging.basicConfig(
    level=logging.INFO,  # ログレベルを設定 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(message)s",  # ログフォーマットを設定
    handlers=[
        logging.FileHandler(
            log_file, mode="a", encoding="utf-8"
        ),  # ファイルにログを出力 (追記モード)
        logging.StreamHandler(),  # コンソールにもログを出力
    ],
)


# Debug mode
# logging.basicConfig(
#     level=logging.DEBUG,  # ログレベルを設定 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # ログフォーマットを設定
#     handlers=[
#         logging.FileHandler(
#             log_file, mode="a", encoding="utf-8"
#         ),  # ファイルにログを出力 (追記モード)
#         logging.StreamHandler(),  # コンソールにもログを出力
#     ],
# )

# ロガーを取得
logger = logging.getLogger("MyAppLogger")

# 特定のライブラリのDEBUGログを無効にする
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
