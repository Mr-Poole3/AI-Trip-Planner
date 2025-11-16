# AI 旅行助手 🌍

一个基于大语言模型（LLM）的智能旅行规划助手，提供个性化旅行行程规划、交互式地图展示、多模式路线查询和酒店推荐等功能。

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Vue](https://img.shields.io/badge/vue-3.5+-brightgreen)

## ✨ 核心特性

### 🤖 智能对话式旅行规划
- **多轮对话需求收集**：通过自然对话逐步收集旅行信息（目的地、日期、人数等）
- **可视化进度追踪**：实时显示信息收集进度和完成度
- **智能字段编辑**：支持点击编辑已收集的信息
- **LLM 双阶段生成**：
  - 阶段1：需求分析和信息收集
  - 阶段2：基于完整信息生成详细行程

### 🗺️ 交互式地图展示
- **高德地图集成**：使用高德地图 JS API 2.0，国内访问流畅
- **每日路线可视化**：
  - 不同天数使用不同颜色标识
  - 景点标记自动编号（D1-1, D1-2...）
  - 自动绘制景点间的路线连接
- **地图数据持久化**：刷新页面或切换会话后地图自动恢复
- **批量地理编码**：一次性获取所有景点坐标，避免重复请求

### 🚗 多模式路线查询
- **三种出行方式**：
  - 🚗 驾车方案：详细导航步骤、距离、时长
  - 🚶 步行方案：适合短距离景点游览
  - 🚌 公交方案：换乘信息、站点数量
- **交互式展开查看**：点击路线卡片展开查看详细步骤
- **智能缓存机制**：
  - 消息级缓存：同一会话内即时响应
  - LocalStorage 缓存：跨会话持久化
  - 避免重复 API 调用，提升响应速度

### 🏨 酒店智能推荐
- **SSE 流式对话**：实时响应，自然对话体验
- **多轮上下文记忆**：记住用户偏好，精准推荐
- **Booking.com 集成**：
  - 实时抓取酒店信息
  - 价格、评分、位置等详细数据
  - 直接生成预订链接

### 💾 会话管理
- **多会话支持**：创建、切换、删除不同的聊天会话
- **会话级数据隔离**：
  - 每个会话独立的消息历史
  - 独立的旅行计划草稿
  - 独立的地图数据和路线缓存
- **本地持久化**：所有数据保存在浏览器 LocalStorage 中

## 🏗️ 技术架构

### 前端技术栈
- **框架**：Vue 3 + TypeScript
- **路由**：Vue Router 4
- **状态管理**：Pinia + 响应式系统
- **UI 样式**：原生 CSS（Google 风格设计）
- **地图**：高德地图 JS API 2.0
- **代码高亮**：highlight.js
- **Markdown 渲染**：marked + DOMPurify
- **构建工具**：Vite

### 后端技术栈
- **框架**：FastAPI
- **LLM**：豆包 AI（doubao-1-5-thinking-vision-pro-250428）
- **地图服务**：高德地图 Web 服务 API
- **爬虫**：Playwright（酒店信息抓取）
- **HTTP 客户端**：OpenAI SDK（兼容火山引擎接口）

### 核心依赖
```python
# 后端
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
openai>=1.68.2
python-dotenv>=1.0.1
python-multipart>=0.0.9
Pillow>=10.2.0
```

```json
// 前端
{
  "vue": "^3.5.17",
  "vue-router": "^4.5.1",
  "pinia": "^3.0.3",
  "ol": "^10.7.0",
  "marked": "^12.0.2",
  "dompurify": "^3.1.7",
  "highlight.js": "^11.11.1"
}
```

## 🚀 快速开始

### 环境要求
- **Node.js**: 18.x 或更高版本
- **Python**: 3.8 或更高版本
- **包管理器**: npm 或 yarn
- **浏览器**: 支持现代 ES6+ 特性的浏览器

### 1. 克隆项目
```bash
git clone <repository-url>
cd AI_house
```

### 2. 配置环境变量
在项目根目录创建 `.env` 文件：

```bash
# 豆包 AI API 密钥
ARK_API_KEY=your_ark_api_key_here

# 高德地图 API 密钥
AMAP_KEY=your_amap_key_here
```

**获取密钥**：
- 豆包 AI：访问 [火山引擎控制台](https://console.volcengine.com/ark)
- 高德地图：访问 [高德开放平台](https://lbs.amap.com/)

### 3. 安装后端依赖
```bash
cd backend
pip install -r ../requirements.txt
```

### 4. 安装前端依赖
```bash
cd frontend
npm install
```

### 5. 启动项目

**启动后端**（端口 9000）：
```bash
cd backend
python main.py
```

**启动前端**（端口 5173）：
```bash
cd frontend
npm run dev
```

### 6. 访问应用
打开浏览器访问：http://localhost:5173

## 📖 使用指南

### 旅行规划流程

1. **启动对话**
   - 在聊天界面输入旅行相关需求
   - 例如："我想去上海玩几天"

2. **信息收集**
   - 系统会逐步询问必要信息：
     - 🎯 目的地：要去哪里？
     - 🏠 出发地：从哪里出发？
     - 📅 开始日期：什么时候出发？
     - 📅 结束日期：什么时候返程？
   - 可选信息（不会主动询问）：
     - 👥 人数：几个人一起？
     - 🎪 景点偏好：想去哪些景点？

3. **编辑和确认**
   - 在右侧进度面板查看已收集信息
   - 点击任意字段可直接编辑
   - 系统自动检测并更新缺失字段

4. **生成行程**
   - 信息收集完成后自动触发计划生成
   - 显示详细的每日行程安排
   - 包含景点名称、游览顺序、交通方式

5. **查看地图**
   - 每日计划卡片顶部自动显示地图
   - 不同天数用不同颜色区分
   - 景点标记带编号（D1-1 表示第1天第1个景点）

6. **路线查询**
   - 点击景点间的路线按钮
   - 查看驾车、步行、公交三种方案
   - 展开查看详细导航步骤

### 酒店推荐

1. 切换到"酒店推荐"页面
2. 输入需求，例如："上海市中心，预算500元左右"
3. AI 助手会根据需求推荐合适酒店
4. 查看酒店详情、价格、评分等信息
5. 点击链接直接跳转预订

### 会话管理

- **新建会话**：点击左侧"新建对话"按钮
- **切换会话**：点击左侧会话列表中的任意会话
- **删除会话**：点击会话右侧的删除按钮
- **会话独立性**：每个会话的数据完全独立，互不干扰

## 🎨 界面设计

### 设计理念
- **简洁优雅**：参考 Google Material Design 风格
- **响应式布局**：适配不同屏幕尺寸
- **交互友好**：流畅的动画效果和反馈
- **信息层次清晰**：合理的视觉引导和层级划分

### 色彩方案
- **主色调**：#4A90E2（现代蓝）
- **强调色**：#5CB85C（成功绿）、#D9534F（警告红）
- **中性色**：灰度系统，保持阅读舒适性
- **地图颜色**：每日路线使用不同饱和色彩

### 组件特色
- **进度条**：渐变色彩，动态填充
- **路线卡片**：Google 风格，展开动画流畅
- **地图容器**：圆角阴影，优雅的边框设计
- **聊天气泡**：区分用户/助手，清晰易读

## 📊 API 接口

### 后端接口列表

| 接口路径 | 方法 | 功能描述 |
|---------|------|---------|
| `/api/chat` | POST | LLM 对话（需求分析 + 计划生成）|
| `/api/hotel-chat` | POST | 酒店推荐对话（SSE 流式）|
| `/api/batch-geocode` | POST | 批量地理编码 |
| `/api/multi-mode-route` | POST | 多模式路线查询 |
| `/api/amap-route-test` | POST | 单次路线测试 |
| `/api/amap-route-direct` | POST | 直接坐标路线计算 |
| `/api/hotel-search` | POST | 酒店搜索（Booking.com）|

### 高德地图 API 调用
- **地理编码**：`/v3/geocode/geo`
- **驾车规划**：`/v3/direction/driving`
- **步行规划**：`/v3/direction/walking`
- **公交规划**：`/v3/direction/transit/integrated`

## 🔒 安全性

- **API 密钥保护**：`.env` 文件加入 `.gitignore`
- **XSS 防护**：使用 DOMPurify 清洁 HTML 内容
- **CORS 配置**：后端配置跨域访问限制
- **输入验证**：Pydantic 模型验证所有输入数据

## 🐛 常见问题

### Q: 地图显示空白或无法加载？
A: 检查以下几点：
1. 确保 `.env` 中的 `AMAP_KEY` 已正确配置
2. 检查 `frontend/index.html` 中的地图脚本是否正确加载
3. 确认网络连接正常（高德地图需要联网）

### Q: LLM 返回格式错误？
A: 系统已实现健壮的 JSON 解析：
1. 支持嵌套数组和对象
2. 多层回退机制
3. 如果问题持续，检查后端日志中的 LLM 原始输出

### Q: 路线查询失败？
A: 可能原因：
1. 景点名称地理编码失败（名称不准确）
2. `city` 参数缺失（公交路线必需）
3. 查看浏览器控制台和后端日志排查

### Q: 会话数据丢失？
A: 数据存储在 LocalStorage 中：
1. 不要清除浏览器缓存
2. 切换浏览器或设备无法同步数据
3. 未来版本将支持云端同步

## 🛣️ Roadmap

### 近期计划
- [ ] 行程编辑功能（修改景点、顺序）
- [ ] 导出行程（PDF、图片）
- [ ] 天气信息集成
- [ ] 预算计算器

### 中期计划
- [ ] 用户账号系统
- [ ] 云端会话同步
- [ ] 行程分享功能
- [ ] 更多地图服务支持（腾讯地图、百度地图）

### 长期愿景
- [ ] 移动端 APP
- [ ] AI 实时导游功能
- [ ] 社交化旅行社区
- [ ] 多语言支持

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 贡献指南
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📧 联系方式

如有问题或建议，欢迎联系：
- 项目 Issue: [GitHub Issues](https://github.com/Mr-Poole3/AI-Trip-Planner)
- 邮箱: 2840269475@qq.com

## 🙏 致谢

- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Python Web 框架
- [豆包 AI](https://www.volcengine.com/product/doubao) - 强大的大语言模型
- [高德地图](https://lbs.amap.com/) - 专业的地图服务
- [OpenLayers](https://openlayers.org/) - 开源地图库
- [Marked](https://marked.js.org/) - Markdown 解析器

---

**⭐ 如果这个项目对你有帮助，请给一个 Star！**

