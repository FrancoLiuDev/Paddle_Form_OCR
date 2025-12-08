# 從 OCR 結果動態提取數字的方法總結

## 問題
如何從 OCR 識別結果中動態提取「1250頁」這類特定數字？

## 6 種提取方法對比

### 方法 1：關鍵字精確匹配 ⭐⭐⭐
**適用場景：** 知道完整的關鍵字

```python
# 查找包含「页」的所有區塊
results = [block for block in text_blocks if '页' in block['text']]
```

**優點：**
- 簡單直接
- 程式碼短

**缺點：**
- 不夠精確，會匹配所有包含「页」的文字
- 無法過濾其他條件

---

### 方法 2：正則表達式模式匹配 ⭐⭐⭐⭐⭐
**適用場景：** 需要靈活匹配複雜模式

```python
import re

# 匹配「數字+頁」的模式
pattern = r'\d+\s*[頁页]'
for block in text_blocks:
    if re.search(pattern, block['text']):
        matches = re.findall(pattern, block['text'])
        print(matches)  # ['1250页']

# 更精確的模式
pattern = r'1\d{3}\s*[頁页]'  # 1開頭的4位數+頁
```

**常用正則表達式：**
- `\d+\s*[頁页]` - 任意數字+頁
- `\d{3,}\s*[頁页]` - 3位以上數字+頁
- `1\d{3}\s*[頁页]` - 1開頭的4位數+頁
- `\d+\s*張` - 數字+張
- `\d+\s*次` - 數字+次

**優點：**
- 非常靈活
- 可以精確控制匹配模式
- 容錯性好（如 `\s*` 可匹配空格）

**缺點：**
- 需要了解正則表達式語法

---

### 方法 3：提取純數字 ⭐⭐⭐
**適用場景：** 從已知文字中提取數字

```python
import re

def extract_number(text):
    """從「1250页」中提取 1250"""
    numbers = re.findall(r'\d+', text)
    if numbers:
        return int(max(numbers, key=lambda x: int(x)))
    return None

# 使用
extract_number('1250页')  # 返回 1250
extract_number('95 6 页')  # 返回 95（最大的數字）
```

**優點：**
- 簡單實用
- 可以處理多個數字

**缺點：**
- 需要先找到包含目標的文字
- 如果有多個數字可能不準確

---

### 方法 4：語意搜尋（多關鍵字）⭐⭐⭐⭐
**適用場景：** 需要容錯，支援同義詞

```python
def semantic_search(text_blocks, keywords=['頁', '页', 'page']):
    """支援多個關鍵字"""
    results = []
    for block in text_blocks:
        if any(kw in block['text'] for kw in keywords):
            number = extract_number(block['text'])
            results.append({
                'text': block['text'],
                'number': number,
                'confidence': block['confidence']
            })
    return results
```

**優點：**
- 容錯性高
- 支援繁體/簡體/英文
- 可以處理不同表達方式

**缺點：**
- 可能產生誤匹配

---

### 方法 5：位置定位 ⭐⭐⭐⭐
**適用場景：** 固定格式的表單（如發票、報表）

```python
def extract_by_position(text_blocks, x_range=(200, 300), y_range=(170, 220)):
    """根據位置範圍提取"""
    results = []
    for block in text_blocks:
        x, y = block['bbox'][0]  # 左上角座標
        if x_range[0] <= x <= x_range[1] and y_range[0] <= y <= y_range[1]:
            if re.search(r'\d', block['text']):  # 包含數字
                results.append(block)
    return results
```

**優點：**
- 適合固定格式
- 精確度高
- 不受文字內容變化影響

**缺點：**
- 需要預先知道位置
- 格式變化時需要調整

---

### 方法 6：組合條件篩選 ⭐⭐⭐⭐⭐（推薦）
**適用場景：** 生產環境，需要高精確度

```python
def extract_with_conditions(text_blocks, 
                           keyword='页',
                           pattern=r'1\d{3}',  # 1開頭的4位數
                           min_confidence=0.9,
                           min_digits=4):
    """組合多個條件"""
    results = []
    
    for block in text_blocks:
        text = block['text']
        confidence = block['confidence']
        
        # 條件1: 信心度檢查
        if confidence < min_confidence:
            continue
        
        # 條件2: 關鍵字檢查
        if keyword not in text:
            continue
        
        # 條件3: 正則表達式檢查
        if not re.search(pattern, text):
            continue
        
        # 條件4: 數字位數檢查
        numbers = re.findall(r'\d+', text)
        if not numbers or len(max(numbers, key=len)) < min_digits:
            continue
        
        results.append({
            'text': text,
            'number': int(max(numbers, key=lambda x: int(x))),
            'confidence': confidence
        })
    
    return results
```

