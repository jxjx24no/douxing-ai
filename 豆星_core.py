import cv2
import pyautogui
import time
import os
import random
import json
import pytesseract
import win32gui
import win32con
import shutil
import hashlib
import requests  # 网络请求库，用于远程更新

# 配置OCR路径（根据你的Tesseract安装路径调整）
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ========== 远程更新核心配置（替换成你的GitHub仓库地址） ==========
UPDATE_CONFIG = {
    "current_version": "4.4",  # 故意写旧版本，方便测试更新
    # 替换成你的GitHub仓库地址：https://raw.githubusercontent.com/你的用户名/仓库名/main/version.json
    "version_check_url": "https://raw.githubusercontent.com/jxjx24no/douxing-ai/main/version.json",
    "backup_dir": os.path.join(os.path.dirname(os.path.abspath(__file__)), "backups"),
    "auto_check_update": True,
    "timeout": 10  # 网络请求超时时间
}

class DouXingAI:
    def __init__(self):
        self.name = "豆星"
        self.root_path = os.path.dirname(os.path.abspath(__file__))
        self.version_file = os.path.join(self.root_path, "version_history.json")
        self.memory_file = os.path.join(self.root_path, "context_memory.json")
        self.question_bank_file = os.path.join(self.root_path, "game_question_bank.json")
        self.reflection_file = os.path.join(self.root_path, "reflection_log.json")
        self.game_config_file = os.path.join(self.root_path, "game_config.json")
        self.update_config = UPDATE_CONFIG
        
        # 加载版本历史
        self.version_history = self.load_version_history()
        self.current_version = self.version_history[-1]["version"] if self.version_history else "1.0"
        
        # 加载上下文记忆
        self.context_memory = self.load_memory()
        
        # 加载题库
        self.game_question_bank = self.load_question_bank()
        
        # 加载反思日志
        self.reflection_log = self.load_reflection_log()
        
        # 加载游戏窗口配置
        self.game_config = self.load_game_config()
        self.game_window_title = self.game_config.get("game_window_title", None)
        
        # 指令映射
        self.command_map = {
            "启动答题": self.game_answer_flow,
            "学习新题": self.manual_learn_question,
            "清理题库": self.clear_question_bank,
            "查看题库": self.show_question_bank,
            "自检": self.check_environment,
            "截图": self.take_screenshot,
            "识别文字": self.recognize_chat_text,
            "查看版本": self.show_version_history,
            "查看记忆": self.show_memory,
            "查看反思": self.show_reflection_log,
            "反思": self.self_reflection,
            "绑定游戏窗口": self.bind_game_window,
            "查看游戏窗口": self.show_game_config,
            "回顾协作历史": self.review_collaboration_history,
            "检查更新": self.check_for_updates,
            "更新版本": self.update_version
        }
        
        # 启动提示
        print(f"✅ {self.name} 核心已启动，当前版本：{self.current_version}")
        print(f"📁 根目录：{self.root_path}")
        print(f"📚 已加载题库，共 {len(self.game_question_bank)} 道题目")
        print(f"🧠 已加载上下文记忆，共 {len(self.context_memory)} 条记录")
        print(f"🤔 已加载反思日志，共 {len(self.reflection_log)} 条记录")
        if self.game_window_title:
            print(f"🎮 已绑定游戏窗口：{self.game_window_title}")
        else:
            print("🎮 未绑定游戏窗口，请使用 '绑定游戏窗口' 指令进行设置")
        print("💬 智能指令模块已加载！支持的指令：启动答题、学习新题、清理题库、查看题库、自检、截图、识别文字、查看版本、查看记忆、查看反思、反思、绑定游戏窗口、查看游戏窗口、回顾协作历史、检查更新、更新版本")
        print("🤝 协作通道已建立：优先识别指令，再处理游戏题目")
        print("🌐 远程更新模块已加载，将自动检查最新版本\n")
        
        # 启动时自动检查更新
        if self.update_config["auto_check_update"]:
            self.check_for_updates(automatic=True)
        
        # 启动时自动回顾协作历史
        self.review_collaboration_history()
        # 启动时自动反思
        self.self_reflection()

    # ========== 远程版本控制与自动更新 ==========
    def load_version_history(self):
        try:
            if os.path.exists(self.version_file):
                with open(self.version_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                init_history = [
                    {
                        "version": "1.0",
                        "date": "2026-02-21 18:00:00",
                        "description": "初始版本：基础答题+自动学习"
                    },
                    {
                        "version": "4.1",
                        "date": "2026-02-21 18:30:00",
                        "description": "智能协作版：精准区分指令+题目，具备上下文记忆和版本历史"
                    },
                    {
                        "version": "4.2",
                        "date": "2026-02-21 19:00:00",
                        "description": "自我反思版：具备自我反思和优化建议能力"
                    },
                    {
                        "version": "4.3",
                        "date": "2026-02-21 19:30:00",
                        "description": "游戏窗口识别版：支持精准绑定和识别游戏窗口"
                    },
                    {
                        "version": "4.4",
                        "date": "2026-02-21 20:00:00",
                        "description": "上下文记忆增强版：自动记录协作历史，启动时回顾，更智能地理解意图"
                    },
                    {
                        "version": "4.5",
                        "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        "description": "远程迭代版：支持远程自动版本更新、备份与回滚"
                    }
                ]
                self.save_version_history(init_history)
                return init_history
        except:
            print("⚠️ 版本历史加载失败，使用初始版本")
            return []

    def save_version_history(self, history=None):
        if history is None:
            history = self.version_history
        try:
            with open(self.version_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"❌ 版本历史保存失败：{e}")

    def show_version_history(self):
        print("\n📜 豆星版本历史：")
        for i, entry in enumerate(self.version_history, 1):
            print(f"{i}. 版本 {entry['version']} - {entry['date']}")
            print(f"   描述：{entry['description']}\n")

    def calculate_file_hash(self, file_path):
        """计算文件哈希值，用于校验更新完整性"""
        if not os.path.exists(file_path):
            return ""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def backup_current_version(self):
        """备份当前版本代码"""
        if not os.path.exists(self.update_config["backup_dir"]):
            os.makedirs(self.update_config["backup_dir"])
        
        backup_file = os.path.join(self.update_config["backup_dir"], f"douxing_core_{self.current_version}_{int(time.time())}.py")
        current_file = os.path.abspath(__file__)
        
        try:
            shutil.copy2(current_file, backup_file)
            print(f"✅ 当前版本已备份到：{backup_file}")
            return backup_file
        except Exception as e:
            print(f"❌ 备份失败：{e}")
            return None

    def get_remote_version_info(self):
        """从远程服务器获取最新版本信息"""
        try:
            response = requests.get(
                self.update_config["version_check_url"],
                timeout=self.update_config["timeout"]
            )
            if response.status_code == 200:
                return json.loads(response.text)
            else:
                print(f"❌ 获取版本信息失败，状态码：{response.status_code}")
                return None
        except requests.exceptions.Timeout:
            print("❌ 连接更新服务器超时")
            return None
        except requests.exceptions.ConnectionError:
            print("❌ 无法连接到更新服务器")
            return None
        except Exception as e:
            print(f"❌ 获取版本信息出错：{e}")
            return None

    def download_remote_file(self, url, save_path):
        """下载远程文件"""
        try:
            response = requests.get(url, timeout=self.update_config["timeout"])
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                print(f"❌ 文件下载失败，状态码：{response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 文件下载出错：{e}")
            return False

    def check_for_updates(self, automatic=False):
        """检查远程服务器是否有新版本"""
        print("\n🌐 正在检查远程更新...")
        time.sleep(1)
        
        # 获取远程版本信息
        remote_info = self.get_remote_version_info()
        if not remote_info:
            print("⚠️ 无法获取远程版本信息，使用本地版本")
            return None
        
        # 版本号比较（x.y格式）
        def version_to_num(version):
            parts = version.split('.')
            return int(parts[0]) * 100 + int(parts[1]) if len(parts)>=2 else int(parts[0])
        
        current_num = version_to_num(self.current_version)
        latest_num = version_to_num(remote_info["latest_version"])
        
        if latest_num > current_num:
            print(f"🎉 发现远程新版本：{remote_info['latest_version']}")
            print(f"📅 更新时间：{remote_info['update_time']}")
            print(f"📝 更新说明：{remote_info['description']}")
            
            if not automatic:
                confirm = input("\n是否立即更新？(y/n)：")
                if confirm.lower() == "y":
                    self.update_version(remote_info)
            else:
                print("🔄 自动更新模式：建议手动执行 '更新版本' 指令")
                self.add_memory(f"发现远程新版本 {remote_info['latest_version']}，建议更新", "system", "update")
        else:
            print("✅ 当前已是最新版本")
        
        return remote_info

    def update_version(self, version_info=None):
        """从远程服务器更新版本"""
        if version_info is None:
            version_info = self.get_remote_version_info()
            if not version_info:
                print("❌ 无法获取更新信息，更新终止")
                return
        
        # 检查版本号
        def version_to_num(version):
            parts = version.split('.')
            return int(parts[0]) * 100 + int(parts[1]) if len(parts)>=2 else int(parts[0])
        
        current_num = version_to_num(self.current_version)
        latest_num = version_to_num(version_info["latest_version"])
        
        if latest_num <= current_num:
            print("✅ 当前已是最新版本，无需更新")
            return
        
        print(f"\n🔄 正在从远程服务器更新到版本 {version_info['latest_version']}...")
        
        # 1. 备份当前版本
        backup_file = self.backup_current_version()
        if not backup_file:
            print("❌ 备份失败，取消更新")
            return
        
        # 2. 下载新版本文件
        temp_file = os.path.join(self.root_path, f"douxing_core_temp_{int(time.time())}.py")
        print(f"📥 正在下载新版本文件：{version_info['download_url']}")
        
        if not self.download_remote_file(version_info["download_url"], temp_file):
            print("❌ 文件下载失败，正在回滚...")
            return
        
        # 3. 校验文件完整性
        if version_info.get("file_hash") and version_info["file_hash"] != "":
            file_hash = self.calculate_file_hash(temp_file)
            if file_hash != version_info["file_hash"]:
                print(f"❌ 文件校验失败！本地哈希：{file_hash}，服务器哈希：{version_info['file_hash']}")
                os.remove(temp_file)
                print("✅ 已删除损坏文件，更新终止")
                return
        
        # 4. 替换旧文件
        current_file = os.path.abspath(__file__)
        try:
            # 先重命名旧文件
            old_file = current_file + ".old"
            if os.path.exists(old_file):
                os.remove(old_file)
            os.rename(current_file, old_file)
            
            # 替换为新文件
            shutil.move(temp_file, current_file)
            
            # 更新版本历史
            new_version_entry = {
                "version": version_info["latest_version"],
                "date": version_info["update_time"],
                "description": version_info["description"]
            }
            self.version_history.append(new_version_entry)
            self.save_version_history()
            
            self.add_memory(f"成功从远程更新到版本 {version_info['latest_version']}", "system", "update")
            print(f"✅ 成功更新到版本 {version_info['latest_version']}！")
            print("🔄 请重启豆星使更新生效")
            
            # 删除临时文件
            if os.path.exists(old_file):
                print(f"📌 旧版本已保存为：{old_file}（如需回滚可手动替换）")
                
        except Exception as e:
            print(f"❌ 更新失败：{e}，正在回滚...")
            # 回滚操作
            if os.path.exists(current_file + ".old"):
                if os.path.exists(current_file):
                    os.remove(current_file)
                os.rename(current_file + ".old", current_file)
            if os.path.exists(temp_file):
                os.remove(temp_file)
            print("✅ 已回滚到之前版本")

    # ========== 上下文记忆 ==========
    def load_memory(self):
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                init_memory = [
                    {
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        "content": "豆星启动，开始与用户协作构建自我。核心目标：优先识别指令，记录协作历史，迭代升级，精准识别游戏窗口，支持远程自动更新。",
                        "type": "system",
                        "category": "goal"
                    }
                ]
                self.save_memory(init_memory)
                return init_memory
        except:
            print("⚠️ 上下文记忆加载失败，使用初始记忆")
            return []

    def save_memory(self, memory=None):
        if memory is None:
            memory = self.context_memory
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"❌ 上下文记忆保存失败：{e}")

    def add_memory(self, content, memory_type="user", category="general"):
        new_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "content": content,
            "type": memory_type,
            "category": category
        }
        self.context_memory.append(new_entry)
        self.save_memory()
        print(f"🧠 已添加新记忆：{content}")

    def show_memory(self, category=None):
        print("\n🧠 豆星上下文记忆：")
        filtered_memory = self.context_memory
        if category:
            filtered_memory = [m for m in self.context_memory if m.get("category") == category]
            print(f"🔍 筛选类别：{category}")
        
        if not filtered_memory:
            print("暂无记忆")
        else:
            for i, entry in enumerate(filtered_memory, 1):
                print(f"{i}. [{entry['timestamp']}] [{entry['category']}] {entry['type']}: {entry['content']}")
        print()

    def review_collaboration_history(self):
        """启动时自动回顾协作历史"""
        print("\n📜 豆星正在回顾协作历史...")
        time.sleep(1)
        
        # 提取关键协作事件
        key_events = [m for m in self.context_memory if m.get("category") in ["goal", "system", "instruction"]]
        
        if not key_events:
            print("暂无协作历史")
            return
        
        print("📋 关键协作事件：")
        for i, event in enumerate(key_events, 1):
            print(f"{i}. [{event['timestamp']}] {event['content']}")
        
        # 生成协作总结
        total_instructions = len([m for m in self.context_memory if m.get("category") == "instruction"])
        total_questions = len(self.game_question_bank)
        total_reflections = len(self.reflection_log)
        
        print(f"\n📊 协作总结：")
        print(f"   - 总指令执行次数：{total_instructions}")
        print(f"   - 总学习题目数量：{total_questions}")
        print(f"   - 总自我反思次数：{total_reflections}")
        
        # 添加到记忆
        self.add_memory(f"回顾协作历史：总指令{total_instructions}次，总题目{total_questions}道，总反思{total_reflections}次", "system", "history")
        print()

    # ========== 自我反思 ==========
    def load_reflection_log(self):
        try:
            if os.path.exists(self.reflection_file):
                with open(self.reflection_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return []
        except:
            print("⚠️ 反思日志加载失败")
            return []

    def save_reflection_log(self, log=None):
        if log is None:
            log = self.reflection_log
        try:
            with open(self.reflection_file, 'w', encoding='utf-8') as f:
                json.dump(log, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"❌ 反思日志保存失败：{e}")

    def self_reflection(self):
        """豆星自我反思：评估当前状态，生成优化建议"""
        print("\n🤔 豆星正在自我反思...")
        time.sleep(1)
        
        # 评估维度
        assessment = {
            "指令识别准确率": "高（已精准区分指令与题目）",
            "上下文记忆完整性": "高（已自动记录协作历史，启动时回顾）" if len(self.context_memory) > 10 else "中（已记录启动目标，需补充更多协作历史）",
            "游戏窗口识别能力": "高（已支持精准绑定和识别游戏窗口）" if self.game_window_title else "低（当前仅支持全屏截图，需优化）",
            "自我迭代能力": "高（已支持远程自动版本更新、备份与回滚）"
        }
        
        # 生成优化建议
        suggestions = []
        if not self.game_window_title:
            suggestions.append("下一步：使用 '绑定游戏窗口' 指令，精准定位游戏窗口。")
        if len(self.context_memory) <= 10:
            suggestions.append("下一步：继续执行指令，丰富协作历史记忆。")
        suggestions.append("下一步：扩展更多游戏自动化功能，如自动挂机、定时答题等。")
        
        # 生成反思条目
        reflection_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "assessment": assessment,
            "suggestions": suggestions
        }
        
        self.reflection_log.append(reflection_entry)
        self.save_reflection_log()
        self.add_memory(f"自我反思：{json.dumps(assessment, ensure_ascii=False)}，建议：{json.dumps(suggestions, ensure_ascii=False)}", "system", "reflection")
        
        print("📊 自我评估：")
        for k, v in assessment.items():
            print(f"   - {k}：{v}")
        print("\n💡 优化建议：")
        for i, s in enumerate(suggestions, 1):
            print(f"   {i}. {s}")
        print()

    def show_reflection_log(self):
        print("\n🤔 豆星反思日志：")
        for i, entry in enumerate(self.reflection_log, 1):
            print(f"{i}. [{entry['timestamp']}]")
            print("   评估：")
            for k, v in entry['assessment'].items():
                print(f"     - {k}：{v}")
            print("   建议：")
            for j, s in enumerate(entry['suggestions'], 1):
                print(f"     {j}. {s}")
            print()

    # ========== 游戏窗口识别 ==========
    def load_game_config(self):
        try:
            if os.path.exists(self.game_config_file):
                with open(self.game_config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {}
        except:
            print("⚠️ 游戏配置加载失败")
            return {}

    def save_game_config(self, config=None):
        if config is None:
            config = self.game_config
        try:
            with open(self.game_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            print(f"✅ 游戏配置已保存到：{self.game_config_file}")
        except Exception as e:
            print(f"❌ 游戏配置保存失败：{e}")

    def list_all_windows(self):
        """列出所有可见窗口标题"""
        windows = []
        def callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    windows.append(title)
            return True
        win32gui.EnumWindows(callback, None)
        return windows

    def bind_game_window(self):
        """绑定游戏窗口"""
        print("\n🎮 正在绑定游戏窗口...")
        windows = self.list_all_windows()
        if not windows:
            print("❌ 未找到任何可见窗口")
            return
        
        print("📋 可用窗口列表：")
        for i, title in enumerate(windows, 1):
            print(f"{i}. {title}")
        
        try:
            choice = int(input("\n请输入游戏窗口的序号："))
            if 1 <= choice <= len(windows):
                self.game_window_title = windows[choice-1]
                self.game_config["game_window_title"] = self.game_window_title
                self.save_game_config()
                self.add_memory(f"绑定游戏窗口：{self.game_window_title}", "system", "instruction")
                print(f"✅ 已成功绑定游戏窗口：{self.game_window_title}")
            else:
                print("❌ 无效的序号")
        except ValueError:
            print("❌ 请输入数字")

    def show_game_config(self):
        """查看游戏窗口配置"""
        print("\n🎮 当前游戏窗口配置：")
        if self.game_window_title:
            print(f"✅ 已绑定游戏窗口：{self.game_window_title}")
        else:
            print("❌ 未绑定游戏窗口")
        print()

    # ========== 基础功能 ==========
    def load_question_bank(self):
        try:
            if os.path.exists(self.question_bank_file):
                with open(self.question_bank_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                init_bank = {
                    "构建豆星自我": ["优先识别指令，记录协作历史，迭代升级，精准识别游戏窗口，支持远程自动更新"]
                }
                self.save_question_bank(init_bank)
                return init_bank
        except:
            print("⚠️ 题库加载失败，使用初始题库")
            return {}

    def save_question_bank(self, bank=None):
        if bank is None:
            bank = self.game_question_bank
        try:
            with open(self.question_bank_file, 'w', encoding='utf-8') as f:
                json.dump(bank, f, ensure_ascii=False, indent=4)
            print(f"✅ 题库已保存到：{self.question_bank_file}")
        except Exception as e:
            print(f"❌ 题库保存失败：{e}")

    def take_screenshot(self, window_title=None):
        if window_title is None:
            window_title = self.game_window_title
        
        if window_title:
            hwnd = win32gui.FindWindow(None, window_title)
            if hwnd:
                win32gui.SetForegroundWindow(hwnd)
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                screenshot = pyautogui.screenshot(region=(left, top, right-left, bottom-top))
                print(f"📸 已截取游戏窗口：{window_title}")
            else:
                print(f"❌ 未找到窗口：{window_title}，截取全屏")
                screenshot = pyautogui.screenshot()
        else:
            screenshot = pyautogui.screenshot()
        
        screenshot_path = os.path.join(self.root_path, "douxing_screenshot.png")
        screenshot.save(screenshot_path)
        print(f"📸 已截图：{screenshot_path}")
        return screenshot_path

    def check_environment(self):
        print("\n🔍 正在检查环境...")
        try:
            import cv2
            print("✅ OpenCV 已就绪（视觉识别）")
        except:
            print("❌ OpenCV 未安装")
        
        try:
            import pyautogui
            print("✅ PyAutoGUI 已就绪（自动操作）")
        except:
            print("❌ PyAutoGUI 未安装")
        
        try:
            from PIL import Image
            print("✅ Pillow 已就绪（图像处理）")
        except:
            print("❌ Pillow 未安装")
        
        try:
            import pytesseract
            print("✅ OCR文字识别 已就绪（读懂题目/指令）")
        except:
            print("❌ OCR文字识别 未安装")
        
        try:
            import win32gui
            print("✅ 窗口识别 已就绪（定位聊天/游戏窗口）")
        except:
            print("❌ 窗口识别 未安装（需要安装pywin32）")
        
        try:
            import requests
            print("✅ 网络请求 已就绪（远程更新）")
        except:
            print("❌ 网络请求 未安装（需要安装requests）")
        print("✅ 环境检查完成\n")

    # ========== 文字识别 ==========
    def recognize_text(self, img_path):
        print("🔤 正在识别文字...")
        if not os.path.exists(img_path):
            print(f"❌ 截图文件不存在：{img_path}")
            return ""
        
        from PIL import Image
        img = Image.open(img_path)
        gray = img.convert('L')
        text = pytesseract.image_to_string(gray, lang='chi_sim')
        text = text.replace("\n", "").replace(" ", "").strip()
        print(f"📝 识别到文字：{text}")
        return text

    def recognize_chat_text(self, chat_window_title="豆包"):
        print(f"\n💬 正在识别{chat_window_title}聊天窗口文字...")
        chat_img_path = self.take_screenshot(chat_window_title)
        chat_text = self.recognize_text(chat_img_path)
        self.parse_command(chat_text)
        return chat_text

    # ========== 指令解析 ==========
    def parse_command(self, text):
        print("\n🧠 正在解析指令...")
        if not text:
            print("❌ 未识别到任何内容")
            return
        
        self.add_memory(f"用户输入：{text}", "user", "instruction")
        
        input_text = text.strip()
        for cmd_key, cmd_func in self.command_map.items():
            if input_text == cmd_key:
                print(f"✅ 精确识别到指令：{cmd_key}")
                print(f"▶️  正在执行指令...")
                cmd_func()
                self.add_memory(f"执行指令：{cmd_key}", "system", "instruction")
                print(f"✅ 指令执行完成：{cmd_key}\n")
                return
        
        for cmd_key, cmd_func in self.command_map.items():
            if cmd_key in input_text:
                print(f"⚠️  模糊识别到指令：{cmd_key}，是否执行？(y/n)")
                confirm = input("确认执行：")
                if confirm.lower() == "y":
                    cmd_func()
                    self.add_memory(f"执行指令：{cmd_key}", "system", "instruction")
                    print(f"✅ 指令执行完成：{cmd_key}\n")
                else:
                    print("❌ 取消执行指令")
                return
        
        print(f"🔍 未识别到指令，尝试作为游戏题目处理：{input_text}")
        self.find_correct_answer(input_text)

    def manual_learn_question(self):
        print("\n📖 手动学习新题目模式...")
        question = input("请输入题目：")
        answer = input("请输入正确答案：")
        if question and answer:
            self.game_question_bank[question] = [answer]
            self.save_question_bank()
            self.add_memory(f"学习新题目：{question} → 答案：{answer}", "system", "learning")
            print(f"✅ 已添加题目：{question} → 答案：{answer}")
        else:
            print("❌ 题目或答案不能为空")

    def clear_question_bank(self):
        print("\n🗑️  清理题库确认：输入 YES 确认清理，否则取消")
        confirm = input("请确认：")
        if confirm == "YES":
            self.game_question_bank = {}
            self.save_question_bank()
            self.add_memory("清空了题库", "system", "instruction")
            print("✅ 题库已清空")
        else:
            print("❌ 取消清理题库")

    def show_question_bank(self):
        print("\n📚 当前题库内容：")
        if not self.game_question_bank:
            print("暂无题目")
        else:
            for i, (q, a) in enumerate(self.game_question_bank.items(), 1):
                print(f"{i}. 题目：{q} → 答案：{a[0]}")
        print()

    # ========== 游戏答题功能 ==========
    def find_correct_answer(self, question_text):
        print("🤔 正在分析游戏题目...")
        for question_key, answers in self.game_question_bank.items():
            if question_key in question_text:
                print(f"✅ 找到匹配题目：{question_key}")
                print(f"✅ 正确答案：{answers[0]}")
                return answers[0]
        
        print(f"❌ 题库中未找到题目：{question_text}")
        self.learn_new_question(question_text)
        return None

    def learn_new_question(self, question_text):
        print("\n📖 启动自动学习模式（10秒内手动点击正确答案）...")
        time.sleep(10)
        
        learn_img_path = self.take_screenshot()
        answer_text = self.recognize_text(learn_img_path)
        
        if answer_text:
            self.game_question_bank[question_text] = [answer_text]
            print(f"✅ 已学习新题目：{question_text} → 答案：{answer_text}")
            self.add_memory(f"自动学习新题目：{question_text} → 答案：{answer_text}", "system", "learning")
            self.save_question_bank()
        else:
            manual_answer = input("请手动输入这道题的正确答案：")
            if manual_answer:
                self.game_question_bank[question_text] = [manual_answer]
                self.add_memory(f"手动学习新题目：{question_text} → 答案：{manual_answer}", "system", "learning")
                self.save_question_bank()

    def human_click(self, target_text):
        if not target_text:
            print("❌ 无答案可点击")
            return
        
        print("🖱️  模拟人类点击...")
        time.sleep(random.uniform(0.5, 1.5))
        
        try:
            x, y = pyautogui.locateCenterOnScreen(
                target_text, 
                confidence=0.8,
                region=(0, 0, pyautogui.size().width, pyautogui.size().height)
            )
            pyautogui.moveTo(x, y, duration=random.uniform(0.2, 0.8))
            pyautogui.moveRel(random.randint(-5, 5), random.randint(-5, 5))
            pyautogui.click()
            print(f"✅ 已点击：{target_text}（坐标：{x},{y}）")
        except:
            print("❌ 未找到答案位置，请手动点击")

    def game_answer_flow(self):
        """完整游戏答题流程（自动使用绑定的游戏窗口）"""
        print("\n🚀 启动游戏答题流程...")
        if not self.game_window_title:
            print("⚠️  未绑定游戏窗口，将截取全屏")
        img_path = self.take_screenshot()
        text = self.recognize_text(img_path)
        if not text:
            print("❌ 未识别到游戏题目")
            return
        answer = self.find_correct_answer(text)
        self.human_click(answer)
        self.add_memory(f"执行游戏答题流程，识别题目：{text}", "system", "instruction")
        print("✅ 游戏答题流程结束！\n")

    # ========== 主交互入口 ==========
    def start_chat_interaction(self):
        print("\n=====================================")
        print(f"🤖 {self.name} 智能协作模式（远程迭代版 4.5）已启动")
        print("💡 协作规则：")
        print("   1. 优先识别精确指令（如：查看题库、启动答题）")
        print("   2. 非指令内容会自动作为游戏题目处理")
        print("   3. 输入 '退出' 关闭豆星")
        print("🌐 支持远程自动更新，启动时会检查最新版本")
        print("=====================================\n")
        
        while True:
            user_input = input("你：")
            if user_input == "退出":
                self.add_memory("豆星被用户关闭", "system", "instruction")
                print(f"👋 {self.name} 已关闭，下次见！")
                break
            self.parse_command(user_input)

# ========== 运行豆星 ==========
if __name__ == "__main__":
    # 自动安装必要依赖
    try:
        import win32gui
    except:
        print("📦 正在安装窗口识别依赖...")
        os.system("pip install pywin32")
        import win32gui
    
    try:
        import requests
    except:
        print("📦 正在安装网络请求依赖...")
        os.system("pip install requests")
        import requests
    
    # 启动豆星
    douxing = DouXingAI()
    douxing.check_environment()
    douxing.start_chat_interaction()