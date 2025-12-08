import { contextBridge, ipcRenderer } from 'electron'

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // OCR Operations
  recognizeImage: (imagePath: string, options: any) => 
    ipcRenderer.invoke('ocr:recognize', imagePath, options),
  
  // Text Extraction
  extractFields: (jsonData: any, fields: string[]) => 
    ipcRenderer.invoke('extract:fields', jsonData, fields),
  
  // System Info
  getPythonVersion: () => 
    ipcRenderer.invoke('python:version'),
})

// Type definitions for TypeScript
export interface ElectronAPI {
  recognizeImage: (imagePath: string, options: {
    highSensitivity?: boolean
    convertFullwidth?: boolean
    verbose?: boolean
  }) => Promise<any>
  extractFields: (jsonData: any, fields: string[]) => Promise<any>
  getPythonVersion: () => Promise<{ version: string, code: number }>
}

declare global {
  interface Window {
    electronAPI: ElectronAPI
  }
}