**優點：**
- 最靈活、最精確
- 可以組合多種條件
- 容錯性和精確性可調

**缺點：**
- 程式碼較長
- 需要調整多個參數

---

## 實際應用範例

### 範例 1：快速提取（最簡單）

```python
import json
import re

# 讀取 OCR 結果
with open('result.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 查找「頁」並提取數字
for block in data['text_blocks']:
    if '页' in block['text']:
        numbers = re.findall(r'\d+', block['text'])
        if numbers:
            print(f"找到: {max(numbers, key=lambda x: int(x))} 頁")
```

### 範例 2：精確提取（推薦）

```python
import json
import re

def extract_total_pages(json_path):
    """提取總頁數（最精確的方法）"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    candidates = []
    
    for block in data['text_blocks']:
        text = block['text']
        conf = block['confidence']
        
        # 檢查是否包含「頁」且信心度高
        if ('页' in text or '頁' in text) and conf > 0.8:
            # 提取數字
            numbers = re.findall(r'\d+', text)
            if numbers:
                num = int(max(numbers, key=lambda x: int(x)))
                # 假設總頁數至少是3位數
                if num >= 100:
                    candidates.append((num, conf, text))
    
    # 返回數字最大的（通常是總頁數）
    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        return {
            'pages': candidates[0][0],
            'confidence': candidates[0][1],
            'original_text': candidates[0][2]
        }
    
    return None

# 使用
result = extract_total_pages('result/result_fuji.json')
print(f"總頁數: {result['pages']} 頁")  # 1250 頁
```

### 範例 3：提取多個數字

```python
def extract_all_numbers(json_path):
    """提取所有統計數字"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stats = {
        'pages': [],      # 頁數
        'prints': [],     # 列印次數
        'sheets': [],     # 張數
    }
    
    patterns = {
        'pages': r'(\d+)\s*[頁页]',
        'prints': r'(\d+)\s*次',
        'sheets': r'(\d+)\s*[張张]',
    }
    
    for block in data['text_blocks']:
        text = block['text']
        
        for key, pattern in patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                stats[key].extend([int(m) for m in matches])
    
    return {
        'total_pages': max(stats['pages']) if stats['pages'] else None,
        'total_prints': sum(stats['prints']) if stats['prints'] else None,
        'total_sheets': sum(stats['sheets']) if stats['sheets'] else None,
    }

# 使用
stats = extract_all_numbers('result/result_fuji.json')
print(f"總頁數: {stats['total_pages']}")
print(f"列印次數: {stats['total_prints']}")
print(f"總張數: {stats['total_sheets']}")
```

---

## 方法選擇指南

| 需求 | 推薦方法 | 原因 |
|------|---------|------|
| 快速原型 | 方法1（關鍵字） | 最簡單 |
| 生產環境 | 方法6（組合條件） | 最精確 |
| 固定格式表單 | 方法5（位置定位） | 不受文字變化影響 |
| 需要靈活性 | 方法2（正則表達式） | 最靈活 |
| 多語言支援 | 方法4（語意搜尋） | 容錯性高 |
| 簡單數字提取 | 方法3（提取純數字） | 實用 |

---

## 完整示範程式

已提供兩個示範程式：

1. **extract_numbers.py** - 完整示範所有6種方法
2. **quick_extract_example.py** - 快速範例

### 使用方法

```bash
# 完整示範
python3 extract_numbers.py

# 快速範例
python3 quick_extract_example.py
```

---

## 常見問題

### Q1: OCR 識別錯誤怎麼辦？
**A:** 使用信心度過濾：
```python
if block['confidence'] > 0.8:  # 只接受高信心度的結果
    # 處理
```

### Q2: 數字中間有空格（如「95 6 页」）？
**A:** 使用正則表達式處理：
```python
# 移除所有空格再提取
text_clean = text.replace(' ', '')
numbers = re.findall(r'\d+', text_clean)
```

### Q3: 如何處理繁體/簡體混用？
**A:** 使用字元類別：
```python
pattern = r'\d+\s*[頁页]'  # 同時匹配繁體和簡體
```

### Q4: 如何提取特定範圍的數字（如只要4位數）？
**A:** 使用更精確的正則表達式：
```python
pattern = r'\d{4}\s*[頁页]'  # 只匹配4位數
```

---

## 總結

對於「提取1250頁」這個需求：

**最簡單的做法（快速原型）：**
```python
[int(re.findall(r'\d+', b['text'])[0]) 
 for b in text_blocks if '页' in b['text']]
```

**最推薦的做法（生產環境）：**
```python
# 使用 extract_numbers.py 中的 extract_by_conditions()
# 組合關鍵字、正則、信心度等多個條件
```

選擇哪種方法取決於：
1. 資料的複雜度
2. 精確度要求
3. 是否是固定格式
4. 開發時間
