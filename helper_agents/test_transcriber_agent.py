#!/usr/bin/env python3
"""
Standalone test file for TranscriberAgent
This file can be run directly without pytest: python test_transcriber_agent_standalone.py
"""

import sys
import os

# Add parent directory to Python path BEFORE any other imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import tempfile
import firebase_admin
from firebase_admin import credentials, storage
from agents import Runner

from transcriber_agent import transcriber_agent, TranscriberOutput, transcribe_audio
from settings import settings

# Test Configuration - Set to True/False to enable/disable specific tests
TEST_CONFIG = {
    "test_agent_execution": True,
    "test_pydantic_model": True,
}

# Real Firebase Storage path for testing
AUDIO_STORAGE_PATH = "gs://audio-summarizer-21302.firebasestorage.app/audio/user123/audio-test1.mp3"

def initialize_firebase():
    """Initialize Firebase Admin SDK for testing"""
    try:
        cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred, {
            'storageBucket': settings.FIREBASE_STORAGE_BUCKET
        })
        print("✓ Firebase Admin SDK initialized successfully")
        return True
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize Firebase Admin SDK: {str(e)}")
        print("   Tests requiring Firebase Storage may fail")
        return False

def download_audio_from_storage():
    """Download the real audio file from Firebase Storage for testing"""
    try:
        bucket = storage.bucket()
        blob = bucket.blob(AUDIO_STORAGE_PATH.replace(f"gs://{bucket.name}/", ""))
        
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            blob.download_to_filename(temp_file.name)
            return temp_file.name
    except Exception as e:
        print(f"⚠️  Warning: Could not download audio file: {str(e)}")
        return None



async def test_agent_execution():
    """Test the transcriber agent execution with Runner using real audio file"""
    print("\n=== Testing TranscriberAgent Execution ===")
    
    # Download the real audio file from Firebase Storage
    audio_file_path = download_audio_from_storage()
    
    if audio_file_path and os.path.exists(audio_file_path):
        try:
            print(f"  Testing agent execution with audio file: {audio_file_path}")
            
            # Test agent execution with real audio file
            result = await Runner.run(
                transcriber_agent,
                f"Transcribe the audio file at {audio_file_path}"
            )
            
            # Verify the result
            assert hasattr(result, 'final_output'), "Result should have final_output attribute"
            
            if isinstance(result.final_output, TranscriberOutput):
                assert len(result.final_output.transcript) > 0, "Transcript should not be empty"
                print(f"✓ Successfully transcribed via agent: {len(result.final_output.transcript)} characters")
                print(f"  Sample transcript: {result.final_output.transcript[:100]}...")
            else:
                # Fallback for string output
                assert len(str(result.final_output)) > 0, "Transcript should not be empty"
                print(f"✓ Successfully transcribed via agent: {len(str(result.final_output))} characters")
                print(f"  Sample transcript: {str(result.final_output)[:100]}...")
            
            return True
            
        except Exception as e:
            print(f"✗ TranscriberAgent execution test failed: {e}")
            return False
        finally:
            # Clean up the downloaded file
            try:
                os.unlink(audio_file_path)
                print(f"  Cleaned up temporary file: {audio_file_path}")
            except Exception as e:
                print(f"  Warning: Could not clean up file {audio_file_path}: {e}")
    else:
        print("⚠️  Warning: Could not download audio file for agent execution test")
        return False



async def test_pydantic_model():
    """Test the TranscriberOutput Pydantic model"""
    print("\n=== Testing TranscriberOutput Pydantic Model ===")
    
    try:
        # Test model creation
        print("  Testing model creation...")
        output = TranscriberOutput(transcript="Test transcript")
        assert output.transcript == "Test transcript", "Model should store transcript correctly"
        
        # Test model serialization
        print("  Testing model serialization...")
        model_dict = output.model_dump()
        assert model_dict["transcript"] == "Test transcript", "Serialized model should contain transcript"
        
        # Test model validation
        print("  Testing model validation...")
        try:
            TranscriberOutput()  # Missing required field
            print("✗ Expected ValueError for missing required field")
            return False
        except ValueError as e:
            print(f"  ✓ Correctly raised ValueError for missing field: {e}")
        
        print("✓ TranscriberOutput Pydantic model test passed")
        return True
        
    except Exception as e:
        print(f"✗ TranscriberOutput Pydantic model test failed: {e}")
        return False

def show_configuration():
    """Show which tests are enabled/disabled"""
    print("\n=== Test Configuration ===")
    for test_name, enabled in TEST_CONFIG.items():
        status = "✓ ENABLED" if enabled else "✗ DISABLED"
        print(f"{test_name}: {status}")
    print("========================\n")

async def run_all_tests():
    """Run all enabled tests"""
    print("Running TranscriberAgent tests with real Firebase Storage...")
    
    # Initialize Firebase
    firebase_initialized = initialize_firebase()
    
    # Show configuration
    show_configuration()
    
    # Track test results
    test_results = {}
    
    # Run enabled tests
    if TEST_CONFIG["test_agent_execution"]:
        test_results["agent_execution"] = await test_agent_execution()
    
    if TEST_CONFIG["test_pydantic_model"]:
        test_results["pydantic_model"] = await test_pydantic_model()
    
    # Print summary
    print("\n=== Test Summary ===")
    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests completed successfully!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    # Run all tests
    success = asyncio.run(run_all_tests())
    
    # Exit with appropriate code
    exit(0 if success else 1) 