#!/usr/bin/env node

/**
 * 构建分析脚本
 * 分析生产构建的文件大小和压缩效果
 */

import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'
import zlib from 'zlib'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const BUILD_DIR = path.resolve(__dirname, '../../feishu_bot/web_admin/static')

// 颜色输出
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

function getGzipSize(filePath) {
  const content = fs.readFileSync(filePath)
  return zlib.gzipSync(content).length
}

function getBrotliSize(filePath) {
  const content = fs.readFileSync(filePath)
  return zlib.brotliCompressSync(content).length
}

function analyzeDirectory(dir, prefix = '') {
  const files = []
  
  function walk(currentDir, currentPrefix) {
    const items = fs.readdirSync(currentDir)
    
    for (const item of items) {
      const fullPath = path.join(currentDir, item)
      const stat = fs.statSync(fullPath)
      
      if (stat.isDirectory()) {
        walk(fullPath, path.join(currentPrefix, item))
      } else if (stat.isFile() && !item.endsWith('.gz') && !item.endsWith('.br')) {
        const ext = path.extname(item)
        if (['.js', '.css', '.html'].includes(ext)) {
          const relativePath = path.join(currentPrefix, item)
          const originalSize = stat.size
          const gzipSize = getGzipSize(fullPath)
          const brotliSize = getBrotliSize(fullPath)
          
          files.push({
            path: relativePath,
            ext,
            originalSize,
            gzipSize,
            brotliSize,
            gzipRatio: ((1 - gzipSize / originalSize) * 100).toFixed(1),
            brotliRatio: ((1 - brotliSize / originalSize) * 100).toFixed(1)
          })
        }
      }
    }
  }
  
  walk(dir, prefix)
  return files
}

function printAnalysis() {
  console.log(`${colors.bright}${colors.cyan}`)
  console.log('╔════════════════════════════════════════════════════════════════╗')
  console.log('║           前端构建分析报告                                      ║')
  console.log('╚════════════════════════════════════════════════════════════════╝')
  console.log(colors.reset)
  
  if (!fs.existsSync(BUILD_DIR)) {
    console.log(`${colors.yellow}⚠ 构建目录不存在: ${BUILD_DIR}${colors.reset}`)
    console.log(`${colors.yellow}请先运行: npm run build${colors.reset}`)
    return
  }
  
  const files = analyzeDirectory(BUILD_DIR)
  
  if (files.length === 0) {
    console.log(`${colors.yellow}⚠ 未找到任何文件${colors.reset}`)
    return
  }
  
  // 按文件类型分组
  const byType = {
    '.js': [],
    '.css': [],
    '.html': []
  }
  
  files.forEach(file => {
    byType[file.ext].push(file)
  })
  
  // 打印每种类型的文件
  Object.entries(byType).forEach(([ext, typeFiles]) => {
    if (typeFiles.length === 0) return
    
    const typeName = {
      '.js': 'JavaScript',
      '.css': 'CSS',
      '.html': 'HTML'
    }[ext]
    
    console.log(`\n${colors.bright}${colors.blue}${typeName} 文件:${colors.reset}`)
    console.log('─'.repeat(80))
    
    typeFiles.forEach(file => {
      console.log(`\n${colors.green}📄 ${file.path}${colors.reset}`)
      console.log(`   原始大小:    ${formatSize(file.originalSize)}`)
      console.log(`   Gzip:        ${formatSize(file.gzipSize)} ${colors.cyan}(减少 ${file.gzipRatio}%)${colors.reset}`)
      console.log(`   Brotli:      ${formatSize(file.brotliSize)} ${colors.cyan}(减少 ${file.brotliRatio}%)${colors.reset}`)
    })
  })
  
  // 总计
  const totalOriginal = files.reduce((sum, f) => sum + f.originalSize, 0)
  const totalGzip = files.reduce((sum, f) => sum + f.gzipSize, 0)
  const totalBrotli = files.reduce((sum, f) => sum + f.brotliSize, 0)
  
  console.log(`\n${colors.bright}${colors.yellow}总计:${colors.reset}`)
  console.log('─'.repeat(80))
  console.log(`   原始大小:    ${formatSize(totalOriginal)}`)
  console.log(`   Gzip 总计:   ${formatSize(totalGzip)} ${colors.cyan}(减少 ${((1 - totalGzip / totalOriginal) * 100).toFixed(1)}%)${colors.reset}`)
  console.log(`   Brotli 总计: ${formatSize(totalBrotli)} ${colors.cyan}(减少 ${((1 - totalBrotli / totalOriginal) * 100).toFixed(1)}%)${colors.reset}`)
  
  // 检查预压缩文件
  console.log(`\n${colors.bright}${colors.blue}预压缩文件检查:${colors.reset}`)
  console.log('─'.repeat(80))
  
  const gzipFiles = files.filter(f => fs.existsSync(path.join(BUILD_DIR, f.path + '.gz')))
  const brotliFiles = files.filter(f => fs.existsSync(path.join(BUILD_DIR, f.path + '.br')))
  
  console.log(`   Gzip 文件:   ${gzipFiles.length}/${files.length} ${gzipFiles.length === files.length ? '✅' : '⚠️'}`)
  console.log(`   Brotli 文件: ${brotliFiles.length}/${files.length} ${brotliFiles.length === files.length ? '✅' : '⚠️'}`)
  
  // 建议
  console.log(`\n${colors.bright}${colors.green}优化建议:${colors.reset}`)
  console.log('─'.repeat(80))
  
  const largeFiles = files.filter(f => f.originalSize > 500 * 1024)
  if (largeFiles.length > 0) {
    console.log(`   ⚠️  发现 ${largeFiles.length} 个大文件 (>500KB):`)
    largeFiles.forEach(f => {
      console.log(`      - ${f.path}: ${formatSize(f.originalSize)}`)
    })
    console.log(`   建议: 考虑进一步拆分代码或使用懒加载`)
  } else {
    console.log(`   ✅ 所有文件大小合理`)
  }
  
  if (gzipFiles.length < files.length || brotliFiles.length < files.length) {
    console.log(`   ⚠️  部分文件缺少预压缩版本`)
    console.log(`   建议: 确保 vite-plugin-compression 正确配置`)
  } else {
    console.log(`   ✅ 所有文件都有预压缩版本`)
  }
  
  console.log(`\n${colors.bright}${colors.cyan}分析完成！${colors.reset}\n`)
}

printAnalysis()
