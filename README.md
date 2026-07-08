1. 核心运行变量
STREAMLIT_APP_URL (必须)

代码位置: APP_URL = os.environ.get("STREAMLIT_APP_URL", "")

作用: 你的 Streamlit 应用的完整网址（例如：https://your-app.streamlit.app）。

检查结果: 如果未配置，脚本会在执行 wakeup_app 时直接抛出异常 Exception("未检测到 STREAMLIT_APP_URL 环境变量") 并退出。

2. Telegram 通知变量
TELEGRAM_BOT_TOKEN (通知功能必须)

代码位置: bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")

作用: Telegram Bot 的鉴权令牌。

检查结果: 如果未配置，脚本不会报错，但会打印日志 🔕 未配置 Telegram Token 或 Chat ID，跳过发送通知。，并跳过通知步骤。

TELEGRAM_CHAT_ID (通知功能必须)

代码位置: chat_id = os.environ.get("TELEGRAM_CHAT_ID")

作用: 接收通知的个人或群组的会话 ID。

检查结果: 同上，缺失时会静默跳过通知发送。
