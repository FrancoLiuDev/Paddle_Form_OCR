<template>
  <div class="home">
    <div class="hero">
      <h2>歡迎使用 Paddle OCR 桌面應用</h2>
      <p>整合 Python OCR 識別與文字提取功能</p>
    </div>

    <div class="features">
      <div class="feature-card" @click="$router.push('/ocr')">
        <div class="icon">📷</div>
        <h3>OCR 識別</h3>
        <p>上傳圖片進行文字識別</p>
      </div>

      <div class="feature-card" @click="$router.push('/extraction')">
        <div class="icon">📝</div>
        <h3>文字提取</h3>
        <p>從識別結果提取結構化資料</p>
      </div>

      <div class="feature-card">
        <div class="icon">⚙️</div>
        <h3>設定</h3>
        <p>配置 OCR 參數與選項</p>
      </div>
    </div>

    <div class="status">
      <h3>系統狀態</h3>
      <div class="status-item">
        <span>Python 環境：</span>
        <span class="value">{{ pythonVersion || '檢查中...' }}</span>
      </div>
      <div class="status-item">
        <span>Electron 版本：</span>
        <span class="value">{{ electronVersion }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const pythonVersion = ref('')
const electronVersion = ref(process.versions.electron)

onMounted(async () => {
  try {
    const result = await window.electronAPI.getPythonVersion()
    pythonVersion.value = result.version
  } catch (error) {
    console.error('Failed to get Python version:', error)
    pythonVersion.value = '無法取得'
  }
})
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.hero {
  text-align: center;
  padding: 3rem 1rem;
  background: white;
  border-radius: 12px;
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.hero h2 {
  font-size: 2rem;
  margin-bottom: 1rem;
  color: #2c3e50;
}

.hero p {
  font-size: 1.125rem;
  color: #7f8c8d;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.feature-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.feature-card .icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  font-size: 1.25rem;
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.feature-card p {
  color: #7f8c8d;
  font-size: 0.875rem;
}

.status {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.status h3 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.status-item {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid #ecf0f1;
}

.status-item:last-child {
  border-bottom: none;
}

.status-item .value {
  font-weight: 600;
  color: #27ae60;
}
</style>
