#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test for neutral phone number asking (fixed)
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_neutral_phone_asking():
    """Test that phone number asking is completely neutral"""
    try:
        from dental_tools import telefonnummer_erfragen
        
        print("🧪 Testing: Neutral Phone Number Asking (Fixed)...")
        
        result = await telefonnummer_erfragen(context=None)
        
        print(f"Result: '{result}'")
        
        # Check what it contains
        has_neutral_question = "wie ist ihre telefonnummer" in result.lower()
        mentions_format = "format" in result.lower()
        mentions_german = "deutsch" in result.lower() or "+49" in result or "0xxx" in result
        mentions_country = any(word in result.lower() for word in ["deutsch", "german", "germany", "+49"])
        
        print(f"✓ Has neutral question: {has_neutral_question}")
        print(f"✓ Mentions format: {mentions_format}")
        print(f"✓ Mentions German/country: {mentions_country}")
        
        if has_neutral_question and not mentions_format and not mentions_country:
            print("✅ PERFECT: Completely neutral phone number request")
            return True
        else:
            print("❌ PROBLEM: Still not completely neutral")
            if not has_neutral_question:
                print("   - Missing neutral question")
            if mentions_format:
                print("   - Still mentions format")
            if mentions_country:
                print("   - Still mentions German/country specific")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🚀 Test: Neutral Phone Number Fix")
    print("=" * 50)
    
    success = await test_neutral_phone_asking()
    
    if success:
        print("\n✅ PHONE NUMBER ASKING IS NOW COMPLETELY NEUTRAL!")
        print("Sofia will only ask: 'Wie ist Ihre Telefonnummer?'")
        print("No format, no German-specific mentions!")
    else:
        print("\n❌ Phone number asking still needs fixing")
    
    return success

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
