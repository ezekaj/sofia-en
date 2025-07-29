# Sofia AI - Quick Deployment Guide

## 🚀 Deploy in Under 2 Hours

This guide helps you deploy Sofia AI's voice mode for investor demos using managed services.

## Prerequisites (30 minutes)

1. **LiveKit Cloud Account**
   - Sign up at https://cloud.livekit.io
   - Create a project and get credentials

2. **Railway Account**
   - Sign up at https://railway.app
   - Add a payment method (required for deployment)

3. **Google Cloud API Key**
   - Get from https://console.cloud.google.com
   - Enable Speech-to-Text API

## Quick Start (1 hour)

### Option 1: Automated Deployment

```bash
# Set your credentials
export LIVEKIT_URL="wss://your-project.livekit.cloud"
export LIVEKIT_API_KEY="your-api-key"
export LIVEKIT_API_SECRET="your-api-secret"
export GOOGLE_API_KEY="your-google-key"

# Run deployment script
cd deployment
chmod +x deploy.sh
./deploy.sh
```

### Option 2: Manual Deployment

#### 1. Deploy Sofia Agent
```bash
cd elo-deu
railway login
railway init --name sofia-agent
railway up
railway domain
```

#### 2. Deploy Calendar Backend
```bash
cd dental-calendar
railway init --name dental-calendar
railway up
railway domain
```

#### 3. Deploy Token Server (Optional)
```bash
cd deployment
railway init --name sofia-token-server
railway up
railway domain
```

## Configuration

### Environment Variables

**Sofia Agent:**
```
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your-key
LIVEKIT_API_SECRET=your-secret
GOOGLE_API_KEY=your-google-key
CALENDAR_URL=https://your-calendar.railway.app
```

**Calendar Backend:**
```
PORT=3005
NODE_ENV=production
DATABASE_URL=file:./data/dental.db
JWT_SECRET=your-secret
```

## Testing Your Deployment

1. **Update Demo Frontend**
   - Edit `demo-frontend.html`
   - Update `LIVEKIT_URL` and `TOKEN_ENDPOINT`

2. **Open in Browser**
   - Open `demo-frontend.html`
   - Click "Mit Sofia sprechen"
   - Allow microphone access
   - Say "Hallo" to start

## Monitoring

### Health Checks
```bash
# Check all services
./monitor.sh

# View logs
railway logs --service sofia-agent
railway logs --service dental-calendar
```

### Railway Dashboard
- Real-time metrics
- Deployment history
- Environment variables
- Scaling controls

## Troubleshooting

### Common Issues

1. **Sofia not responding**
   - Check LiveKit credentials
   - Verify Google API key
   - Check logs: `railway logs`

2. **Calendar errors**
   - Ensure DATABASE_URL is set
   - Check calendar service health
   - Verify CORS settings

3. **Connection issues**
   - Verify all URLs are HTTPS
   - Check network connectivity
   - Ensure services are running

### Quick Fixes

```bash
# Restart service
railway restart --service sofia-agent

# Update environment variable
railway variables set KEY=value --service sofia-agent

# Scale up
railway scale --min=2 --max=5 --service sofia-agent
```

## Cost Breakdown

### Monthly Estimates
- **Low Usage (Demos)**: ~$15-25
  - LiveKit: Free tier
  - Railway: $10 + minimal usage

- **Medium Usage (Pilot)**: ~$80-150
  - LiveKit: ~$50-100
  - Railway: ~$30-50

## Production Checklist

- [ ] LiveKit Cloud account created
- [ ] Railway projects deployed
- [ ] Environment variables configured
- [ ] Health checks passing
- [ ] Demo frontend working
- [ ] Monitoring set up
- [ ] Backup plan ready

## Support

For deployment issues:
1. Check Railway logs
2. Verify environment variables
3. Test health endpoints
4. Review error messages

## Next Steps

1. **Custom Domain**
   ```bash
   railway domain set sofia.yourdomain.com
   ```

2. **SSL Certificate**
   - Automatically handled by Railway

3. **Scaling**
   ```bash
   railway scale --min=2 --max=10
   ```

4. **Monitoring**
   - Set up alerts in Railway
   - Configure uptime monitoring

Remember: This setup is optimized for demos. For production, consider additional security, monitoring, and scaling configurations.