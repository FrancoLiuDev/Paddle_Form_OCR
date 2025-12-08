import { app, BrowserWindow, ipcMain } from 'electron'
import path from 'path'
import { spawn } from 'child_process'

// Python backend paths
const isProd = process.env.NODE_ENV === 'production'
const pythonPath = isProd 
  ? path.join(process.resourcesPath, 'python') 
  : 'python3'

let mainWindow: BrowserWindow | null = null

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  })

  // Load the app
  if (process.env.VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL)
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

// IPC Handlers for Python backend

// OCR Recognition
ipcMain.handle('ocr:recognize', async (event, imagePath: string, options: any) => {
  return new Promise((resolve, reject) => {
    const ocrScript = isProd
      ? path.join(process.resourcesPath, 'ocr_backend', 'ocr_parser.py')
      : path.join(__dirname, '../../4_OCR_Recognition/ocr_parser.py')

    const args = [
      ocrScript,
      '-i', imagePath,
      '--output', '-'  // Output to stdout
    ]

    if (options.highSensitivity) args.push('--high-sensitivity')
    if (options.convertFullwidth) args.push('--convert-fullwidth')
    if (options.verbose) args.push('--verbose')

    const python = spawn(pythonPath, args)
    let dataString = ''
    let errorString = ''

    python.stdout.on('data', (data) => {
      dataString += data.toString()
    })

    python.stderr.on('data', (data) => {
      errorString += data.toString()
    })

    python.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(dataString)
          resolve(result)
        } catch (e) {
          reject({ error: 'Failed to parse OCR result', details: e })
        }
      } else {
        reject({ error: 'OCR process failed', stderr: errorString, code })
      }
    })
  })
})

// Text Extraction
ipcMain.handle('extract:fields', async (event, jsonData: any, fields: string[]) => {
  return new Promise((resolve, reject) => {
    const extractScript = isProd
      ? path.join(process.resourcesPath, 'text_extraction', 'extract_fuji_fields_dynamic.py')
      : path.join(__dirname, '../../5_Text_Extraction/extract_fuji_fields_dynamic.py')

    const python = spawn(pythonPath, [extractScript])
    
    // Send JSON data to stdin
    python.stdin.write(JSON.stringify({ data: jsonData, fields }))
    python.stdin.end()

    let dataString = ''
    let errorString = ''

    python.stdout.on('data', (data) => {
      dataString += data.toString()
    })

    python.stderr.on('data', (data) => {
      errorString += data.toString()
    })

    python.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(dataString)
          resolve(result)
        } catch (e) {
          reject({ error: 'Failed to parse extraction result', details: e })
        }
      } else {
        reject({ error: 'Extraction process failed', stderr: errorString, code })
      }
    })
  })
})

// Get Python version info
ipcMain.handle('python:version', async () => {
  return new Promise((resolve, reject) => {
    const python = spawn(pythonPath, ['--version'])
    let dataString = ''

    python.stdout.on('data', (data) => {
      dataString += data.toString()
    })

    python.stderr.on('data', (data) => {
      dataString += data.toString()
    })

    python.on('close', (code) => {
      resolve({ version: dataString.trim(), code })
    })
  })
})
