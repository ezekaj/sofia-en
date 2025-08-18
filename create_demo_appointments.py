#!/usr/bin/env python3
"""
Create demo appointments for presentation
"""

import asyncio
import json
from datetime import datetime, timedelta
import httpx

async def create_appointments():
    """Create sample appointments for demonstration"""
    calendar_url = "http://localhost:3005"
    
    print("\n[CREATING] Demo appointments for presentation...")
    
    demo_appointments = [
        {
            "patient_name": "Emma Johnson",
            "phone": "+44 7700 900001",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": "10:00",
            "end_time": "10:30",
            "treatment_type": "Check-up",
            "notes": "Regular 6-month check-up"
        },
        {
            "patient_name": "James Wilson",
            "phone": "+44 7700 900002",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": "11:00",
            "end_time": "11:45",
            "treatment_type": "Filling",
            "notes": "Upper molar filling"
        },
        {
            "patient_name": "Sarah Brown",
            "phone": "+44 7700 900003",
            "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "time": "14:00",
            "end_time": "15:00",
            "treatment_type": "Cleaning",
            "notes": "Professional dental cleaning"
        },
        {
            "patient_name": "Michael Davis",
            "phone": "+44 7700 900004",
            "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "time": "15:30",
            "end_time": "16:00",
            "treatment_type": "Consultation",
            "notes": "Wisdom tooth consultation"
        },
        {
            "patient_name": "Emily Thompson",
            "phone": "+44 7700 900005",
            "date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
            "time": "09:00",
            "end_time": "10:00",
            "treatment_type": "Root Canal",
            "notes": "Root canal treatment - first session"
        }
    ]
    
    async with httpx.AsyncClient() as client:
        created_count = 0
        for appt in demo_appointments:
            try:
                response = await client.post(
                    f"{calendar_url}/api/appointments",
                    json=appt
                )
                if response.status_code in [200, 201]:
                    print(f"   [OK] Created: {appt['patient_name']} - {appt['treatment_type']} on {appt['date']} at {appt['time']}")
                    created_count += 1
                else:
                    print(f"   [FAIL] Failed: {appt['patient_name']}")
            except Exception as e:
                print(f"   [ERROR] {e}")
    
    print(f"\n[COMPLETE] Created {created_count} demo appointments")
    print("\n[INFO] Open browser to: http://localhost:3005")
    print("[INFO] Calendar is ready for presentation!")
    
    return created_count

if __name__ == "__main__":
    asyncio.run(create_appointments())