"""
Booking.com 酒店搜索自动化脚本 - 改进版
支持动态弹窗处理
"""
from playwright.sync_api import sync_playwright, Page
import time
import json
from typing import Optional, Dict, List
from datetime import datetime


def close_popups_dynamically(page: Page):
    """
    动态关闭各种弹窗
    这个函数会尝试关闭所有常见的弹窗，可以在任何时候调用
    """
    popups_closed = []
    
    # 定义所有可能的弹窗关闭策略
    close_strategies = [
        # 1. Genius 登录弹窗
        {
            "name": "Genius登录弹窗",
            "method": lambda: page.keyboard.press("Escape"),
            "check": lambda: True  # ESC键总是可以尝试
        },
        # 2. 通用关闭按钮（aria-label）
        {
            "name": "通用关闭按钮",
            "selector": 'button[aria-label*="关闭"], button[aria-label*="Close"], button[aria-label*="Dismiss"]',
            "timeout": 1000
        },
        # 3. Cookie 设置弹窗 - 点击"接受"
        {
            "name": "Cookie设置-接受",
            "text": "接受",
            "role": "button",
            "timeout": 1000
        },
        # 4. Cookie 设置弹窗 - 点击"拒绝"
        {
            "name": "Cookie设置-拒绝", 
            "text": "拒绝",
            "role": "button",
            "timeout": 1000
        },
        # 5. 切换中国版弹窗 - 留在国际版
        {
            "name": "留在国际版",
            "text": "留在国际版",
            "role": "button",
            "timeout": 1000
        },
        # 6. Modal 遮罩层关闭
        {
            "name": "Modal关闭按钮",
            "selector": '.bui-modal__close, .modal-header button',
            "timeout": 1000
        },
        # 7. X 按钮（SVG）
        {
            "name": "X关闭按钮",
            "selector": 'button:has(svg[data-testid="modal-close-icon"])',
            "timeout": 1000
        }
    ]
    
    for strategy in close_strategies:
        try:
            if "method" in strategy:
                # 自定义方法
                if strategy.get("check", lambda: False)():
                    strategy["method"]()
                    popups_closed.append(strategy["name"])
                    time.sleep(0.5)
            elif "selector" in strategy:
                # CSS 选择器
                element = page.locator(strategy["selector"]).first
                if element.is_visible(timeout=strategy.get("timeout", 1000)):
                    element.click()
                    popups_closed.append(strategy["name"])
                    time.sleep(0.5)
            elif "text" in strategy and "role" in strategy:
                # 文本 + 角色
                element = page.get_by_role(strategy["role"], name=strategy["text"])
                if element.is_visible(timeout=strategy.get("timeout", 1000)):
                    element.click()
                    popups_closed.append(strategy["name"])
                    time.sleep(0.5)
        except Exception as e:
            # 静默失败，继续尝试下一个策略
            pass
    
    if popups_closed:
        print(f"✓ 已关闭弹窗: {', '.join(popups_closed)}")
    
    return len(popups_closed) > 0


def handle_cookie_consent(page: Page):
    """处理 Cookie 确认页面（首次访问）"""
    if "pipl_consent" in page.url:
        print("检测到 Cookie 确认页面，正在处理...")
        try:
            # 等待页面加载
            time.sleep(1)
            
            # 步骤1: 点击"全选"标签
            try:
                select_all_label = page.locator('label').filter(has_text="全选")
                select_all_label.click()
                print("✓ 已点击全选")
                time.sleep(0.5)
            except Exception as e:
                print(f"点击全选时出错: {e}")
            
            # 步骤2: 点击"同意"按钮
            try:
                agree_button = page.get_by_role("button", name="同意")
                agree_button.click()
                print("✓ 已点击'同意'按钮")
                page.wait_for_load_state("networkidle", timeout=10000)
                time.sleep(2)
                print("✓ Cookie 确认完成，页面已跳转")
                return True
            except Exception as e:
                print(f"点击同意按钮时出错: {e}")
                return False
            
        except Exception as e:
            print(f"处理 Cookie 确认时出错: {e}")
            import traceback
            traceback.print_exc()
            return False
    return False


def safe_action(page: Page, action_name: str, action_func):
    """
    安全执行操作，操作前后都检查并关闭弹窗
    
    Args:
        page: Playwright page对象
        action_name: 操作名称（用于日志）
        action_func: 要执行的操作函数
    """
    print(f"准备执行: {action_name}")
    
    # 操作前关闭弹窗
    close_popups_dynamically(page)
    time.sleep(0.5)
    
    try:
        # 执行操作
        result = action_func()
        time.sleep(1)
        
        # 操作后再次关闭可能出现的弹窗
        close_popups_dynamically(page)
        
        print(f"✓ {action_name} 完成")
        return result
    except Exception as e:
        print(f"✗ {action_name} 失败: {e}")
        # 即使失败也尝试关闭弹窗
        close_popups_dynamically(page)
        raise


