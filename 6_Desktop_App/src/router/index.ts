import { createRouter, createWebHashHistory } from 'vue-router'
import Home from '../views/Home.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/ocr',
    name: 'OCR',
    component: () => import('../views/OCRPage.vue')
  },
  {
    path: '/extraction',
    name: 'Extraction',
    component: () => import('../views/ExtractionPage.vue')
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
