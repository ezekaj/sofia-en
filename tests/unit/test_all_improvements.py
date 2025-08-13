#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Comprehensive test for ALL Sofia improvements
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_no_double_asking():
    """Test intelligent reason detection"""
    try:
        from dental_tools import intelligente_terminanfrage
        
        print("🧪 Testing: No Double Asking...")
        
        result = await intelligente_terminanfrage(
            context=None,
            patient_anfrage="Ich habe starke Schmerzen"
        )
        
        asks_for_reason = "worum geht es denn" in result.lower()
        has_appointment = "soll ich" in result.lower() and "buchen" in result.lower()
        
        if not asks_for_reason and has_appointment:
            print("   ✅ No double asking - Direct appointment suggestion")
            return True
        else:
            print("   ❌ Still asking for reason when it's already clear")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

async def test_phone_number_neutral():
    """Test neutral phone number asking"""
    try:
        from dental_tools import telefonnummer_erfragen
        
        print("🧪 Testing: Neutral Phone Number Asking...")
        
        result = await telefonnummer_erfragen(context=None)
        
        has_neutral_ask = "wie ist ihre telefonnummer" in result.lower()
        no_german_specific = "deutsche" not in result.lower()
        
        if has_neutral_ask and no_german_specific:
            print("   ✅ Neutral phone number request (no 'deutsche')")
            return True
        else:
            print("   ❌ Phone number request not neutral")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

def test_performance_optimization():
    """Test performance optimizations"""
    try:
        from appointment_manager import appointment_manager
        
        print("🧪 Testing: Performance Optimization...")
        
        # Test batch query function exists
        if hasattr(appointment_manager, 'get_belegte_termine_batch'):
            print("   ✅ Batch query function exists")
            
            # Test performance
            start_time = time.time()
            termin = appointment_manager.get_naechster_freier_termin()
            duration = time.time() - start_time
            
            if duration < 0.05:  # Under 50ms
                print(f"   ✅ Fast appointment search: {duration:.4f}s")
                return True
            else:
                print(f"   ⚠️ Slow appointment search: {duration:.4f}s")
                return False
        else:
            print("   ❌ Batch query function missing")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

async def test_conversation_ending():
    """Test complete conversation ending"""
    try:
        from dental_tools import gespraech_komplett_beenden
        
        print("🧪 Testing: Complete Conversation Ending...")
        
        result = await gespraech_komplett_beenden(
            context=None,
            grund="Terminbuchung abgeschlossen"
        )
        
        has_end_signal = "*[CALL_END_SIGNAL]*" in result
        has_goodbye = "auf wiederhören" in result.lower() or "auf wiedersehen" in result.lower()
        
        if has_end_signal and has_goodbye:
            print("   ✅ Complete conversation ending with auto hang-up")
            return True
        else:
            print("   ❌ Conversation ending incomplete")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

def test_callmanager_fix():
    """Test CallManager fix"""
    try:
        from dental_tools import call_manager
        
        print("🧪 Testing: CallManager Fix...")
        
        # Test correct method exists
        if hasattr(call_manager, 'initiate_call_end'):
            print("   ✅ initiate_call_end() method exists")
            
            # Test incorrect method doesn't exist
            if not hasattr(call_manager, 'end_conversation'):
                print("   ✅ end_conversation() method correctly removed")
                return True
            else:
                print("   ❌ end_conversation() method still exists")
                return False
        else:
            print("   ❌ initiate_call_end() method missing")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

async def test_agent_loading():
    """Test that agent loads successfully"""
    try:
        from agent import DentalReceptionist
        
        print("🧪 Testing: Agent Loading...")
        
        agent = DentalReceptionist()
        tool_count = len(agent.tools)
        
        if tool_count > 30:  # Should have many tools
            print(f"   ✅ Agent loads with {tool_count} tools")
            return True
        else:
            print(f"   ❌ Agent has too few tools: {tool_count}")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Sofia - Complete Improvements Test")
    print("=" * 60)
    print("Testing ALL improvements we implemented:")
    print()
    
    tests = [
        ("No Double Asking", test_no_double_asking()),
        ("Neutral Phone Number", test_phone_number_neutral()),
        ("Performance Optimization", test_performance_optimization()),
        ("Conversation Ending", test_conversation_ending()),
        ("CallManager Fix", test_callmanager_fix()),
        ("Agent Loading", test_agent_loading())
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if hasattr(test_func, '__await__'):  # Async function
                result = await test_func
            else:  # Sync function
                result = test_func
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
        print()
    
    # Summary
    print("=" * 60)
    print("📊 SUMMARY:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name}")
    
    print(f"\n🎯 OVERALL: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("\n🏆 EXCELLENT: All Sofia improvements are working!")
        print("✅ No double asking about appointment reasons")
        print("✅ Neutral phone number requests")
        print("✅ Lightning-fast appointment search")
        print("✅ Complete conversation ending")
        print("✅ CallManager errors fixed")
        print("✅ Agent loads successfully")
    elif passed >= total * 0.8:
        print("\n🥇 VERY GOOD: Most improvements working")
        print("💡 Minor issues to address")
    else:
        print("\n🥈 NEEDS WORK: Some improvements need fixing")
        print("⚠️ Check failed tests above")
    
    return passed == total

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