def search_hotel(
    destination: str,
    checkin_date: Optional[str] = None,
    checkout_date: Optional[str] = None,
    adults: int = 2,
    children: int = 0,
    rooms: int = 1,
    children_ages: Optional[List[int]] = None,
    pets: bool = False
) -> Dict:
    """
    搜索酒店并返回结果（改进版 - 支持动态弹窗处理）
    
    Args:
        destination: 目的地（城市、地区、酒店名称、地标等）
        checkin_date: 入住日期 (YYYY-MM-DD)
        checkout_date: 退房日期 (YYYY-MM-DD)
        adults: 成人数量
        children: 儿童数量
        rooms: 房间数量
        children_ages: 儿童年龄列表
        pets: 是否携带宠物
    
    Returns:
        包含酒店信息的字典
    """
    result = {
        "success": False,
        "hotels": [],
        "error": None,
        "search_params": {
            "destination": destination,
            "checkin_date": checkin_date,
            "checkout_date": checkout_date,
            "adults": adults,
            "children": children,
            "rooms": rooms,
            "children_ages": children_ages,
            "pets": pets
        }
    }
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        page = browser.new_page()
        page.set_default_timeout(30000)
        
        try:
            # 访问 Booking.com
            print(f"正在访问 Booking.com，搜索目的地：{destination}...")
            page.goto("https://www.booking.com/index.zh-cn.html", timeout=30000, wait_until="domcontentloaded")
            print("页面已加载")
            time.sleep(3)
            
            # 处理 Cookie 确认页面
            if handle_cookie_consent(page):
                time.sleep(2)
            
            # 🆕 首次进入首页后，立即关闭所有弹窗
            print("关闭初始弹窗...")
            close_popups_dynamically(page)
            time.sleep(1)
            
            # 1. 输入目的地（使用 safe_action）
            def input_destination():
                destination_input = page.get_by_role("combobox", name="目的地？")
                destination_input.clear()
                destination_input.fill(destination)
                destination_input.press("Enter")
            
            safe_action(page, f"输入目的地: {destination}", input_destination)
            time.sleep(2)
            
            # 2. 设置日期（使用 safe_action）
            if checkin_date and checkout_date:
                def set_dates():
                    date_button = page.get_by_role("button", name="入住日期 — 退房日期")
                    date_button.click()
                    time.sleep(1)
                    
                    checkin = page.locator(f'span[data-date="{checkin_date}"]').first
                    checkin.click()
                    time.sleep(0.5)
                    
                    checkout = page.locator(f'span[data-date="{checkout_date}"]').first
                    checkout.click()
                
                safe_action(page, f"设置日期: {checkin_date} 至 {checkout_date}", set_dates)
                time.sleep(1)
            
            # 3. 点击搜索按钮（使用 safe_action）
            def click_search():
                search_button = page.get_by_role("button", name="搜索")
                search_button.click()
            
            safe_action(page, "点击搜索按钮", click_search)
            
            # 等待搜索结果加载
            print("等待搜索结果加载...")
            page.wait_for_load_state("networkidle", timeout=30000)
            time.sleep(3)
            
            # 🆕 搜索结果页面也可能有弹窗，再次关闭
            close_popups_dynamically(page)
            time.sleep(1)
            
            # 提取酒店信息
            print("正在提取酒店信息...")
            hotels = []
            
            # 🆕 滚动页面时也检查弹窗
            def scroll_and_extract():
                nonlocal hotels
                
                # 滚动加载更多结果
                for _ in range(3):
                    page.evaluate("window.scrollBy(0, 1000)")
                    time.sleep(1)
                    # 每次滚动后都关闭可能出现的弹窗
                    close_popups_dynamically(page)
                
                # 提取酒店卡片
                hotel_cards = page.locator('[data-testid="property-card"]').all()
                print(f"找到 {len(hotel_cards)} 个酒店")
                
                for card in hotel_cards[:10]:  # 只取前10个
                    try:
                        hotel_data = {}
                        
                        # 提取酒店名称
                        try:
                            name_elem = card.locator('[data-testid="title"]')
                            hotel_data["name"] = name_elem.inner_text()
                        except:
                            hotel_data["name"] = "未知酒店"
                        
                        # 提取价格
                        try:
                            price_elem = card.locator('[data-testid="price-and-discounted-price"]')
                            hotel_data["price"] = price_elem.inner_text()
                        except:
                            hotel_data["price"] = "价格未知"
                        
                        # 提取评分
                        try:
                            rating_elem = card.locator('[data-testid="review-score"]')
                            hotel_data["rating"] = rating_elem.inner_text()
                        except:
                            hotel_data["rating"] = "暂无评分"
                        
                        # 提取位置
                        try:
                            location_elem = card.locator('[data-testid="address"]')
                            hotel_data["location"] = location_elem.inner_text()
                        except:
                            hotel_data["location"] = "位置未知"
                        
                        # 提取图片
                        try:
                            img_elem = card.locator('img').first
                            hotel_data["image_url"] = img_elem.get_attribute("src")
                        except:
                            hotel_data["image_url"] = ""
                        
                        # 提取链接
                        try:
                            link_elem = card.locator('a[data-testid="title-link"]')
                            hotel_data["link"] = link_elem.get_attribute("href")
                            if hotel_data["link"] and not hotel_data["link"].startswith("http"):
                                hotel_data["link"] = "https://www.booking.com" + hotel_data["link"]
                        except:
                            hotel_data["link"] = ""
                        
                        hotels.append(hotel_data)
                        
                    except Exception as e:
                        print(f"提取单个酒店信息时出错: {e}")
                        continue
            
            safe_action(page, "滚动并提取酒店信息", scroll_and_extract)
            
            result["success"] = True
            result["hotels"] = hotels
            print(f"✓ 成功提取 {len(hotels)} 个酒店")
            
        except Exception as e:
            result["error"] = str(e)
            print(f"搜索过程出错: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # 保持浏览器打开一段时间以便查看结果
            time.sleep(2)
            browser.close()
    
    return result


if __name__ == "__main__":
    # 测试搜索
    result = search_hotel(
        destination="上海外滩",
        checkin_date="2024-12-20",
        checkout_date="2024-12-22",
        adults=2
    )
    
    print("\n" + "="*50)
    print("搜索结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

