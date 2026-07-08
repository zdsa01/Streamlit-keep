# 🚀 Streamlit App Auto-Waker (Streamlit 自动唤醒工具)

Streamlit Community Cloud 部署的应用在一段时间无访问后会自动进入休眠状态。本项目利用 Python + Selenium 模拟真实用户访问，自动点击唤醒按钮，并结合 GitHub Actions 实现定时无人值守运行。同时集成 Telegram 机器人，实时推送唤醒结果。

## ✨ 核心特性

- **🤖 自动化唤醒**: 自动识别并点击休眠页面的 "Yes, get this app back up!" 按钮。
- **🛡️ 深度穿透探测**: 支持主页面及嵌套 Iframe 深度扫描，结合 Selenium 定位与原生 JS 强力触发。
- **☁️ 云端免运维**: 完美适配 GitHub Actions 无头浏览器 (Headless Chrome) 环境。
- **⏰ 多触发机制**: 支持定时任务 (Cron)、手动触发 (Workflow Dispatch) 以及 Webhook 联动 (Repository Dispatch，如 Uptime Kuma)。
- **📩 实时消息通知**: 执行成功或遇到异常时，自动通过 Telegram 发送图文并茂的通知。

---

## 📂 目录结构

建议的项目目录结构如下：

```text
.
├── .github/
│   └── workflows/
│       └── wakeup.yml          # GitHub Actions 工作流配置文件
├── keep/
│   ├── streamlit-keep.py       # 核心唤醒脚本
│   └── requirements.txt        # Python 依赖包清单
└── README.md

```

*(注：`keep/requirements.txt` 中需包含 `selenium` 和 `requests`)*

---

## ⚙️ 环境变量与配置

无论是本地运行还是在 GitHub Actions 中运行，都需要配置以下环境变量：

| 变量名 | 必填 | 说明 | 示例 |
| --- | --- | --- | --- |
| `STREAMLIT_APP_URL` | **是** | 您的 Streamlit 应用完整地址 | `https://your-app.streamlit.app` |
| `TELEGRAM_BOT_TOKEN` | 否* | Telegram 机器人 Token (通过 @BotFather 获取) | `123456789:ABCdefGhIJKlmNo...` |
| `TELEGRAM_CHAT_ID` | 否* | 接收通知的用户或群组 ID (通过 @userinfobot 获取) | `123456789` |

**注：如果不配置 Telegram 相关变量，脚本将正常执行唤醒流程，但会静默跳过通知发送。*

---

## 🛠️ 如何在 GitHub Actions 中使用

本项目已配置好自动化的 CI/CD 流程，您只需在 GitHub 仓库中配置相应的 Secrets 即可。

1. 进入您的 GitHub 仓库，点击顶部的 **Settings**。
2. 在左侧菜单栏选择 **Secrets and variables** -> **Actions**。
3. 点击绿色的 **New repository secret** 按钮，依次添加以下三个 Secret：
* `STREAMLIT_APP_URL`
* `TELEGRAM_BOT_TOKEN`
* `TELEGRAM_CHAT_ID`


4. 切换到仓库的 **Actions** 标签页，在左侧选择 **Streamlit 自动唤醒** 工作流。
5. 点击 **Run workflow** 即可手动测试唤醒功能。

### 触发规则说明

* **定时触发**: 默认每 6 小时（UTC 0, 6, 12, 18 点）自动执行一次。
* **手动触发**: 支持在 Actions 页面手动点击运行。
* **API 触发**: 支持接收外部 `repository_dispatch` 事件（类型为 `service-down-alert`），完美对接 Uptime Kuma 等监控服务。

---

## 💻 本地测试与运行

如果您希望在本地测试脚本：

1. **克隆代码并进入目录**:
```bash
git clone <your-repo-url>
cd <your-repo-directory>

```


2. **安装依赖**:
```bash
pip install -r keep/requirements.txt

```


3. **设置环境变量** (以 Linux/macOS 为例):
```bash
export STREAMLIT_APP_URL="[https://your-app.streamlit.app](https://your-app.streamlit.app)"
export TELEGRAM_BOT_TOKEN="你的_BOT_TOKEN"
export TELEGRAM_CHAT_ID="你的_CHAT_ID"

```


*(Windows 用户请使用 `set` 或 `$env:` 命令)*
4. **运行脚本**:
```bash
python keep/streamlit-keep.py

```



---

## 📝 运行日志示例

```text
[INFO] ⚙️ 正在初始化浏览器配置...
[INFO] ✅ 浏览器驱动就绪
[INFO] 🌐 正在访问目标地址: [https://your-app.streamlit.app](https://your-app.streamlit.app)
[INFO] ⏳ 等待页面初步渲染 (15s)...
[INFO] 🔍 正在 [主页面] 搜索唤醒按钮...
[INFO] 🎯 命中按钮，执行点击...
[INFO] ⏳ 点击已触发，预留后端响应时间 (10s)...
[INFO] 🩺 正在验证唤醒结果...
[INFO] ✨ 验证通过 (第 1 次尝试确认)
[INFO] 🩺 正在刷新页面进行最终验证...
[INFO] 🚀 任务结束: ✅ 唤醒流程执行完毕，应用已恢复
[INFO] 📩 Telegram 通知发送成功
[INFO] 🧹 浏览器会话已安全关闭

```

## 📄 许可证

MIT License

