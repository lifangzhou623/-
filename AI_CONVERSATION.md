# AI 助手交流记录

> 项目：AI 中文文本情绪分析系统
> 日期：2026年6月
> 工具：Claude Code (Anthropic)

---

## 1. 项目选题阶段

**我**：帮我按照要求完成大项目，选题选择做一个有趣的网站

**AI**：列出了5个选题方向（AI手写识别、股票预测仪表盘、文本情绪分析、图像风格迁移、推荐系统），分析了各自的优缺点。

**我**：3（选择AI文本情绪分析）

**AI**：确认选题，开始技术方案设计。

---

## 2. 技术方案设计

**AI** 提出技术架构：
- 后端 Flask + SnowNLP/Transformers
- 前端原生 HTML/CSS/JS + ECharts
- 中文分词 jieba + 词云 wordcloud
- 单文本分析 + 批量CSV处理 + 历史记录

**我**：继续

---

## 3. 项目实施过程

### 后端开发（model.py + app.py）

- 实现 `SentimentAnalyzer` 类，支持双模式：
  - SnowNLP：轻量级中文情感分析
  - Transformers：预训练BERT中文模型
- 集成 jieba 分词和 TF-IDF 关键词提取
- Flask API 提供4个接口：单文本分析、批量分析、词云生成、历史查询
- 词云生成使用中文字体（微软雅黑）

### 前端开发（index.html）

- 暗色主题UI，响应式布局
- 三个Tab面板：单文本、批量、历史
- ECharts 集成：词频柱状图 + 情感饼图
- 拖拽上传CSV文件
- 逐句分析展开
- 关键词标签展示

### 文档撰写

- README.md：项目概述、技术栈、快速开始、API文档
- AI_CONVERSATION.md（本文件）：完整AI对话记录
- requirements.txt：Python依赖清单

---

## 4. 遇到的问题与解决

### 问题1：Transformers模型加载慢且需要GPU
**解决**：默认使用SnowNLP（加载快、CPU友好），Transformers作为可选升级

### 问题2：词云中文乱码
**解决**：指定中文字体路径 `C:/Windows/Fonts/msyh.ttc`

### 问题3：批量分析性能
**解决**：限制单次100条，逐条分析并返回统计摘要

---

## 5. 总结

通过本项目，完成了以下技术实践：
1. Flask REST API 设计与实现
2. 中文NLP（分词、情感分析、关键词提取）的工程应用
3. 前端数据可视化（ECharts）
4. ML模型的集成与部署
5. 完整的项目文档编写

AI辅助效率：代码生成约80%、调试定位约90%、文档撰写约70%。
