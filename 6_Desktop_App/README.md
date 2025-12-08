# 桌面應用程式 - OCR 文字識別與提取

這是一個基於 Electron + Vue 3 + TypeScript 的桌面應用程式，整合了 PaddleOCR 文字識別和動態欄位提取功能。

## 技術棧

- **前端**: Vue 3 + TypeScript + Vue Router + Pinia
- **桌面框架**: Electron 28
- **建置工具**: Vite 5
- **後端**: Python 3.8+ (PaddleOCR)

## 功能特色

### 1. OCR 文字識別
- 圖片上傳與預覽
- PaddleOCR 高精度識別
- 文字區塊信心度顯示
- 自動全型轉半型
- 結果匯出 (JSON/TXT)

### 2. 文字提取
- 動態欄位提取
- 模糊匹配演算法
- 繁簡體自動轉換
- 結構化資料輸出

### 3. 系統資訊
- Python 版本檢測
- Electron 版本顯示
- 即時狀態監控

## 前置需求

### 系統需求
- Node.js 18+ 
- Python 3.8+
- npm 或 yarn

### Python 環境
確保已安裝 PaddleOCR 相關套件：

```bash
cd ../4_OCR_Recognition
pip install -r requirements.txt
```

## 安裝步驟

### 1. 安裝依賴

```bash
cd 6_Desktop_App
npm install
```

### 2. 開發模式

```bash
npm run dev
```

這會啟動：
- Vite 開發伺服器 (Vue 3 前端)
- Electron 視窗

### 3. 建置應用程式

```bash
npm run build          # 建置前端
npm run electron:build # 打包 Electron 應用
```

建置完成後，執行檔會在 `dist/` 目錄中。

## 專案結構

```
6_Desktop_App/
├── package.json           # 專案配置與依賴
├── tsconfig.json          # TypeScript 配置
├── vite.config.ts         # Vite 配置
├── index.html             # 入口 HTML
├── electron/
│   ├── main.ts           # Electron 主程序
│   └── preload.ts        # 預載腳本 (IPC)
└── src/
    ├── main.ts           # Vue 應用入口
    ├── App.vue           # 根元件
    ├── style.css         # 全域樣式
    ├── router/
    │   └── index.ts      # 路由配置
    └── views/
        ├── Home.vue           # 首頁
        ├── OCRPage.vue        # OCR 識別頁
        └── ExtractionPage.vue # 文字提取頁
```

## IPC 通訊架構

### 可用 API

```typescript
// OCR 識別
await window.electronAPI.recognizeImage(imagePath: string)

// 欄位提取
await window.electronAPI.extractFields(jsonData: any, fields: string[])

// 取得 Python 版本
await window.electronAPI.getPythonVersion()
```

### 實作細節

1. **主程序** (`electron/main.ts`): 處理 Python 子程序呼叫
2. **預載腳本** (`electron/preload.ts`): 暴露安全的 IPC API
3. **渲染程序** (Vue 元件): 透過 `window.electronAPI` 呼叫

## 開發指南

### 新增路由

編輯 `src/router/index.ts`:

```typescript
const routes = [
  // ... 現有路由
  {
    path: '/new-page',
    name: 'NewPage',
    component: () => import('../views/NewPage.vue')
  }
]
```

### 新增 IPC 處理器

編輯 `electron/main.ts`:

```typescript
ipcMain.handle('new:api', async (event, arg) => {
  // 處理邏輯
  return result
})
```

編輯 `electron/preload.ts`:

```typescript
contextBridge.exposeInMainWorld('electronAPI', {
  // ... 現有 API
  newApi: (arg: any) => ipcRenderer.invoke('new:api', arg)
})
```

## Python 後端整合

### 開發環境
- OCR: `../4_OCR_Recognition/ocr_parser.py`
- 提取: `../5_Text_Extraction/extract_fuji_fields_dynamic.py`

### 生產環境
建置時會自動將 Python 腳本打包到 `resources/` 目錄。

## 常見問題

### Q: TypeScript 編譯錯誤
A: 確保已執行 `npm install` 安裝所有依賴。

### Q: Python 找不到模組
A: 確認 Python 環境已安裝 `paddleocr`, `opencv-python` 等套件。

### Q: Electron 視窗無法啟動
A: 檢查控制台錯誤訊息，確認 `electron/main.ts` 中的路徑正確。

### Q: OCR 識別失敗
A: 確認圖片路徑正確，且 Python 腳本可正常執行：
```bash
python3 ../4_OCR_Recognition/ocr_parser.py <image_path>
```

## 授權

此專案為內部使用，未指定公開授權。

## 聯絡資訊

如有問題或建議，請聯絡專案維護者。
