"""
AI 中文文本情绪分析系统 - Flask API
"""
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from model import analyzer
import os
import json
import pandas as pd
from io import BytesIO

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend'))
CORS(app)

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')


@app.route('/')
def serve_frontend():
    return send_from_directory(FRONTEND_DIR, 'index.html')

HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'history.json')
WORDCLOUD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'wordclouds')
os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
os.makedirs(WORDCLOUD_DIR, exist_ok=True)


@app.route('/')
def index():
    return jsonify({'service': 'AI中文情感分析API', 'version': '1.0', 'status': 'running'})


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    单文本情感分析
    请求: {"text": "..."}
    返回: {"label": "positive", "score": 0.85, "confidence": 0.85, ...}
    """
    data = request.get_json(force=True)
    text = data.get('text', '')

    if not text.strip():
        return jsonify({'error': '文本不能为空'}), 400

    result = analyzer.analyze(text)

    # 保存历史记录
    save_history({
        'text': text[:200],
        'label': result['label'],
        'score': result['score'],
        'timestamp': pd.Timestamp.now().isoformat()
    })

    return jsonify(result)


@app.route('/api/analyze/batch', methods=['POST'])
def analyze_batch():
    """
    批量文本情感分析（上传CSV或JSON）
    请求: CSV文件 或 {"texts": ["文本1", "文本2", ...]}
    返回: {"results": [...], "summary": {...}}
    """
    results = []

    if request.is_json:
        texts = request.get_json().get('texts', [])
    elif request.files:
        file = request.files.get('file')
        if file:
            content = file.read().decode('utf-8')
            df = pd.read_csv(BytesIO(content.encode())) if file.filename.endswith('.csv') else None
            if df is None:
                texts = content.split('\n')
            else:
                text_col = df.columns[0]
                texts = df[text_col].dropna().tolist()
        else:
            texts = []
    else:
        return jsonify({'error': '请提供texts数组或上传CSV文件'}), 400

    for t in texts[:100]:  # 限制100条
        if str(t).strip():
            result = analyzer.analyze(str(t).strip())
            results.append({
                'text': str(t)[:100],
                'label': result['label'],
                'score': result['score']
            })

    # 统计摘要
    labels = [r['label'] for r in results]
    summary = {
        'total': len(results),
        'positive': labels.count('positive'),
        'negative': labels.count('negative'),
        'neutral': labels.count('neutral'),
        'positive_rate': round(labels.count('positive') / max(len(results), 1) * 100, 1),
        'negative_rate': round(labels.count('negative') / max(len(results), 1) * 100, 1),
        'neutral_rate': round(labels.count('neutral') / max(len(results), 1) * 100, 1),
        'avg_score': round(sum(r['score'] for r in results) / max(len(results), 1), 4)
    }

    return jsonify({'results': results, 'summary': summary})


@app.route('/api/wordcloud', methods=['POST'])
def wordcloud():
    """
    生成词云
    请求: {"text": "..."}
    返回: 词云图片PNG
    """
    data = request.get_json(force=True)
    text = data.get('text', '')

    if not text.strip():
        return jsonify({'error': '文本不能为空'}), 400

    import hashlib
    text_hash = hashlib.md5(text.encode()).hexdigest()[:10]
    output_path = os.path.join(WORDCLOUD_DIR, f'wc_{text_hash}.png')

    if not os.path.exists(output_path):
        analyzer.generate_wordcloud(text, output_path)

    if os.path.exists(output_path):
        return send_file(output_path, mimetype='image/png')
    return jsonify({'error': '词云生成失败'}), 500


@app.route('/api/history', methods=['GET'])
def history():
    """获取分析历史"""
    records = load_history()
    # 统计
    labels = [r['label'] for r in records]
    return jsonify({
        'records': records[-20:],  # 最近20条
        'total': len(records),
        'stats': {
            'positive': labels.count('positive'),
            'negative': labels.count('negative'),
            'neutral': labels.count('neutral')
        }
    })


@app.route('/api/history/clear', methods=['DELETE'])
def clear_history():
    """清空分析历史"""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)
    return jsonify({'status': 'ok'})

def save_history(record):
    records = load_history()
    records.append(record)
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  AI 中文文本情绪分析系统")
    print("  接口: http://localhost:5000")
    print("  前端: 打开 frontend/index.html")
    print("=" * 50 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
