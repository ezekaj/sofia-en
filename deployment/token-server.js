const express = require('express');
const { AccessToken } = require('livekit-server-sdk');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

// Get from environment or use defaults
const LIVEKIT_API_KEY = process.env.LIVEKIT_API_KEY || 'devkey';
const LIVEKIT_API_SECRET = process.env.LIVEKIT_API_SECRET || 'secret';

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'healthy', service: 'token-server' });
});

// Token generation endpoint
app.post('/api/livekit-token', async (req, res) => {
    try {
        const { identity, name, room } = req.body;
        
        if (!identity || !room) {
            return res.status(400).json({ 
                error: 'Identity and room are required' 
            });
        }
        
        // Create access token
        const token = new AccessToken(
            LIVEKIT_API_KEY,
            LIVEKIT_API_SECRET,
            {
                identity: identity,
                name: name || identity,
                ttl: '4h', // Token valid for 4 hours
            }
        );
        
        // Grant permissions
        token.addGrant({
            room: room,
            roomJoin: true,
            canPublish: true,
            canSubscribe: true,
            canPublishData: true,
        });
        
        const jwt = await token.toJwt();
        
        console.log(`Token generated for ${identity} in room ${room}`);
        
        res.json({ token: jwt });
        
    } catch (error) {
        console.error('Token generation error:', error);
        res.status(500).json({ 
            error: 'Failed to generate token' 
        });
    }
});

const PORT = process.env.PORT || 3006;
app.listen(PORT, () => {
    console.log(`Token server running on port ${PORT}`);
    console.log(`Health check: http://localhost:${PORT}/health`);
});