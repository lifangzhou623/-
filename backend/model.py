"""
中文文本情绪分析模型
支持两种模式：
1. SnowNLP - 轻量级，离线可用
2. Transformers - 基于BERT的中文情感分类（需下载模型，首次运行较慢）
"""
import jieba
import jieba.analyse
import re
import numpy as np
from collections import Counter


class SentimentAnalyzer:
    """中文情感分析器"""

    def __init__(self, use_transformers=True):
        self.use_transformers = use_transformers
        self.transformer_pipeline = None
        self._init_jieba()

        if use_transformers:
            self._load_transformer()

    def _init_jieba(self):
        """初始化jieba分词，加载自定义情感词典"""
        # 添加常用情感词
        positive_words = ['好', '棒', '优秀', '喜欢', '开心', '满意', '赞', '厉害', '牛',
                          '精彩', '完美', '不错', '舒服', '快乐', '幸福', '感动', '温暖']
        negative_words = ['差', '烂', '糟糕', '讨厌', '生气', '失望', '垃圾', '恶心',
                          '难受', '伤心', '愤怒', '悲哀', '坑', '骗', '假']
        for w in positive_words:
            jieba.suggest_freq(w, tune=True)
        for w in negative_words:
            jieba.suggest_freq(w, tune=True)

    def _load_transformer(self):
        """加载预训练Transformers模型"""
        try:
            from transformers import pipeline
            print("[模型] 正在加载中文情感分析模型...")
            # 使用哈工大讯飞联合发布的中文情感分析模型
            self.transformer_pipeline = pipeline(
                'sentiment-analysis',
                model='uer/roberta-base-finetuned-jd-binary-chinese',
                tokenizer='uer/roberta-base-finetuned-jd-binary-chinese',
                max_length=256,
                truncation=True
            )
            print("[模型] Transformers模型加载完成 ✓")
        except Exception as e:
            print(f"[模型] Transformers加载失败({e})，回退到SnowNLP")
            self.use_transformers = False
            self._init_snownlp()

    def _init_snownlp(self):
        """初始化SnowNLP"""
        try:
            from snownlp import SnowNLP
            self.SnowNLP = SnowNLP
            print("[模型] SnowNLP 加载完成 ✓")
        except ImportError:
            print("[模型] SnowNLP未安装，使用词典方法")

    def _split_sentences(self, text):
        """将长文本按句号、问号、感叹号等分割"""
        sentences = re.split(r'[。！？!?\n；;]', text)
        return [s.strip() for s in sentences if len(s.strip()) > 2]

    def analyze_snownlp(self, text):
        """使用SnowNLP进行情感分析（0~1，越接近1越正面）"""
        try:
            from snownlp import SnowNLP
            sentences = self._split_sentences(text)
            if not sentences:
                sentences = [text]

            scores = []
            for sent in sentences:
                s = SnowNLP(sent)
                scores.append(s.sentiments)

            avg_score = np.mean(scores) if scores else 0.5
        except ImportError:
            # Fallback: 基于情感词典的简单分析
            avg_score = self._lexicon_analysis(text)

        return self._score_to_label(avg_score), avg_score

    def analyze_transformer(self, text):
        """使用Transformers进行情感分析"""
        if self.transformer_pipeline is None:
            return self.analyze_snownlp(text)

        if len(text) > 500:
            text = text[:500]  # 截断过长文本

        result = self.transformer_pipeline(text)[0]
        label = result['label']
        score = result['score']

        # 转换：label可能为 'positive (2 stars)' 或 'negative (1 star)'
        if 'positive' in label.lower():
            sentiment_label = 'positive'
            sentiment_score = score
        elif 'negative' in label.lower():
            sentiment_label = 'negative'
            sentiment_score = 1 - score  # 负面的置信度
        else:
            sentiment_label = 'neutral'
            sentiment_score = 0.5

        return sentiment_label, sentiment_score

    def _lexicon_analysis(self, text):
        """基于情感词典的简单情感分析"""
        pos_words = ['好', '棒', '优秀', '喜欢', '开心', '满意', '赞', '厉害', '牛',
                      '精彩', '完美', '不错', '舒服', '快乐', '幸福', '感动', '温暖',
                      '支持', '推荐', '值得', '给力', '好评']
        neg_words = ['差', '烂', '糟糕', '讨厌', '生气', '失望', '垃圾', '恶心',
                      '难受', '伤心', '愤怒', '悲哀', '坑', '骗', '假', '差评',
                      '无语', '不要', '失败', '错误']

        text_lower = text.lower()
        pos_count = sum(1 for w in pos_words if w in text_lower)
        neg_count = sum(1 for w in neg_words if w in text_lower)

        total = pos_count + neg_count
        if total == 0:
            return 0.5
        return pos_count / total

    def _score_to_label(self, score):
        """将连续分数映射到情感标签"""
        if score > 0.6:
            return 'positive'
        elif score < 0.4:
            return 'negative'
        else:
            return 'neutral'

    def analyze(self, text):
        """
        综合分析
        返回: {
            'label': 'positive'|'negative'|'neutral',
            'score': float (0~1),
            'confidence': float (0~1),
            'keywords': [str],
            'sentences_detail': [{sentence, score, label}]
        }
        """
        if not text or not text.strip():
            return {
                'label': 'neutral', 'score': 0.5, 'confidence': 0,
                'keywords': [], 'sentences_detail': [], 'word_freq': []
            }

        text = text.strip()

        # 使用 Transformers 或 SnowNLP
        if self.use_transformers and self.transformer_pipeline is not None:
            label, score = self.analyze_transformer(text)
        else:
            label, score = self.analyze_snownlp(text)

        # 逐句分析
        sentences = self._split_sentences(text)
        sentences_detail = []
        for sent in sentences:
            if len(sent) > 2:
                if hasattr(self, 'SnowNLP'):
                    s = self.SnowNLP(sent)
                    s_score = s.sentiments
                else:
                    s_score = self._lexicon_analysis(sent)
                sentences_detail.append({
                    'text': sent,
                    'score': round(s_score, 4),
                    'label': self._score_to_label(s_score)
                })

        # 提取关键词
        keywords = self.extract_keywords(text, topk=15)

        # 词频统计
        word_freq = self.get_word_frequency(text, topk=30)

        # 置信度
        if label == 'positive':
            confidence = score
        elif label == 'negative':
            confidence = score
        else:
            confidence = 1 - abs(score - 0.5) * 2

        return {
            'label': label,
            'score': round(score, 4),
            'confidence': round(confidence, 4),
            'keywords': keywords,
            'sentences_detail': sentences_detail,
            'word_freq': word_freq
        }

    def extract_keywords(self, text, topk=15):
        """提取TF-IDF关键词"""
        try:
            keywords = jieba.analyse.extract_tags(text, topK=topk, withWeight=True)
            return [{'word': w, 'weight': round(weight, 4)} for w, weight in keywords]
        except:
            return []

    def get_word_frequency(self, text, topk=30):
        """获取词频统计"""
        words = jieba.lcut(text)
        # 过滤停用词和单字词
        stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都',
                      '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你',
                      '会', '着', '没有', '看', '好', '自己', '这', '他', '她', '它',
                      '们', '那', '什么', '怎么', '如何', '为什么', '因为', '所以',
                      '但是', '然而', '虽然', '可以', '这个', '那个', '我们', '你们',
                      '他们', '她们', '它们', '啊', '呢', '吧', '吗', '嗯', '哦',
                      '被', '把', '让', '给', '与', '或', '及', '对', '从', '以'}
        filtered = [w for w in words if len(w) > 1 and w not in stop_words]
        counter = Counter(filtered)
        return [{'word': w, 'count': c} for w, c in counter.most_common(topk)]

    def generate_wordcloud(self, text, output_path='wordcloud.png'):
        """生成词云图片"""
        try:
            from wordcloud import WordCloud
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt

            word_freq_dict = dict(counter.most_common(100))

            wc = WordCloud(
                font_path='C:/Windows/Fonts/msyh.ttc',  # 微软雅黑
                width=800, height=400,
                background_color='white',
                max_words=80,
                collocations=False,
                scale=2
            )

            if word_freq_dict:
                wc.generate_from_frequencies(word_freq_dict)
            else:
                wc.generate(text)

            wc.to_file(output_path)
            return output_path
        except Exception as e:
            print(f"词云生成失败: {e}")
            return None


# 全局单例
analyzer = SentimentAnalyzer(use_transformers=False)  # 先用SnowNLP确保启动速度快
