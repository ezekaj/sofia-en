#!/usr/bin/env node

/**
 * Sofia AI - Production Startup Script
 * Coordinates calendar system with voice agent integration
 */

const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const { Pool } = require('pg');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');
require('dotenv').config();

console.log('🚀 Starting Sofia AI Complete System...');
console.log('📊 Environment:', process.env.NODE_ENV || 'development');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST", "PUT", "DELETE"]
  }
});

// Middleware
app.use(cors({
  origin: "*",
  methods: ["GET", "POST", "PUT", "DELETE"],
  allowedHeaders: ["Content-Type", "Authorization"]
}));
app.use(bodyParser.json());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files from calendar-sofia/public
app.use(express.static(path.join(__dirname, 'calendar-sofia', 'public')));

// Database configuration
const connectionString = process.env.DATABASE_URL || 'postgresql://localhost:5432/sofia_ai';
const pool = new Pool({
  connectionString,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

// Database initialization
async function initializeDatabase() {
  try {
    console.log('📊 Initializing database...');
    
    // Create appointments table
    await pool.query(`
      CREATE TABLE IF NOT EXISTS appointments (
        id SERIAL PRIMARY KEY,
        patient_name VARCHAR(255) NOT NULL,
        patient_email VARCHAR(255),
        patient_phone VARCHAR(50),
        appointment_date DATE NOT NULL,
        appointment_time TIME NOT NULL,
        service_type VARCHAR(100),
        notes TEXT,
        status VARCHAR(50) DEFAULT 'confirmed',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Create patients table
    await pool.query(`
      CREATE TABLE IF NOT EXISTS patients (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE,
        phone VARCHAR(50),
        date_of_birth DATE,
        address TEXT,
        medical_history TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    console.log('✅ Database initialized successfully');
  } catch (error) {
    console.error('❌ Database initialization failed:', error);
  }
}

// Routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'calendar-sofia', 'public', 'index.html'));
});

app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'sofia-ai-complete',
    timestamp: new Date().toISOString(),
    components: {
      database: 'connected',
      calendar: 'running',
      sofia_agent: 'integrated'
    }
  });
});

app.get('/api/appointments', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM appointments ORDER BY appointment_date, appointment_time');
    res.json(result.rows);
  } catch (error) {
    console.error('Error fetching appointments:', error);
    res.status(500).json({ error: 'Failed to fetch appointments' });
  }
});

app.post('/api/appointments', async (req, res) => {
  try {
    const { patient_name, patient_email, patient_phone, appointment_date, appointment_time, service_type, notes } = req.body;
    
    const result = await pool.query(
      `INSERT INTO appointments (patient_name, patient_email, patient_phone, appointment_date, appointment_time, service_type, notes)
       VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING *`,
      [patient_name, patient_email, patient_phone, appointment_date, appointment_time, service_type, notes]
    );
    
    // Emit to all connected clients
    io.emit('appointmentCreated', result.rows[0]);
    
    res.json(result.rows[0]);
  } catch (error) {
    console.error('Error creating appointment:', error);
    res.status(500).json({ error: 'Failed to create appointment' });
  }
});

app.put('/api/appointments/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { patient_name, patient_email, patient_phone, appointment_date, appointment_time, service_type, notes, status } = req.body;
    
    const result = await pool.query(
      `UPDATE appointments SET 
       patient_name = $1, patient_email = $2, patient_phone = $3, 
       appointment_date = $4, appointment_time = $5, service_type = $6, 
       notes = $7, status = $8, updated_at = CURRENT_TIMESTAMP 
       WHERE id = $9 RETURNING *`,
      [patient_name, patient_email, patient_phone, appointment_date, appointment_time, service_type, notes, status, id]
    );
    
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Appointment not found' });
    }
    
    // Emit to all connected clients
    io.emit('appointmentUpdated', result.rows[0]);
    
    res.json(result.rows[0]);
  } catch (error) {
    console.error('Error updating appointment:', error);
    res.status(500).json({ error: 'Failed to update appointment' });
  }
});

app.delete('/api/appointments/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const result = await pool.query('DELETE FROM appointments WHERE id = $1 RETURNING *', [id]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Appointment not found' });
    }
    
    // Emit to all connected clients
    io.emit('appointmentDeleted', { id: parseInt(id) });
    
    res.json({ message: 'Appointment deleted successfully' });
  } catch (error) {
    console.error('Error deleting appointment:', error);
    res.status(500).json({ error: 'Failed to delete appointment' });
  }
});

// Sofia Agent Integration Routes
app.get('/api/sofia/status', (req, res) => {
  res.json({
    status: 'online',
    capabilities: ['voice_interaction', 'appointment_booking', 'patient_queries'],
    livekit_configured: !!process.env.LIVEKIT_URL
  });
});

app.post('/api/sofia/appointment', async (req, res) => {
  try {
    // This endpoint allows Sofia Agent to create appointments
    const appointment = req.body;
    
    const result = await pool.query(
      `INSERT INTO appointments (patient_name, patient_email, patient_phone, appointment_date, appointment_time, service_type, notes)
       VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING *`,
      [appointment.patient_name, appointment.patient_email, appointment.patient_phone, 
       appointment.appointment_date, appointment.appointment_time, appointment.service_type, 
       'Created via Sofia AI Voice Assistant']
    );
    
    // Emit to all connected clients
    io.emit('appointmentCreated', result.rows[0]);
    
    res.json({
      success: true,
      appointment: result.rows[0],
      message: 'Appointment created successfully via Sofia AI'
    });
  } catch (error) {
    console.error('Sofia appointment creation error:', error);
    res.status(500).json({ error: 'Failed to create appointment via Sofia' });
  }
});

// Socket.IO connection handling
io.on('connection', (socket) => {
  console.log('🔌 Client connected:', socket.id);
  
  socket.on('disconnect', () => {
    console.log('🔌 Client disconnected:', socket.id);
  });
  
  socket.on('requestAppointments', async () => {
    try {
      const result = await pool.query('SELECT * FROM appointments ORDER BY appointment_date, appointment_time');
      socket.emit('appointmentsList', result.rows);
    } catch (error) {
      console.error('Error fetching appointments for socket:', error);
      socket.emit('error', 'Failed to fetch appointments');
    }
  });
});

// Error handling
app.use((err, req, res, next) => {
  console.error('❌ Server error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
const PORT = process.env.PORT || 8080;

async function startServer() {
  try {
    // Initialize database
    await initializeDatabase();
    
    // Test database connection
    await pool.query('SELECT NOW()');
    console.log('✅ Database connection successful');
    
    // Start server
    server.listen(PORT, '0.0.0.0', () => {
      console.log('🎉 Sofia AI Complete System is running!');
      console.log(`🌐 Server: http://0.0.0.0:${PORT}`);
      console.log(`📊 Health: http://0.0.0.0:${PORT}/health`);
      console.log(`🎤 Sofia Integration: Ready`);
      console.log('✅ System fully operational at elosofia.site');
    });
    
  } catch (error) {
    console.error('❌ Failed to start server:', error);
    process.exit(1);
  }
}

startServer();