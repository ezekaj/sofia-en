/**
 * Sofia AI - Unified Production Server
 * Combines calendar interface + Sofia agent + LiveKit integration
 * Single deployment for complete dental assistant system
 */

const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const sqlite3 = require('sqlite3').verbose();
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');
const { spawn } = require('child_process');
const { AccessToken } = require('livekit-server-sdk');
require('dotenv').config();

console.log('🚀 Sofia AI - Unified Production Server Starting...');
console.log('📊 Environment:', process.env.NODE_ENV || 'production');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

const PORT = process.env.PORT || 10000;

// Global variables for Sofia agent management
let sofiaAgent = null;
let isAgentRunning = false;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'dental-calendar/public')));

console.log('🗄️ Setting up SQLite database...');
// Database setup - use dental-calendar database
const dbPath = path.join(__dirname, 'dental-calendar/dental_calendar.db');
const db = new sqlite3.Database(dbPath);

// Create tables if they don't exist
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT UNIQUE NOT NULL,
    email TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    patient_name TEXT NOT NULL,
    phone TEXT,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    end_time TEXT,
    treatment_type TEXT,
    notes TEXT,
    status TEXT DEFAULT 'confirmed',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients (id)
  )`);
});

console.log('✅ Database setup complete');

// Sofia Agent Management Functions
function startSofiaAgent() {
  if (isAgentRunning) {
    console.log('🤖 Sofia agent already running');
    return;
  }

  console.log('🚀 Starting Sofia AI agent...');
  
  sofiaAgent = spawn('python', ['agent.py'], {
    cwd: __dirname,
    env: {
      ...process.env,
      PYTHONPATH: __dirname,
      LIVEKIT_URL: process.env.LIVEKIT_URL || 'wss://sofia-y7ojalkh.livekit.cloud',
      LIVEKIT_API_KEY: process.env.LIVEKIT_API_KEY || 'APILexYWwak6y55',
      LIVEKIT_API_SECRET: process.env.LIVEKIT_API_SECRET || 'ewMkNz2dcz2zRRA6eveAnn8dp8D0kFf7gg1yle06rXxH',
      GOOGLE_API_KEY: process.env.GOOGLE_API_KEY || 'AIzaSyCGXSa68qIQNtp8WEH_zYFF3UjIHS4EW2M'
    }
  });

  sofiaAgent.stdout.on('data', (data) => {
    console.log('🤖 Sofia Agent:', data.toString().trim());
  });

  sofiaAgent.stderr.on('data', (data) => {
    console.error('⚠️ Sofia Agent Error:', data.toString().trim());
  });

  sofiaAgent.on('close', (code) => {
    console.log(`🤖 Sofia Agent exited with code ${code}`);
    isAgentRunning = false;
    
    // Auto-restart agent if it crashes (production resilience)
    if (code !== 0) {
      console.log('🔄 Restarting Sofia Agent in 5 seconds...');
      setTimeout(startSofiaAgent, 5000);
    }
  });

  isAgentRunning = true;
}

function stopSofiaAgent() {
  if (sofiaAgent && isAgentRunning) {
    console.log('🛑 Stopping Sofia Agent...');
    sofiaAgent.kill('SIGTERM');
    isAgentRunning = false;
  }
}

// Health Check Endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'Sofia AI - Unified Production Server',
    version: '1.0.0',
    components: {
      server: 'running',
      database: 'connected',
      sofia_agent: isAgentRunning ? 'running' : 'stopped',
      calendar: 'available'
    },
    uptime: process.uptime()
  });
});

// LiveKit Token Generation Endpoint
app.post('/api/voice/connect', async (req, res) => {
  const { roomName, participantName } = req.body;
  
  try {
    const roomNameFinal = roomName || `dental_room_${Date.now()}`;
    const participantNameFinal = participantName || 'Patient';
    
    // Generate LiveKit JWT token
    const at = new AccessToken(
      process.env.LIVEKIT_API_KEY || 'APILexYWwak6y55',
      process.env.LIVEKIT_API_SECRET || 'ewMkNz2dcz2zRRA6eveAnn8dp8D0kFf7gg1yle06rXxH',
      {
        identity: participantNameFinal,
        name: participantNameFinal,
      }
    );
    
    at.addGrant({
      room: roomNameFinal,
      roomJoin: true,
      canPublish: true,
      canSubscribe: true,
      canPublishData: true,
    });
    
    const token = await at.toJwt();
    
    console.log('🎤 LiveKit JWT token generated for:', participantNameFinal);
    
    // Ensure Sofia agent is running when someone wants to connect
    if (!isAgentRunning) {
      startSofiaAgent();
    }
    
    res.json({
      success: true,
      token: token,
      room_name: roomNameFinal,
      livekit_url: process.env.LIVEKIT_URL || 'wss://sofia-y7ojalkh.livekit.cloud',
      participant_name: participantNameFinal
    });
    
  } catch (error) {
    console.error('❌ Failed to generate LiveKit token:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to generate token: ' + error.message
    });
  }
});

// Sofia Agent Control Endpoints
app.post('/api/sofia/start', (req, res) => {
  startSofiaAgent();
  res.json({
    success: true,
    message: 'Sofia agent starting...',
    status: isAgentRunning ? 'running' : 'starting'
  });
});

app.post('/api/sofia/stop', (req, res) => {
  stopSofiaAgent();
  res.json({
    success: true,
    message: 'Sofia agent stopped',
    status: 'stopped'
  });
});

app.get('/api/sofia/status', (req, res) => {
  res.json({
    status: isAgentRunning ? 'running' : 'stopped',
    message: 'Sofia AI voice assistant for dental practice',
    livekit_connected: true,
    calendar_connected: true,
    agent_running: isAgentRunning
  });
});

// Calendar API Endpoints
app.get('/api/appointments', (req, res) => {
  const sql = `
    SELECT a.*, p.email 
    FROM appointments a 
    LEFT JOIN patients p ON a.patient_id = p.id 
    ORDER BY a.date DESC, a.time DESC
  `;
  
  db.all(sql, [], (err, rows) => {
    if (err) {
      console.error('Database error:', err);
      res.status(500).json({ error: err.message });
      return;
    }
    
    res.json({
      appointments: rows,
      count: rows.length
    });
  });
});

app.post('/api/appointments', (req, res) => {
  const { patientName, phone, email, date, time, treatmentType, notes } = req.body;
  
  console.log('📅 New appointment request:', { patientName, phone, date, time, treatmentType });
  
  // First, insert or get patient
  db.serialize(() => {
    db.run(
      `INSERT OR IGNORE INTO patients (name, phone, email) VALUES (?, ?, ?)`,
      [patientName, phone, email],
      function(err) {
        if (err) {
          console.error('Error inserting patient:', err);
          res.status(500).json({ error: err.message });
          return;
        }
        
        // Get patient ID
        db.get(
          `SELECT id FROM patients WHERE phone = ?`,
          [phone],
          (err, patient) => {
            if (err) {
              console.error('Error fetching patient:', err);
              res.status(500).json({ error: err.message });
              return;
            }
            
            // Insert appointment
            db.run(
              `INSERT INTO appointments (patient_id, patient_name, phone, date, time, treatment_type, notes) 
               VALUES (?, ?, ?, ?, ?, ?, ?)`,
              [patient ? patient.id : null, patientName, phone, date, time, treatmentType || 'General Consultation', notes],
              function(err) {
                if (err) {
                  console.error('Error inserting appointment:', err);
                  res.status(500).json({ error: err.message });
                  return;
                }
                
                const appointment = {
                  id: this.lastID,
                  patient_id: patient ? patient.id : null,
                  patient_name: patientName,
                  phone,
                  date,
                  time,
                  treatment_type: treatmentType || 'General Consultation',
                  notes,
                  status: 'confirmed',
                  created_at: new Date().toISOString()
                };
                
                console.log('✅ Appointment created:', appointment);
                
                // Emit real-time update
                io.emit('appointmentBooked', appointment);
                
                res.json({
                  success: true,
                  appointment,
                  message: 'Appointment booked successfully'
                });
              }
            );
          }
        );
      }
    );
  });
});

// Delete appointment endpoint
app.delete('/api/appointments/:id', (req, res) => {
  const appointmentId = req.params.id;
  
  db.run(
    `DELETE FROM appointments WHERE id = ?`,
    [appointmentId],
    function(err) {
      if (err) {
        console.error('Error deleting appointment:', err);
        res.status(500).json({ error: err.message });
        return;
      }
      
      if (this.changes === 0) {
        res.status(404).json({ error: 'Appointment not found' });
        return;
      }
      
      io.emit('appointmentDeleted', { id: appointmentId });
      
      res.json({
        success: true,
        message: 'Appointment deleted successfully'
      });
    }
  );
});

// Socket.IO for real-time updates
io.on('connection', (socket) => {
  console.log('🔌 Client connected:', socket.id);
  
  socket.on('disconnect', () => {
    console.log('🔌 Client disconnected:', socket.id);
  });
  
  socket.on('sofia-message', (data) => {
    console.log('💬 Sofia message from client:', data);
    socket.broadcast.emit('sofia-response', data);
  });
});

// Serve main application
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'dental-calendar/public/index.html'));
});

// Graceful shutdown handling
process.on('SIGINT', () => {
  console.log('\n🛑 Received SIGINT, shutting down gracefully...');
  stopSofiaAgent();
  db.close((err) => {
    if (err) {
      console.error('Error closing database:', err);
    } else {
      console.log('✅ Database connection closed');
    }
    process.exit(0);
  });
});

process.on('SIGTERM', () => {
  console.log('\n🛑 Received SIGTERM, shutting down gracefully...');
  stopSofiaAgent();
  db.close((err) => {
    if (err) {
      console.error('Error closing database:', err);
    } else {
      console.log('✅ Database connection closed');
    }
    process.exit(0);
  });
});

// Start the unified server
server.listen(PORT, '0.0.0.0', () => {
  console.log('🎉 Sofia AI - Unified Production Server is LIVE!');
  console.log('🌐 Server: http://0.0.0.0:' + PORT);
  console.log('📊 Health: http://0.0.0.0:' + PORT + '/health');
  console.log('🎤 Sofia Status: http://0.0.0.0:' + PORT + '/api/sofia/status');
  console.log('🔌 Socket.IO: Real-time updates enabled');
  console.log('🗄️ Database: SQLite connected');
  console.log('✅ UNIFIED DEPLOYMENT READY');
  
  // Start Sofia agent after server is ready
  console.log('⏳ Starting Sofia AI agent in 3 seconds...');
  setTimeout(startSofiaAgent, 3000);
});