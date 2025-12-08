<template>
  <div id="app">
    <header class="app-header">
      <h1>🖼️ Paddle OCR Desktop</h1>
      <div class="system-info">
        <span v-if="pythonVersion">Python: {{ pythonVersion }}</span>
      </div>
    </header>

    <main class="app-main">
      <router-view />
    </main>

    <footer class="app-footer">
      <p>Powered by PaddleOCR | Electron + Vue 3 + TypeScript</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

const pythonVersion = ref('')

onMounted(async () => {
  try {
    const result = await window.electronAPI.getPythonVersion()
    pythonVersion.value = result.version
  } catch (error) {
    console.error('Failed to get Python version:', error)
  }
})
</script>

<style scoped>
#app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.app-header h1 {
  margin: 0;
  font-size: 1.5rem;
}

.system-info {
  font-size: 0.875rem;
  opacity: 0.9;
}

.app-main {
  flex: 1;
  overflow: auto;
  padding: 2rem;
  background: #f5f5f5;
}

.app-footer {
  background: #2c3e50;
  color: #ecf0f1;
  text-align: center;
  padding: 1rem;
  font-size: 0.875rem;
}

.app-footer p {
  margin: 0;
}
</style>
