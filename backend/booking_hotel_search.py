"""
Booking.com 酒店搜索自动化脚本
支持动态参数搜索酒店
"""
from playwright.async_api import async_playwright
import asyncio
import json
from typing import Optional, Dict, List
from datetime import datetime


async def close_popups_dynamically(page):
    """
    动态关闭各种弹窗 - 可以在任何时候调用
    """
    popups_closed = []
    
    # ESC 键（最通用，可以关闭大多数弹窗）
    try:
        await page.keyboard.press("Escape")
        await asyncio.sleep(0.3)
        popups_closed.append("ESC键关闭")
    except:
        pass
    
    # 定义所有可能的弹窗关闭策略
    close_strategies = [
        # 通用关闭按钮
        ('button[aria-label*="关闭"]', "关闭按钮"),
        ('button[aria-label*="Close"]', "Close按钮"),
        ('button[aria-label*="Dismiss"]', "Dismiss按钮"),
        # Cookie 弹窗
        ('.bui-modal__close', "Modal关闭"),
        # X 按钮
        ('button:has(svg)', "SVG关闭按钮"),
    ]
    
    for selector, name in close_strategies:
        try:
            element = page.locator(selector).first
            if await element.is_visible(timeout=1000):
                await element.click()
                popups_closed.append(name)
                await asyncio.sleep(0.3)
        except:
            pass
    
    # 尝试点击特定文本按钮
    text_buttons = [
        ("接受", "Cookie接受"),
        ("拒绝", "Cookie拒绝"),
        ("留在国际版", "留在国际版"),
    ]
    
    for text, name in text_buttons:
        try:
            element = page.get_by_role("button", name=text)
            if await element.is_visible(timeout=1000):
                await element.click()
                popups_closed.append(name)
                await asyncio.sleep(0.3)
        except:
            pass
    
    if popups_closed:
        print(f"✓ 已关闭弹窗: {', '.join(popups_closed)}")
    
    return len(popups_closed) > 0


async def handle_cookie_consent(page):
    """处理 Cookie 确认页面"""
    if "pipl_consent" in page.url:
        print("检测到 Cookie 确认页面，正在处理...")
        try:
            # 等待页面加载
            await asyncio.sleep(1)
            
            # 步骤1: 点击"全选"标签（点击label而不是checkbox）
            try:
                # 使用 label 定位器查找包含"全选"文本的标签并点击
                select_all_label = page.locator('label').filter(has_text="全选")
                await select_all_label.click()
                print("✓ 已点击全选")
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"点击全选时出错: {e}")
            
            # 步骤2: 点击"同意"按钮
            try:
                agree_button = page.get_by_role("button", name="同意")
                await agree_button.click()
                print("✓ 已点击'同意'按钮")
                # 等待页面跳转
                await page.wait_for_load_state("networkidle", timeout=10000)
                await asyncio.sleep(2)
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


