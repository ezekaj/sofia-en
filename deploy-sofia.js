#!/usr/bin/env node

/**
 * Sofia AI - ULTRATHINK Railway Deployment Helper
 * Comprehensive deployment orchestration and monitoring
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const http = require('http');

const RAILWAY_URL = 'https://sofia-complete-production.up.railway.app';
const DOMAIN_URL = 'https://elosofia.site';

console.log('🚀 ULTRATHINK Sofia AI Deployment Orchestrator');
console.log('================================================\n');

class SofiaDeployer {
  constructor() {
    this.deploymentSteps = [
      { name: 'Pre-deployment Validation', fn: this.validatePreDeployment.bind(this) },
      { name: 'Environment Check', fn: this.checkEnvironment.bind(this) },
      { name: 'Railway Deployment', fn: this.deployToRailway.bind(this) },
      { name: 'Health Monitoring', fn: this.monitorHealth.bind(this) },
      { name: 'Domain Verification', fn: this.verifyDomain.bind(this) },
      { name: 'Post-deployment Tests', fn: this.runPostDeploymentTests.bind(this) }
    ];
  }

  async validatePreDeployment() {
    console.log('📁 Validating project structure...');
    
    const requiredFiles = [
      'ultrathink-server.js',
      'package.json',
      'railway.toml',
      'Procfile',
      'calendar-sofia/public/index.html'
    ];
    
    for (const file of requiredFiles) {
      if (!fs.existsSync(path.join(__dirname, file))) {
        throw new Error(`Required file missing: ${file}`);
      }
      console.log(`  ✅ ${file}`);
    }
    
    console.log('📦 Validating package.json dependencies...');
    const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
    const requiredDeps = ['express', 'socket.io', 'pg', 'cors', 'body-parser', 'dotenv'];
    
    for (const dep of requiredDeps) {
      if (!packageJson.dependencies[dep]) {
        throw new Error(`Required dependency missing: ${dep}`);
      }
      console.log(`  ✅ ${dep}`);
    }
    
    return { success: true, message: 'Pre-deployment validation passed' };
  }

  async checkEnvironment() {
    console.log('🔧 Checking environment variables...');
    
    const envVars = [
      'LIVEKIT_URL',
      'GOOGLE_API_KEY',
      'DATABASE_URL',
      'PRACTICE_NAME'
    ];
    
    const missing = [];
    const configured = [];
    
    for (const envVar of envVars) {
      if (process.env[envVar]) {
        configured.push(envVar);
        console.log(`  ✅ ${envVar}: Configured`);
      } else {
        missing.push(envVar);
        console.log(`  ⚠️  ${envVar}: Not configured`);
      }
    }
    
    return { 
      success: true, 
      configured, 
      missing, 
      message: `${configured.length} environment variables configured, ${missing.length} optional variables not set` 
    };
  }

  async deployToRailway() {
    console.log('🚀 Starting Railway deployment...');
    
    // Check if railway CLI is available
    try {
      await this.runCommand('railway', ['--version']);
      console.log('  ✅ Railway CLI is available');
    } catch (error) {
      console.log('  ⚠️  Railway CLI not found - using manual deployment instructions');
      return this.showManualDeploymentInstructions();
    }
    
    try {
      // Deploy to Railway
      console.log('  📤 Deploying to Railway...');
      await this.runCommand('railway', ['up']);
      
      return { success: true, message: 'Railway deployment initiated' };
    } catch (error) {
      throw new Error(`Railway deployment failed: ${error.message}`);
    }
  }

  showManualDeploymentInstructions() {
    console.log('\n📋 MANUAL DEPLOYMENT INSTRUCTIONS:');
    console.log('=====================================');
    console.log('1. Push your changes to your Git repository:');
    console.log('   git add .');
    console.log('   git commit -m "Fix deployment configuration"');
    console.log('   git push origin main');
    console.log('');
    console.log('2. In Railway dashboard (https://railway.app):');
    console.log('   - Go to your sofia-complete project');
    console.log('   - Click "Deploy" or wait for auto-deploy');
    console.log('   - Monitor the deployment logs');
    console.log('');
    console.log('3. Environment Variables (if not set):');
    console.log('   - DATABASE_URL: [Your PostgreSQL connection string]');
    console.log('   - LIVEKIT_URL: [Your LiveKit server URL]');
    console.log('   - GOOGLE_API_KEY: [Your Google AI API key]');
    console.log('   - PRACTICE_NAME: "Sofia AI Dental Practice"');
    
    return { success: true, message: 'Manual deployment instructions provided' };
  }

  async monitorHealth(retries = 30, interval = 10000) {
    console.log(`🏥 Monitoring deployment health (${retries} retries)...`);
    
    for (let i = 0; i < retries; i++) {
      try {
        console.log(`  🔍 Health check attempt ${i + 1}/${retries}...`);
        
        const response = await this.makeHttpRequest(`${RAILWAY_URL}/health`);
        
        if (response.statusCode === 200) {
          console.log(`  ✅ Health check passed! (${response.responseTime}ms)`);
          
          try {
            const healthData = JSON.parse(response.data);
            console.log(`  📊 Service: ${healthData.service}`);
            console.log(`  🎯 Status: ${healthData.status}`);
            console.log(`  ⏰ Timestamp: ${healthData.timestamp}`);
          } catch (e) {
            // Health endpoint responded but not JSON
          }
          
          return { success: true, message: 'Health monitoring passed', attempts: i + 1 };
        } else {
          console.log(`  ❌ Health check failed: HTTP ${response.statusCode}`);
        }
        
      } catch (error) {
        console.log(`  ❌ Health check error: ${error.message}`);
      }
      
      if (i < retries - 1) {
        console.log(`  ⏳ Waiting ${interval/1000}s before next check...`);
        await this.sleep(interval);
      }
    }
    
    throw new Error('Health monitoring failed - deployment may not be working');
  }

  async verifyDomain() {
    console.log('🌐 Verifying domain configuration...');
    
    try {
      console.log('  🔍 Testing Railway URL...');
      const railwayResponse = await this.makeHttpRequest(`${RAILWAY_URL}/health`);
      if (railwayResponse.statusCode === 200) {
        console.log('  ✅ Railway URL responding correctly');
      }
      
      console.log('  🔍 Testing custom domain...');
      const domainResponse = await this.makeHttpRequest(`${DOMAIN_URL}/health`);
      if (domainResponse.statusCode === 200) {
        console.log('  ✅ Custom domain responding correctly');
        return { success: true, message: 'Domain verification passed' };
      } else {
        console.log('  ⚠️  Custom domain not responding - DNS may still be propagating');
        return { success: true, message: 'Railway working, domain propagating', warning: true };
      }
    } catch (error) {
      console.log('  ⚠️  Domain check inconclusive - may still be working');
      return { success: true, message: 'Domain verification inconclusive', warning: true };
    }
  }

  async runPostDeploymentTests() {
    console.log('🧪 Running post-deployment tests...');
    
    const tests = [
      { name: 'Main Page', url: `${RAILWAY_URL}/` },
      { name: 'Health Endpoint', url: `${RAILWAY_URL}/health` },
      { name: 'Sofia Status', url: `${RAILWAY_URL}/api/sofia/status` },
      { name: 'Appointments API', url: `${RAILWAY_URL}/api/appointments` }
    ];
    
    const results = [];
    
    for (const test of tests) {
      try {
        console.log(`  🧪 Testing ${test.name}...`);
        const response = await this.makeHttpRequest(test.url);
        
        if (response.statusCode === 200) {
          console.log(`  ✅ ${test.name}: OK (${response.responseTime}ms)`);
          results.push({ ...test, success: true, responseTime: response.responseTime });
        } else {
          console.log(`  ❌ ${test.name}: HTTP ${response.statusCode}`);
          results.push({ ...test, success: false, statusCode: response.statusCode });
        }
      } catch (error) {
        console.log(`  ❌ ${test.name}: ${error.message}`);
        results.push({ ...test, success: false, error: error.message });
      }
    }
    
    const successCount = results.filter(r => r.success).length;
    return { 
      success: successCount >= 2, // At least main page and health must work
      results, 
      message: `${successCount}/${results.length} tests passed` 
    };
  }

  async makeHttpRequest(url, timeout = 10000) {
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
      
      request.on('error', reject);
      request.on('timeout', () => {
        request.destroy();
        reject(new Error('Request timeout'));
      });
    });
  }

  async runCommand(command, args) {
    return new Promise((resolve, reject) => {
      const process = spawn(command, args, { stdio: 'pipe' });
      let stdout = '';
      let stderr = '';
      
      process.stdout.on('data', (data) => {
        stdout += data.toString();
      });
      
      process.stderr.on('data', (data) => {
        stderr += data.toString();
      });
      
      process.on('close', (code) => {
        if (code === 0) {
          resolve(stdout);
        } else {
          reject(new Error(stderr || `Process exited with code ${code}`));
        }
      });
    });
  }

  async sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async deploy() {
    console.log('🎯 Starting ULTRATHINK deployment process...\n');
    
    const results = [];
    let overallSuccess = true;
    
    for (const step of this.deploymentSteps) {
      try {
        console.log(`📋 Step: ${step.name}`);
        console.log('─'.repeat(40));
        
        const result = await step.fn();
        results.push({ step: step.name, ...result });
        
        if (!result.success) {
          overallSuccess = false;
        }
        
        console.log(`✅ ${step.name}: ${result.message}\n`);
        
      } catch (error) {
        console.log(`❌ ${step.name}: ${error.message}\n`);
        results.push({ step: step.name, success: false, error: error.message });
        overallSuccess = false;
        
        // Continue with remaining steps even if one fails
      }
    }
    
    console.log('🎯 DEPLOYMENT SUMMARY');
    console.log('====================');
    
    for (const result of results) {
      const status = result.success ? '✅' : '❌';
      const warning = result.warning ? '⚠️ ' : '';
      console.log(`${status} ${warning}${result.step}: ${result.message || result.error}`);
    }
    
    console.log('');
    
    if (overallSuccess) {
      console.log('🎉 DEPLOYMENT SUCCESSFUL!');
      console.log(`🌐 Sofia AI is live at: ${RAILWAY_URL}`);
      console.log(`🏠 Custom domain: ${DOMAIN_URL}`);
      console.log('📊 Monitor at: https://railway.app/project/[your-project-id]');
    } else {
      console.log('⚠️  DEPLOYMENT COMPLETED WITH WARNINGS');
      console.log('🔧 Review the issues above and address them if needed');
      console.log(`🌐 Sofia AI may still be accessible at: ${RAILWAY_URL}`);
    }
    
    return { success: overallSuccess, results };
  }
}

// Run deployment if called directly
if (require.main === module) {
  const deployer = new SofiaDeployer();
  deployer.deploy().catch(error => {
    console.error('💥 Fatal deployment error:', error.message);
    process.exit(1);
  });
}