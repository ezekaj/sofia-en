#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Quick test for intelligent reason detection
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_intelligent_reason():
    """Test the intelligent reason detection"""
    try:
        from dental_tools import intelligente_terminanfrage
        
        print("🧪 Testing intelligent reason detection...")
        
        # Test case where reason is already clear
        result = await intelligente_terminanfrage(
            context=None,
            patient_anfrage="Ich habe starke Schmerzen"
        )
        
        print(f"Input: 'Ich habe starke Schmerzen'")
        print(f"Output: {result}")
        
        # Check if it asks for reason (it shouldn't)
        asks_for_reason = "worum geht es denn" in result.lower()
        has_appointment = "soll ich" in result.lower() and "buchen" in result.lower()
        
        if not asks_for_reason and has_appointment:
            print("✅ CORRECT: Direct appointment suggestion without asking for reason")
            return True
        else:
            print("❌ PROBLEM: Still asking for reason or no appointment suggestion")
            if asks_for_reason:
                print("   - Still asks 'Worum geht es denn?'")
            if not has_appointment:
                print("   - No appointment suggestion")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🚀 Quick Test: Intelligent Reason Detection")
    print("=" * 50)
    
    success = await test_intelligent_reason()
    
    if success:
        print("\n✅ INTELLIGENT REASON DETECTION WORKS!")
        print("Sofia should not ask twice about appointment reasons.")
    else:
        print("\n❌ PROBLEM: Intelligent reason detection not working")
        print("Sofia is still asking about reasons when she shouldn't.")
    
    return success

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