async def search_hotel(
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
    搜索酒店并返回结果
    
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
    
    async with async_playwright() as p:
        # 使用非headless模式，可以看到浏览器操作过程
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']  # 避免被检测为机器人
        )
        page = await browser.new_page()
        # 设置更长的默认超时
        page.set_default_timeout(30000)
        
        try:
            # 访问 Booking.com
            print(f"正在访问 Booking.com，搜索目的地：{destination}...")
            print("开始加载页面...")
            await page.goto("https://booking.cn/index.zh-cn.html", timeout=30000, wait_until="domcontentloaded")
            print("DOM 已加载")
            await asyncio.sleep(3)
            
            # 处理 Cookie 确认页面
            print("检查 Cookie 确认页面...")
            cookie_handled = await handle_cookie_consent(page)
            if cookie_handled:
                print("Cookie 处理完成，等待页面稳定...")
                await asyncio.sleep(2)
            else:
                print("无需处理 Cookie")
            
            # 🆕 动态关闭所有可能的初始弹窗
            print("关闭初始弹窗...")
            await close_popups_dynamically(page)
            await asyncio.sleep(1)
            
            # 1. 输入目的地
            print(f"正在输入目的地：{destination}...")
            # 🆕 操作前关闭弹窗
            await close_popups_dynamically(page)
            try:
                destination_input = page.get_by_role("combobox", name="目的地？")
                await destination_input.clear()
                await destination_input.fill(destination)
                print(f"已输入目的地：{destination}")
                await asyncio.sleep(2)
                await destination_input.press("Enter")
                print("已按下 Enter 键")
                await asyncio.sleep(1)
                # 🆕 操作后关闭弹窗
                await close_popups_dynamically(page)
            except Exception as e:
                print(f"输入目的地时出错: {e}")
                raise
            
            # 2. 设置日期
            if checkin_date and checkout_date:
                print(f"正在设置日期：{checkin_date} 至 {checkout_date}...")
                try:
                    date_button = page.get_by_role("button", name="入住日期 — 退房日期")
                    await date_button.click()
                    print("已打开日期选择器")
                    await asyncio.sleep(1)
                    
                    checkin = page.locator(f'span[data-date="{checkin_date}"]').first
                    await checkin.click()
                    print(f"已选择入住日期：{checkin_date}")
                    await asyncio.sleep(0.5)
                    
                    checkout = page.locator(f'span[data-date="{checkout_date}"]').first
                    await checkout.click()
                    print(f"已选择退房日期：{checkout_date}")
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"日期选择出现问题: {e}")
            
            # 3. 设置旅客信息
            if adults != 2 or children != 0 or rooms != 1:
                print(f"正在设置旅客信息：{adults}位成人，{children}位儿童，{rooms}间房...")
                # 这里可以添加更复杂的旅客设置逻辑
            
            # 🆕 搜索前再次关闭弹窗
            print("搜索前关闭弹窗...")
            await close_popups_dynamically(page)
            
            # 4. 点击搜索按钮
            print("正在搜索...")
            search_button = page.get_by_role("button", name="搜特价")
            # 使用 force=True 强制点击，忽略遮挡
            await search_button.click(force=True)
            
            # 等待搜索结果页面加载
            print("等待页面跳转...")
            try:
                await page.wait_for_url("**/searchresults.*", timeout=15000)
                print("页面已跳转到搜索结果")
            except:
                print("URL未按预期变化，继续...")
            
            await page.wait_for_load_state("networkidle", timeout=30000)
            await asyncio.sleep(3)
            
            # 再次检查 Cookie 确认页面
            await handle_cookie_consent(page)
            
            # 🆕 搜索结果页面关闭弹窗
            print("关闭搜索结果页面弹窗...")
            await close_popups_dynamically(page)
            await asyncio.sleep(1)
            
            # 获取搜索结果
            try:
                # 等待页面加载完成
                print("等待搜索结果加载...")
                await asyncio.sleep(8)  # 给页面更多时间加载
                
                # 等待酒店卡片出现
                print("等待酒店卡片加载...")
                await page.wait_for_selector('[data-testid="property-card"]', timeout=20000)
                print("酒店卡片已加载")
                
                # 获取酒店卡片
                hotels = await page.locator('[data-testid="property-card"]').all()
                
                if not hotels or len(hotels) == 0:
                    # 保存页面截图用于调试
                    print("未找到酒店元素，保存页面截图...")
                    await page.screenshot(path="debug_screenshot.png")
                    print("页面URL:", page.url)
                    result["error"] = "未找到酒店搜索结果，可能是页面结构变化或网络问题"
                    return result
                
                print(f"找到 {len(hotels)} 家酒店")
                
                # 提取前10个酒店信息（LLM会从中选择5个推荐）
                for i, hotel in enumerate(hotels[:10], 1):
                    try:
                        hotel_info = {}
                        
                        # 酒店名称
                        try:
                            hotel_info["name"] = await hotel.locator('[data-testid="title"]').inner_text(timeout=3000)
                        except:
                            try:
                                hotel_info["name"] = await hotel.locator('h3, h4').first.inner_text(timeout=3000)
                            except:
                                print(f"无法获取酒店 {i} 的名称，跳过")
                                continue
                        
                        # 价格
                        try:
                            price = await hotel.locator('[data-testid="price-and-discounted-price"]').inner_text(timeout=3000)
                            hotel_info["price"] = price
                        except:
                            try:
                                price = await hotel.locator('.prco-valign-middle-helper').first.inner_text(timeout=3000)
                                hotel_info["price"] = price
                            except:
                                hotel_info["price"] = "价格待询"
                        
                        # 评分
                        try:
                            score = await hotel.locator('[data-testid="review-score"]').inner_text(timeout=3000)
                            hotel_info["score"] = score
                        except:
                            try:
                                score = await hotel.locator('.bui-review-score__badge').first.inner_text(timeout=3000)
                                hotel_info["score"] = score
                            except:
                                hotel_info["score"] = "暂无评分"
                        
                        # 位置
                        try:
                            location = await hotel.locator('[data-testid="address"]').inner_text(timeout=3000)
                            hotel_info["location"] = location
                        except:
                            try:
                                location = await hotel.locator('[data-testid="distance"]').inner_text(timeout=3000)
                                hotel_info["location"] = location
                            except:
                                hotel_info["location"] = "位置信息待确认"
                        
                        # 设施/特色
                        try:
                            facilities = await hotel.locator('[data-testid="facility-group"]').all_inner_texts()
                            hotel_info["facilities"] = facilities[:5] if facilities else []
                        except:
                            hotel_info["facilities"] = []
                        
                        result["hotels"].append(hotel_info)
                        print(f"{i}. {hotel_info['name']} - {hotel_info['price']}")
                        
                    except Exception as e:
                        print(f"提取酒店 {i} 信息时出错: {e}")
                        continue
                
                if len(result["hotels"]) > 0:
                    result["success"] = True
                else:
                    result["error"] = "成功访问页面但未能提取酒店信息"
                        
            except Exception as e:
                result["error"] = f"获取搜索结果时出错: {str(e)}"
                print(result["error"])
            
        except Exception as e:
            result["error"] = f"搜索过程出错: {str(e)}"
            print(result["error"])
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()
    
    return result


if __name__ == "__main__":
    # 测试搜索
    result = asyncio.run(search_hotel(
        destination="成都春熙路",
        checkin_date="2025-11-13",
        checkout_date="2025-11-14",
        adults=2
    ))
    print(json.dumps(result, ensure_ascii=False, indent=2))