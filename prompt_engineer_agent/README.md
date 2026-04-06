# Prompt Engineer Agent

## 安裝
```bash
pip install pyyaml rich
```

## 使用方式

### 命令列
```bash
python run.py --mode design --task it_news_summary
python run.py --mode test --prompt it_news_summary_v2
python run.py --mode optimize --prompt it_news_summary_v1
python run.py --mode library --list
```

### 程式化
```python
from prompt_engineer import PromptEngineer

pe = PromptEngineer()
prompt = pe.design(task="摘要生成", context={...})
results = pe.test(prompt_id="summary_v1")
```
