import json
import os
from openai import OpenAI

BASE_URL = "https://api.deepseek.com"
MODEL    = "deepseek-chat"

FIELDS = ["品牌", "车型", "配置版本", "颜色", "价格", "数量", "地区", "联系方式", "备注"]

SYSTEM_PROMPT = """你是汽车行业信息提取专家。从用户提供的微信群聊原始文本中，提取所有汽车报价信息。

规则：
- 每辆车/每条报价单独一条记录
- 相同车型不同颜色/配置分开列
- 字段缺失时填空字符串 ""
- 价格保留原始单位（万、元、$等）
- 只返回 JSON 数组，不要任何解释

返回格式（JSON array）：
[
  {
    "品牌": "马自达",
    "车型": "CX-5",
    "配置版本": "1258标准版",
    "颜色": "白/黑",
    "价格": "11500$",
    "数量": "2",
    "地区": "东区",
    "联系方式": "13xxxxxxxxx",
    "备注": "现车"
  }
]"""


def parse_text(raw_text: str) -> list[dict]:
    api_key = os.environ["DEEPSEEK_API_KEY"]
    client = OpenAI(api_key=api_key, base_url=BASE_URL)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": raw_text},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content.strip()

    parsed = json.loads(content)
    if isinstance(parsed, list):
        records = parsed
    else:
        # find the first list value
        records = next((v for v in parsed.values() if isinstance(v, list)), [])

    # normalize: ensure all fields present
    normalized = []
    for r in records:
        row = {field: str(r.get(field, "")).strip() for field in FIELDS}
        if any(row.values()):
            normalized.append(row)

    return normalized
