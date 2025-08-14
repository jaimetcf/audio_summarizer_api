'''
The objective of the code in this file is to review and format a transcript file using OpenAI Agents SDK,
to make it more readable to a human.
'''

import asyncio
import argparse
import os
from agents import Runner
from helper_agents.transcript_reviewer_agent import transcript_reviewer_agent, TranscriptReviewerOutput

# Default values
default_transcript_file_name = 'transformer-paper-introduction.txt'

transcript_files_folder = './data/transcripts/'
reviewed_transcript_files_folder = './data/transcripts/'


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Transcript Reviewer - Review and format transcript files')
    parser.add_argument(
        '--transcript-file', 
        '-t',
        type=str, 
        default=default_transcript_file_name,
        help=f'Transcript file name (default: {default_transcript_file_name})'
    )
    return parser.parse_args()


async def review_transcript_file(transcript_file_path: str, reviewed_file_path: str):
    """
    Review and format transcript file using OpenAI Agents SDK
    """
    try:
        print(f"\nReading transcript file => ... ")
        
        # Read the transcript file
        with open(transcript_file_path, 'r', encoding='utf-8') as f:
            transcript_content = f.read()
        
        print(f"✓ Successfully read transcript file: {len(transcript_content)} characters")
        
        print(f"\nReviewing transcript => ... ")
        
        # Call the transcript reviewer agent
        result = await Runner.run(
            transcript_reviewer_agent,
            f"Review and format the following transcript text: {transcript_content}"
        )
        
        if isinstance(result.final_output, TranscriptReviewerOutput):
            reviewed_transcript = result.final_output.reviewed_transcript
            print(f"✓ Successfully reviewed transcript via AI agent: {len(reviewed_transcript)} characters")
        else:
            # Fallback for string output
            reviewed_transcript = str(result.final_output)
            print(f"✓ Successfully reviewed transcript via AI agent: {len(reviewed_transcript)} characters")
        
        print(f"\nSaving reviewed transcript => ... ")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(reviewed_file_path), exist_ok=True)
        
        # Save the reviewed transcript
        with open(reviewed_file_path, 'w', encoding='utf-8') as f:
            f.write(reviewed_transcript)
        
        print(f"✓ Successfully saved reviewed transcript: {reviewed_file_path}")
        print('\n\n')
        
    except Exception as e:
        raise Exception(f"Failed to review transcript: {str(e)}")


if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    
    # Set file paths based on CLI arguments
    transcript_file_name = args.transcript_file
    
    # Ensure the transcript file has .txt extension
    if not transcript_file_name.endswith('.txt'):
        transcript_file_name += '.txt'
    
    transcript_file_path = os.path.join(transcript_files_folder, transcript_file_name)
    
    # Create the reviewed file name
    base_name = os.path.splitext(transcript_file_name)[0]
    reviewed_file_name = f"{base_name}_reviewed.txt"
    reviewed_file_path = os.path.join(reviewed_transcript_files_folder, reviewed_file_name)

    print('\nFiles that will be processed:')
    print(f"Input transcript: {transcript_file_path}")
    print(f"Output reviewed transcript: {reviewed_file_path}")

    print('\n--------------------------------------------------------------------\n')
    
    # Run the transcript review
    success = asyncio.run(review_transcript_file(transcript_file_path, reviewed_file_path))    
    # Exit with appropriate code
    exit(0 if success else 1)
