<template>
  <div class="ocr-page">
    <h2>OCR 文字識別</h2>

    <div class="upload-section">
      <label for="file-input" class="file-upload-button">
        📁 選擇圖片
      </label>
      <input
        id="file-input"
        type="file"
        accept="image/*"
        @change="handleFileSelect"
      />

      <div v-if="selectedFile" class="file-info">
        <p>已選擇: {{ selectedFile.name }}</p>
        <button @click="recognizeImage" :disabled="processing">
          {{ processing ? '識別中...' : '🔍 開始識別' }}
        </button>
      </div>
    </div>

    <div v-if="preview" class="preview-section">
      <h3>預覽</h3>
      <img :src="preview" alt="Preview" class="preview-image" />
    </div>

    <div v-if="result" class="result-section">
      <h3>識別結果</h3>
      <div class="result-stats">
        <div class="stat">
          <span>總區塊數:</span>
          <strong>{{ result.total_blocks }}</strong>
        </div>
        <div class="stat">
          <span>平均信心度:</span>
          <strong>{{ averageConfidence }}%</strong>
        </div>
      </div>

      <div class="text-blocks">
        <div
          v-for="(block, index) in result.text_blocks"
          :key="index"
          class="text-block"
        >
          <span class="index">{{ index + 1 }}</span>
          <span class="text">{{ block.text }}</span>
          <span class="confidence">{{ (block.confidence * 100).toFixed(1) }}%</span>
        </div>
      </div>

      <div class="actions">
        <button @click="copyText">📋 複製全部文字</button>
        <button @click="exportJSON">💾 匯出 JSON</button>
      </div>
    </div>

    <div v-if="error" class="error">
      ❌ {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const selectedFile = ref<File | null>(null)
const preview = ref('')
const processing = ref(false)
const result = ref<any>(null)
const error = ref('')

const averageConfidence = computed(() => {
  if (!result.value || !result.value.text_blocks) return 0
  const sum = result.value.text_blocks.reduce(
    (acc: number, block: any) => acc + block.confidence,
    0
  )
  return ((sum / result.value.text_blocks.length) * 100).toFixed(1)
})

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (file) {
    selectedFile.value = file
    
    // Create preview
    const reader = new FileReader()
    reader.onload = (e) => {
      preview.value = e.target?.result as string
    }
    reader.readAsDataURL(file)
    
    // Reset previous results
    result.value = null
    error.value = ''
  }
}

async function recognizeImage() {
  if (!selectedFile.value) return
  
  processing.value = true
  error.value = ''
  
  try {
    // In Electron, we need to get the file path
    const path = (selectedFile.value as any).path
    
    const ocrResult = await window.electronAPI.recognizeImage(path, {
      highSensitivity: false,
      convertFullwidth: true,
      verbose: false
    })
    
    result.value = ocrResult
  } catch (err: any) {
    error.value = err.message || '識別失敗'
    console.error('OCR Error:', err)
  } finally {
    processing.value = false
  }
}

function copyText() {
  if (!result.value) return
  
  const text = result.value.text_blocks
    .map((block: any) => block.text)
    .join('\n')
  
  navigator.clipboard.writeText(text)
  alert('已複製到剪貼簿')
}

function exportJSON() {
  if (!result.value) return
  
  const dataStr = JSON.stringify(result.value, null, 2)
  const blob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  
  const a = document.createElement('a')
  a.href = url
  a.download = 'ocr_result.json'
  a.click()
  
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.ocr-page {
  max-width: 1000px;
  margin: 0 auto;
}

.ocr-page h2 {
  margin-bottom: 2rem;
  color: #2c3e50;
}

.upload-section {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 2rem;
}

.file-info {
  margin-top: 1rem;
  display: flex;
  gap: 1rem;
  align-items: center;
}

.file-info p {
  flex: 1;
  color: #7f8c8d;
}

.preview-section {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 2rem;
}

.preview-image {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin-top: 1rem;
}

.result-section {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.result-stats {
  display: flex;
  gap: 2rem;
  margin: 1rem 0;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat {
  display: flex;
  gap: 0.5rem;
}

.text-blocks {
  margin: 1rem 0;
  max-height: 400px;
  overflow-y: auto;
}

.text-block {
  display: grid;
  grid-template-columns: 50px 1fr 80px;
  gap: 1rem;
  padding: 0.75rem;
  border-bottom: 1px solid #ecf0f1;
  align-items: center;
}

.text-block .index {
  color: #95a5a6;
  font-size: 0.875rem;
}

.text-block .text {
  color: #2c3e50;
}

.text-block .confidence {
  text-align: right;
  color: #27ae60;
  font-weight: 600;
  font-size: 0.875rem;
}

.actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.error {
  background: #fee;
  color: #c33;
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
