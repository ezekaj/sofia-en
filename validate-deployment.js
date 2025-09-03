#!/usr/bin/env node

/**
 * Sofia AI - ULTRATHINK Deployment Validator
 * Validates deployment health and provides detailed diagnostics
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 8080;
const HOST = process.env.RAILWAY_STATIC_URL || 'localhost';
const BASE_URL = process.env.RAILWAY_STATIC_URL ? `https://${HOST}` : `http://localhost:${PORT}`;

console.log('🔍 ULTRATHINK Deployment Validator Starting...');
console.log(`🌐 Testing: ${BASE_URL}`);

// Test endpoints to validate
const endpoints = [
  { path: '/health', name: 'Health Check', critical: true },
  { path: '/', name: 'Main Page', critical: true },
  { path: '/api/sofia/status', name: 'Sofia AI Status', critical: false },
  { path: '/api/appointments', name: 'Appointments API', critical: false }
];

async function makeRequest(url, timeout = 5000) {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    
    const request = http.get(url, { timeout }, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        const responseTime = Date.now() - startTime;
        resolve({
          statusCode: res.statusCode,
          data,
          responseTime,
          headers: res.headers
        });
      });
    });
    
    request.on('error', (error) => {
      reject(error);
    });
    
    request.on('timeout', () => {
      request.destroy();
      reject(new Error('Request timeout'));
    });
  });
}

async function validateEndpoint(endpoint) {
  try {
    console.log(`🧪 Testing ${endpoint.name} at ${endpoint.path}...`);
    
    const response = await makeRequest(`${BASE_URL}${endpoint.path}`);
    
    if (response.statusCode === 200) {
      console.log(`  ✅ ${endpoint.name}: OK (${response.responseTime}ms)`);
      return { success: true, responseTime: response.responseTime, data: response.data };
    } else {
      console.log(`  ❌ ${endpoint.name}: HTTP ${response.statusCode}`);
      return { success: false, statusCode: response.statusCode, critical: endpoint.critical };
    }
  } catch (error) {
    console.log(`  ❌ ${endpoint.name}: ${error.message}`);
    return { success: false, error: error.message, critical: endpoint.critical };
  }
}

async function validateFileStructure() {
  console.log('📁 Validating file structure...');
  
  const requiredFiles = [
    'ultrathink-server.js',
    'package.json',
    'calendar-sofia/public/index.html',
    'railway.toml'
  ];
  
  const results = [];
  
  for (const file of requiredFiles) {
    const filePath = path.join(__dirname, file);
    if (fs.existsSync(filePath)) {
      console.log(`  ✅ ${file}: Found`);
      results.push({ file, exists: true });
    } else {
      console.log(`  ❌ ${file}: Missing`);
      results.push({ file, exists: false });
    }
  }
  
  return results;
}

async function validateEnvironment() {
  console.log('🔧 Validating environment configuration...');
  
  const envVars = [
    { name: 'PORT', required: false, value: process.env.PORT },
    { name: 'NODE_ENV', required: false, value: process.env.NODE_ENV },
    { name: 'DATABASE_URL', required: false, value: process.env.DATABASE_URL },
    { name: 'LIVEKIT_URL', required: false, value: process.env.LIVEKIT_URL },
    { name: 'GOOGLE_API_KEY', required: false, value: process.env.GOOGLE_API_KEY }
  ];
  
  const results = [];
  
  for (const env of envVars) {
    if (env.value) {
      console.log(`  ✅ ${env.name}: Configured`);
      results.push({ name: env.name, configured: true });
    } else if (env.required) {
      console.log(`  ❌ ${env.name}: Missing (Required)`);
      results.push({ name: env.name, configured: false, required: true });
    } else {
      console.log(`  ⚠️  ${env.name}: Not configured (Optional)`);
      results.push({ name: env.name, configured: false, required: false });
    }
  }
  
  return results;
}

async function runFullValidation() {
  console.log('🎯 Starting ULTRATHINK Deployment Validation...\n');
  
  // 1. File structure validation
  const fileResults = await validateFileStructure();
  console.log('');
  
  // 2. Environment validation
  const envResults = await validateEnvironment();
  console.log('');
  
  // 3. Endpoint validation
  console.log('🌐 Testing endpoints...');
  const endpointResults = [];
  
  for (const endpoint of endpoints) {
    const result = await validateEndpoint(endpoint);
    endpointResults.push({ ...endpoint, result });
  }
  
  console.log('');
  
  // Generate report
  const report = {
    timestamp: new Date().toISOString(),
    fileStructure: fileResults,
    environment: envResults,
    endpoints: endpointResults,
    summary: {
      filesOK: fileResults.filter(f => f.exists).length,
      totalFiles: fileResults.length,
      endpointsOK: endpointResults.filter(e => e.result.success).length,
      totalEndpoints: endpointResults.length,
      criticalFailures: endpointResults.filter(e => !e.result.success && e.critical).length
    }
  };
  
  console.log('📊 VALIDATION SUMMARY:');
  console.log(`  📁 Files: ${report.summary.filesOK}/${report.summary.totalFiles} OK`);
  console.log(`  🌐 Endpoints: ${report.summary.endpointsOK}/${report.summary.totalEndpoints} OK`);
  console.log(`  🔥 Critical Failures: ${report.summary.criticalFailures}`);
  
  if (report.summary.criticalFailures === 0 && report.summary.filesOK === report.summary.totalFiles) {
    console.log('\n🎉 VALIDATION SUCCESSFUL - Deployment is healthy!');
    process.exit(0);
  } else {
    console.log('\n❌ VALIDATION FAILED - Critical issues detected');
    console.log('🔧 Fix the issues above and try again');
    process.exit(1);
  }
}

// Handle both direct execution and Railway health checks
if (process.argv.includes('--health-check')) {
  // Quick health check for Railway
  makeRequest(`${BASE_URL}/health`)
    .then((response) => {
      if (response.statusCode === 200) {
        console.log('✅ Health check passed');
        process.exit(0);
      } else {
        console.log(`❌ Health check failed: HTTP ${response.statusCode}`);
        process.exit(1);
      }
    })
    .catch((error) => {
      console.log(`❌ Health check failed: ${error.message}`);
      process.exit(1);
    });
} else {
  // Full validation
  runFullValidation();
}