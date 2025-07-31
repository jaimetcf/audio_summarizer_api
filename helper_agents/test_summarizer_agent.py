#!/usr/bin/env python3
"""
Standalone test file for SummarizerAgent
This file can be run directly without pytest: python test_summarizer_agent_standalone.py
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
from docx import Document

from summarizer_agent import summarizer_agent, SummarizerOutput, generate_summary
from settings import settings

# Test Configuration - Set to True/False to enable/disable specific tests
TEST_CONFIG = {
    "test_agent_execution": True,
    "test_pydantic_model": True,
}

# Real Firebase Storage path for testing
TEMPLATE_STORAGE_PATH = "gs://audio-summarizer-21302.firebasestorage.app/report_templates/user123/test_report_template.docx"

test_transcript = """
Recurrent neural networks, long short-term memory [13] and gated recurrent [7] neural networks
in particular, have been firmly established as state of the art approaches in sequence modeling and
transduction problems such as language modeling and machine translation [35, 2, 5]. Numerous
efforts have since continued to push the boundaries of recurrent language models and encoder-decoder
architectures [38, 24, 15].
Recurrent models typically factor computation along the symbol positions of the input and output
sequences. Aligning the positions to steps in computation time, they generate a sequence of hidden
states ht, as a function of the previous hidden state ht−1 and the input for position t. This inherently
sequential nature precludes parallelization within training examples, which becomes critical at longer
sequence lengths, as memory constraints limit batching across examples. Recent work has achieved
significant improvements in computational efficiency through factorization tricks [21] and conditional
computation [32], while also improving model performance in case of the latter. The fundamental
constraint of sequential computation, however, remains.
Attention mechanisms have become an integral part of compelling sequence modeling and transduction models in various tasks, allowing modeling of dependencies without regard to their distance in
the input or output sequences [2, 19]. In all but a few cases [27], however, such attention mechanisms
are used in conjunction with a recurrent network.
In this work we propose the Transformer, a model architecture eschewing recurrence and instead
relying entirely on an attention mechanism to draw global dependencies between input and output.
The Transformer allows for significantly more parallelization and can reach a new state of the art in
translation quality after being trained for as little as twelve hours on eight P100 GPUs.

The goal of reducing sequential computation also forms the foundation of the Extended Neural GPU
[16], ByteNet [18] and ConvS2S [9], all of which use convolutional neural networks as basic building
block, computing hidden representations in parallel for all input and output positions. In these models,
the number of operations required to relate signals from two arbitrary input or output positions grows
in the distance between positions, linearly for ConvS2S and logarithmically for ByteNet. This makes
it more difficult to learn dependencies between distant positions [12]. In the Transformer this is
reduced to a constant number of operations, albeit at the cost of reduced effective resolution due
to averaging attention-weighted positions, an effect we counteract with Multi-Head Attention as
described in section 3.2.
Self-attention, sometimes called intra-attention is an attention mechanism relating different positions
of a single sequence in order to compute a representation of the sequence. Self-attention has been
used successfully in a variety of tasks including reading comprehension, abstractive summarization,
textual entailment and learning task-independent sentence representations [4, 27, 28, 22].
End-to-end memory networks are based on a recurrent attention mechanism instead of sequencealigned recurrence and have been shown to perform well on simple-language question answering and
language modeling tasks [34].
To the best of our knowledge, however, the Transformer is the first transduction model relying
entirely on self-attention to compute representations of its input and output without using sequencealigned RNNs or convolution. In the following sections, we will describe the Transformer, motivate
self-attention and discuss its advantages over models such as [17, 18] and [9].
"""

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

def download_template_from_storage():
    """Download the real template file from Firebase Storage for testing"""
    try:
        bucket = storage.bucket()
        blob = bucket.blob(TEMPLATE_STORAGE_PATH.replace(f"gs://{bucket.name}/", ""))
        
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as temp_file:
            blob.download_to_filename(temp_file.name)
            return temp_file.name
    except Exception as e:
        print(f"⚠️  Warning: Could not download template file: {str(e)}")
        return None

def extract_template_content(template_path: str) -> str:
    """Extract content from template Word document"""
    try:
        doc = Document(template_path)
        content = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                content.append(paragraph.text)
        return "\n".join(content)
    except Exception as e:
        raise Exception(f"Failed to extract template content: {str(e)}")

async def test_agent_execution():
    """Test the summarizer agent execution with Runner using real template file"""
    print("\n=== Testing SummarizerAgent Execution ===")
    
    template_file_path = download_template_from_storage()
    if (not template_file_path) or (not os.path.exists(template_file_path)):
        print("⚠️  Warning: Could not download template file")
        return False

    template_content = extract_template_content(template_file_path)
    if (not template_content) or (not os.path.exists(template_file_path)):
        print("⚠️  Warning: Could not extract template file content")
        return False
        
    try:
        print(f"  Testing agent execution with template file: {template_file_path}")
        print(f"  Template content: {template_content}")
                        
        # Test agent execution with real template file
        result = await Runner.run(
            summarizer_agent,
            f"Generate a summary from transcript: {test_transcript}\nTemplate content: {template_content}"
        )
            
        # Verify the result
        assert hasattr(result, 'final_output'), "Result should have final_output attribute"
            
        if isinstance(result.final_output, SummarizerOutput):
            assert len(result.final_output.summary) > 0, "Summary should not be empty"
            print(f"✓ Successfully generated summary via agent: {len(result.final_output.summary)} characters")
            print(f"  Sample summary: {result.final_output.summary[:100]}...")
        else:
            # Fallback for string output
            assert len(str(result.final_output)) > 0, "Summary should not be empty"
            print(f"✓ Successfully generated summary via agent: {len(str(result.final_output))} characters")
            print(f"  Sample summary: {str(result.final_output)[:100]}...")
            
        return True
            
    except Exception as e:
        print(f"✗ SummarizerAgent execution test failed: {e}")
        return False
    
    finally:
        # Clean up the downloaded file
        try:
            os.unlink(template_file_path)
            print(f"  Cleaned up temporary file: {template_file_path}")
        except Exception as e:
            print(f"  Warning: Could not clean up file {template_file_path}: {e}")


async def test_pydantic_model():
    """Test the SummarizerOutput Pydantic model"""
    print("\n=== Testing SummarizerOutput Pydantic Model ===")
    
    try:
        # Test model creation
        print("  Testing model creation...")
        output = SummarizerOutput(summary="Test summary")
        assert output.summary == "Test summary", "Model should store summary correctly"
        
        # Test model serialization
        print("  Testing model serialization...")
        model_dict = output.model_dump()
        assert model_dict["summary"] == "Test summary", "Serialized model should contain summary"
        
        # Test model validation
        print("  Testing model validation...")
        try:
            SummarizerOutput()  # Missing required field
            print("✗ Expected ValueError for missing required field")
            return False
        except ValueError as e:
            print(f"  ✓ Correctly raised ValueError for missing field: {e}")
        
        print("✓ SummarizerOutput Pydantic model test passed")
        return True
        
    except Exception as e:
        print(f"✗ SummarizerOutput Pydantic model test failed: {e}")
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
    print("Running SummarizerAgent tests with real Firebase Storage...")
    
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