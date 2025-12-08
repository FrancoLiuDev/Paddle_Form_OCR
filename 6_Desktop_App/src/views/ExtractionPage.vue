<template>
  <div class="extraction-page">
    <h2>文字提取</h2>

    <div class="input-section">
      <h3>輸入 OCR 結果</h3>
      <textarea
        v-model="jsonInput"
        placeholder="貼上 OCR JSON 結果..."
        rows="10"
      ></textarea>
      
      <div class="fields-config">
        <h4>要提取的欄位</h4>
        <div class="field-inputs">
          <input
            v-for="(field, index) in fields"
            :key="index"
            v-model="fields[index]"
            type="text"
            placeholder="欄位名稱"
          />
          <button @click="addField">+ 新增欄位</button>
        </div>
      </div>

      <button @click="extractFields" :disabled="!jsonInput || processing">
        {{ processing ? '提取中...' : '🔍 開始提取' }}
      </button>
    </div>

    <div v-if="extractedData" class="result-section">
      <h3>提取結果</h3>
      
      <div class="extracted-fields">
        <div
          v-for="(field, name) in extractedData.extracted_fields"
          :key="name"
          class="field-result"
        >
          <div class="field-name">{{ name }}</div>
          <div class="field-value">
            <span class="value">{{ field.value }}</span>
            <span class="confidence">信心度: {{ field.value_confidence }}</span>
          </div>
          <div class="field-meta">
            <small>欄位識別: {{ field.field_text }} (相似度: {{ field.field_similarity }})</small>
          </div>
        </div>
      </div>

      <div class="stats">
        <p>成功提取: {{ extractedData.total_extracted }} / {{ extractedData.total_extracted }} 個欄位</p>
      </div>

      <button @click="exportResult">💾 匯出結果</button>
    </div>

    <div v-if="error" class="error">
      ❌ {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const jsonInput = ref('')
const fields = ref(['印表機名稱', '總印張數', '彩色印張數', '黑白印張數', '序號'])
const processing = ref(false)
const extractedData = ref<any>(null)
const error = ref('')

function addField() {
  fields.value.push('')
}

async function extractFields() {
  processing.value = true
  error.value = ''
  
  try {
    const jsonData = JSON.parse(jsonInput.value)
    
    const result = await window.electronAPI.extractFields(
      jsonData,
      fields.value.filter(f => f.trim())
    )
    
    extractedData.value = result
  } catch (err: any) {
    error.value = err.message || '提取失敗'
    console.error('Extraction Error:', err)
  } finally {
    processing.value = false
  }
}

function exportResult() {
  if (!extractedData.value) return
  
  const dataStr = JSON.stringify(extractedData.value, null, 2)
  const blob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  
  const a = document.createElement('a')
  a.href = url
  a.download = 'extracted_fields.json'
  a.click()
  
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.extraction-page {
  max-width: 1000px;
  margin: 0 auto;
}

.extraction-page h2 {
  margin-bottom: 2rem;
  color: #2c3e50;
}

.input-section {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 2rem;
}

textarea {
  width: 100%;
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-family: monospace;
  font-size: 0.875rem;
  resize: vertical;
}

.fields-config {
  margin: 1.5rem 0;
}

.fields-config h4 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.field-inputs {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.field-inputs input {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.field-inputs button {
  align-self: flex-start;
  margin-top: 0.5rem;
}

.result-section {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.extracted-fields {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin: 1rem 0;
}

.field-result {
  padding: 1rem;
  border: 1px solid #ecf0f1;
  border-radius: 8px;
  background: #f8f9fa;
}

.field-name {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.field-value {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.field-value .value {
  font-size: 1.125rem;
  color: #27ae60;
}

.field-value .confidence {
  font-size: 0.875rem;
  color: #7f8c8d;
}

.field-meta {
  font-size: 0.75rem;
  color: #95a5a6;
}

.stats {
  margin: 1rem 0;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.error {
  background: #fee;
  color: #c33;
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
}
</style>
