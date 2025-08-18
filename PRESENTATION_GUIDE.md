# 🎯 SOFIA PRESENTATION GUIDE
## Dr. Smith's Dental Practice - English Version

---

## ✅ SYSTEM STATUS

### Services Running:
- ✅ **Dental Calendar**: http://localhost:3005
- ✅ **Sofia Agent**: Console mode active
- ✅ **Demo Appointments**: 5 appointments created

---

## 🎬 PRESENTATION FLOW (10-15 minutes)

### 1. **Introduction** (1 minute)
"Today I'll demonstrate Sofia, an AI-powered dental assistant for Dr. Smith's Dental Practice. Sofia handles appointment booking, patient inquiries, and emergency triage - all in natural English conversation."

### 2. **Show Calendar System** (2 minutes)
- Open: http://localhost:3005
- Show existing appointments
- Click "New Appointment" to show manual booking
- Highlight real-time updates

### 3. **Demonstrate Sofia Console** (5 minutes)

#### Test Conversation 1: Basic Booking
```
You: "I need to book an appointment"
Sofia: [Will ask what it's for]
You: "I need a check-up"
Sofia: [Will check availability]
You: "My name is John Smith"
Sofia: [Will confirm appointment]
```

#### Test Conversation 2: Emergency Handling
```
You: "I have severe tooth pain"
Sofia: [Will ask pain scale 1-10]
You: "It's about an 8"
Sofia: [Will prioritize and find urgent slot]
```

#### Test Conversation 3: Information Request
```
You: "What services do you offer?"
Sofia: [Will list dental services]
You: "How much does a filling cost?"
Sofia: [Will provide pricing information]
```

### 4. **Key Features to Highlight** (3 minutes)
- ✨ **Natural Language**: No rigid scripts
- ⏰ **Time Awareness**: Greets based on time of day (CET)
- 🚨 **Emergency Protocol**: Pain scale assessment
- 📅 **Smart Scheduling**: Finds best available times
- 🔚 **Auto-End**: Recognizes goodbye and ends call
- 🏥 **Practice Branding**: Always mentions Dr. Smith's Dental Practice

### 5. **Technical Overview** (2 minutes)
- **AI Model**: Google Gemini for natural conversation
- **Voice**: LiveKit for real-time voice processing
- **Database**: SQLite for appointment storage
- **Architecture**: Microservices with Docker support
- **Language**: Fully localized to English

### 6. **Q&A** (2 minutes)

---

## 🎮 CONSOLE COMMANDS

In the Sofia console window, you can type messages to interact:

1. Type your message and press Enter
2. Sofia will respond with voice (if LiveKit is running) and text
3. Say "goodbye" to end the conversation

---

## 🔧 TROUBLESHOOTING

### If Calendar Not Working:
```bash
cd elo-english/dental-calendar
npm start
```

### If Sofia Not Responding:
```bash
cd elo-english
python agent.py console
```

### To Add More Test Appointments:
```bash
cd elo-english
python create_demo_appointments.py
```

---

## 📊 DEMO DATA

### Test Patients Created:
1. **Emma Johnson** - Check-up today at 10:00
2. **James Wilson** - Filling today at 11:00
3. **Sarah Brown** - Cleaning tomorrow at 14:00
4. **Michael Davis** - Consultation tomorrow at 15:30
5. **Emily Thompson** - Root Canal in 2 days at 09:00

### Available Services:
- Check-ups (£50)
- Cleanings (£80)
- Fillings (£150-300)
- Root Canals (£500-800)
- Crowns (£600-1000)
- Emergency appointments

---

## 💡 PRESENTATION TIPS

1. **Start Strong**: Show the calendar first - visual impact
2. **Keep It Natural**: Have real conversations with Sofia
3. **Show Errors**: If something fails, explain it's a demo environment
4. **Emphasize English**: Point out natural language understanding
5. **Time Awareness**: Note how Sofia knows it's evening (CET)
6. **Emergency Feature**: Highlight the pain scale triage

---

## 🎯 KEY SELLING POINTS

✅ **24/7 Availability** - Never miss a patient call
✅ **Reduces Staff Workload** - Handles routine bookings
✅ **Emergency Triage** - Prioritizes urgent cases
✅ **Professional Image** - Consistent, polite service
✅ **Data Integration** - Syncs with practice systems
✅ **Scalable** - Handles multiple calls simultaneously

---

## 📞 EXAMPLE FULL CONVERSATION

```
Sofia: "Good evening! Thank you for calling Dr. Smith's Dental Practice. 
        I'm Sofia, your virtual assistant. How may I help you today?"

Patient: "Hi, I need to book an appointment for a toothache"

Sofia: "I'm sorry to hear you're experiencing a toothache. 
        On a scale of 1 to 10, how severe is your pain?"

Patient: "It's about a 6"

Sofia: "I understand you're in moderate pain. Let me find the earliest 
        available appointment for you. What's your name please?"

Patient: "David Miller"

Sofia: "Thank you, Mr. Miller. I can offer you an appointment tomorrow 
        at 9:00 AM or 2:30 PM. Which would work better for you?"

Patient: "Tomorrow at 9 AM would be perfect"

Sofia: "Perfect! I've booked you for tomorrow at 9:00 AM with Dr. Smith 
        for your toothache. Could I have a contact phone number?"

Patient: "It's 07700 900123"

Sofia: "Thank you. Your appointment is confirmed for tomorrow, 
        August 14th at 9:00 AM. Is there anything else I can help you with?"

Patient: "No, that's all. Thank you!"

Sofia: "Perfect! Thank you for calling Dr. Smith's Dental Practice. 
        Have a great evening and goodbye!"

[Call automatically ends]
```

---

## 🚀 READY TO PRESENT!

**Remember**: The system is live and working. Just interact naturally with Sofia and show off the calendar integration. Good luck with your presentation!

---

**Quick Access Links:**
- Calendar: http://localhost:3005
- Test Page: Open `test_calendar.html` in browser
- Console: Terminal window running `agent.py console`