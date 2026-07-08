import os
import time
import logging
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# 配置日志
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class StreamlitAppWaker:
    """针对 Streamlit 应用的自动唤醒工具"""
    
    APP_URL = os.environ.get("STREAMLIT_APP_URL", "")
    INITIAL_WAIT_TIME = 15  # 初始等待，确保页面结构稳定
    CLICK_WAIT_TIME = 10  # 点击后的硬等待，确保异步请求完成
    
    # 定位器
    TEST_ID_SELECTOR = "button[data-testid='wakeup-button-owner']"
    ROBUST_XPATH = "//button[contains(., 'Yes') and contains(., 'app back up')]"

    def __init__(self):
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        logger.info("⚙️ 正在初始化浏览器配置...")
        chrome_options = Options()
        chrome_options.page_load_strategy = 'eager'
        if os.getenv('GITHUB_ACTIONS'):
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logger.info("✅ 浏览器驱动就绪")
        except Exception as e:
            logger.error(f"❌ 驱动初始化失败: {str(e)}")
            raise

    def send_telegram_notify(self, status: str, message: str):
        """发送 Telegram 通知"""
        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        
        if not bot_token or not chat_id:
            logger.info("🔕 未配置 Telegram Token 或 Chat ID，跳过发送通知。")
            return

        # 提取域名作为应用标识，让通知更直观
        app_name = self.APP_URL.split("//")[-1].split("/")[0] if self.APP_URL else "未知应用"
        
        text = (
            f"{status}\n"
            f"<b>应用:</b> <code>{app_name}</code>\n"
            f"<b>详情:</b> {message}"
        )
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("📩 Telegram 通知发送成功")
        except Exception as e:
            logger.error(f"⚠️ Telegram 通知发送失败: {str(e)}")

    def find_and_click_button(self, context="主页面"):
        """核心逻辑：结合 Selenium 定位与 JS 深度扫描"""
        logger.info(f"🔍 正在 [{context}] 搜索唤醒按钮...")
        
        button = None
        # 1. 尝试 Selenium 标准定位
        try:
            button = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.TEST_ID_SELECTOR))
            )
        except:
            try:
                button = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, self.ROBUST_XPATH))
                )
            except:
                button = None

        # 2. 如果标准定位找到，执行点击流程
        if button:
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                time.sleep(2) 
                logger.info(f"🎯 命中按钮，执行点击...")
                try:
                    button.click()
                except:
                    self.driver.execute_script("arguments[0].click();", button)
                
                logger.info(f"⏳ 点击已触发，预留后端响应时间 ({self.CLICK_WAIT_TIME}s)...")
                time.sleep(self.CLICK_WAIT_TIME)
                return True
            except Exception as e:
                logger.warning(f"⚠️ 点击尝试失败: {str(e)}")

        # 3. 如果没找到或点击失败，尝试 JS 扫描并直接在 JS 中点击
        js_logic = """
        var btn = document.querySelector("button[data-testid='wakeup-button-owner']");
        if(!btn) {
            btn = Array.from(document.querySelectorAll('button')).find(b => 
                b.innerText.includes('Yes') && b.innerText.includes('app')
            );
        }
        if(btn) {
            btn.click();
            return true;
        }
        return false;
        """
        if self.driver.execute_script(js_logic):
            logger.info(f"⚡ JS 扫描成功触发点击")
            time.sleep(self.CLICK_WAIT_TIME)
            return True
        
        return False

    def check_app_status(self):
        """双重验证：检查按钮消失且应用容器出现"""
        logger.info("🩺 正在验证唤醒结果...")
        
        def is_app_running():
            try:
                selectors = ["[data-testid='stAppViewContainer']", "[data-testid='stSidebar']"]
                for selector in selectors:
                    if len(self.driver.find_elements(By.CSS_SELECTOR, selector)) > 0:
                        return True
            except: return False
            return False
        
        def is_button_gone():
            self.driver.switch_to.default_content()
            btns = self.driver.find_elements(By.CSS_SELECTOR, self.TEST_ID_SELECTOR)
            return len(btns) == 0

        for attempt in range(1, 4):
            # 按钮消失或容器出现均视为成功
            if is_button_gone() or is_app_running():
                logger.info(f"✨ 验证通过 (第 {attempt} 次尝试确认)")
                return True
            time.sleep(3)
        return False

    def wakeup_app(self):
        if not self.APP_URL:
            raise Exception("未检测到 STREAMLIT_APP_URL 环境变量")
        
        logger.info(f"🌐 正在访问目标地址: {self.APP_URL}")
        self.driver.get(self.APP_URL)
        logger.info(f"⏳ 等待页面初步渲染 ({self.INITIAL_WAIT_TIME}s)...")
        time.sleep(self.INITIAL_WAIT_TIME)

        # 尝试主页面
        clicked = self.find_and_click_button("主页面")
        
        # 如果主页面没点到，尝试 Iframe
        if not clicked:
            logger.info("📂 主页面未找到按钮，开始探测嵌套 Iframe...")
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            logger.info(f"🔍 检测到 {len(iframes)} 个 iframe")
            
            for i, frame in enumerate(iframes):
                try:
                    self.driver.switch_to.frame(frame)
                    if self.find_and_click_button(f"Iframe #{i}"):
                        clicked = True
                        break
                finally:
                    self.driver.switch_to.default_content()

        # 无论是否点到，如果页面已经是运行状态，直接返回成功
        if not clicked:
            logger.info("🧐 未找到唤醒按钮，正在检查应用是否已在线...")
            if self.check_app_status():
                return True, "应用已是唤醒状态，无需操作"
            else:
                raise Exception("无法找到唤醒入口，且应用仍处于冷启动/睡眠状态")

        # 结果确认：刷新并深度验证
        logger.info(f"🩺 正在刷新页面进行最终验证...")
        self.driver.refresh()
        time.sleep(self.CLICK_WAIT_TIME) # 刷新后的加载时间
        
        if self.check_app_status():
            return True, "唤醒流程执行完毕，应用已恢复"
        else:
            raise Exception("唤醒动作已执行，但刷新页面后仍未检测到应用启动")

    def run(self):
        try:
            success, msg = self.wakeup_app()
            logger.info(f"🚀 任务结束: {msg}")
            # 发送成功通知
            self.send_telegram_notify("✅ <b>Streamlit 唤醒成功</b>", msg)
            return success, msg
        except Exception as e:
            error_msg = str(e)
            logger.error(f"💥 运行异常: {error_msg}")
            # 发送失败通知
            self.send_telegram_notify("❌ <b>Streamlit 唤醒失败</b>", error_msg)
            return False, error_msg
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("🧹 浏览器会话已安全关闭")

if __name__ == "__main__":
    waker = StreamlitAppWaker()
    success, _ = waker.run()
    exit(0 if success else 1)
