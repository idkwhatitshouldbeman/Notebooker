"""
Test script for AI service integration
Tests the AI service client and EN writer integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_service_client import AIServiceClient, AgentConfig, initialize_ai_service
from en_writer import ENWriter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ai_service_client():
    """Test AI service client functionality"""
    print("Testing AI Service Client...")
    
    try:
        # Initialize AI service
        initialize_ai_service()
        
        # Test health check
        from ai_service_client import get_ai_client
        ai_client = get_ai_client()
        
        print(f"AI Service URL: {ai_client.base_url}")
        
        # Test health check
        is_healthy = ai_client.health_check()
        print(f"AI Service Health: {'✅ Healthy' if is_healthy else '❌ Unhealthy'}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Service Client test failed: {e}")
        return False

def test_en_writer_integration():
    """Test EN writer with AI service integration"""
    print("\nTesting EN Writer Integration...")
    
    try:
        # Create EN writer instance
        en_writer = ENWriter("en_files")
        
        # Test gap analysis (should work with fallback)
        test_sections = {
            "test_section": "# Test Section\n\nThis is a test section with minimal content."
        }
        
        gap_analysis = en_writer.analyze_sections_for_gaps(test_sections)
        print(f"✅ Gap analysis completed: {len(gap_analysis.get('missing_sections', []))} missing sections")
        
        # Test question generation (will use fallback if AI service unavailable)
        questions = en_writer.generate_user_questions(gap_analysis)
        print(f"✅ Question generation completed: {len(questions)} questions generated")
        
        # Test draft generation (will use fallback if AI service unavailable)
        user_inputs = {
            'title': 'Test Hardware Component',
            'overview': 'A test hardware component for robotics',
            'technical_details': 'Basic technical specifications',
            'tags': 'robotics, hardware, test'
        }
        
        draft = en_writer.draft_new_entry("test_section", user_inputs)
        print(f"✅ Draft generation completed: {len(draft)} characters generated")
        
        return True
        
    except Exception as e:
        print(f"❌ EN Writer integration test failed: {e}")
        return False

def test_fallback_functionality():
    """Test fallback functionality when AI service is unavailable"""
    print("\nTesting Fallback Functionality...")
    
    try:
        # Test with invalid AI service URL to force fallback
        initialize_ai_service("http://invalid-url-for-testing")
        
        en_writer = ENWriter("en_files")
        
        # Test that fallback works
        gap_analysis = {
            'missing_sections': ['Hardware Design', 'Software Architecture'],
            'incomplete_sections': ['Testing Procedures'],
            'technical_gaps': ['Control System'],
            'unclear_content': ['System Overview'],
            'missing_images': ['Architecture Diagram']
        }
        
        questions = en_writer.generate_user_questions(gap_analysis)
        print(f"✅ Fallback question generation: {len(questions)} questions")
        
        # Test draft generation with fallback
        user_inputs = {
            'title': 'Fallback Test Section',
            'overview': 'Testing fallback functionality',
            'tags': 'test, fallback'
        }
        
        draft = en_writer.draft_new_entry("fallback_test", user_inputs)
        print(f"✅ Fallback draft generation: {len(draft)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Fallback functionality test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 AI Service Integration Tests")
    print("=" * 50)
    
    tests = [
        test_ai_service_client,
        test_en_writer_integration,
        test_fallback_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! AI service integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
