# AI 中文文本情绪分析系统

> 基于深度学习的智能中文情感识别网站 · 数据科学与大数据技术大项目

## 项目概述

本系统是一个**中文文本情绪分析**Web应用，用户输入中文文本后，系统自动判断情感倾向（正面/负面/中性），并提供置信度评分、关键词提取、词云生成、逐句分析等功能。支持单文本和批量CSV两种分析模式。

### 功能特性

- **单文本分析**：输入中文文本 → 即时返回情感标签、得分、置信度
- **逐句拆解**：自动分句，逐句标注情感倾向
- **关键词提取**：基于 TF-IDF 的关键词分析
- **词云生成**：一键生成可视化词云
- **批量分析**：上传CSV文件，批量处理并统计情感分布
- **历史记录**：本地保存分析历史，支持回顾统计
- **可视化图表**：ECharts 词频柱状图、情感饼图、分布概览

### 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python Flask + flask-cors |
| ML 模型 | SnowNLP / Transformers (BERT-Chinese) |
| 中文分词 | jieba |
| 词云 | wordcloud |
| 前端 | 原生 HTML/CSS/JS + ECharts 图表 |
| 数据处理 | pandas + numpy |

### 项目结构

```
sentiment-analysis/
├── backend/
│   ├── app.py              # Flask API 服务
│   ├── model.py            # 情感分析模型（SnowNLP + Transformers）
│   └── requirements.txt    # Python依赖
├── frontend/
│   └── index.html          # 单页前端（直接打开即可用）
├── data/
│   ├── history.json        # 分析历史记录
│   └── wordclouds/         # 生成的词云图片
├── AI_CONVERSATION.md       # 与AI助手的完整对话记录
└── README.md               # 本文件
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r backend/requirements.txt
```

### 2. 启动后端

```bash
cd backend
python app.py
```

后端启动在 `http://localhost:5000`

### 3. 打开前端

直接用浏览器打开 `frontend/index.html`，或使用任意 HTTP 服务器：

```bash
cd frontend
python -m http.server 8080
# 浏览器打开 http://localhost:8080
```

### 4. 使用

1. 在文本框中输入中文文本（例如影评、微博、新闻）
2. 点击「开始分析」
3. 查看情感标签、得分、置信度
4. 浏览关键词提取和逐句分析结果
5. 点击「生成词云」获取可视化词云图

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/analyze` | 单文本分析 `{"text": "..."}` |
| POST | `/api/analyze/batch` | 批量分析 `{"texts": [...]}` |
| POST | `/api/wordcloud` | 生成词云 |
| GET | `/api/history` | 获取历史记录 |

## 模型说明

- **SnowNLP**（默认）：轻量级，离线可用，基于贝叶斯分类的中文情感分析
- **Transformers**（可选）：基于 `uer/roberta-base-finetuned-jd-binary-chinese` 预训练模型，准确率更高

如需切换模型，修改 `backend/model.py` 中 `SentimentAnalyzer` 初始化参数：
```python
analyzer = SentimentAnalyzer(use_transformers=True)  # 使用Transformers
```

## 许可证

MIT License
