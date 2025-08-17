"""
Audio Transcription Tool with Speaker Identification

This script provides a command-line interface for transcribing audio files with advanced
speaker identification capabilities. It uses OpenAI's Whisper API for transcription and
GPT-4 for speaker identification and segmentation.

Features:
- Transcribes audio files from MP3 format to text
- Identifies different speakers in conversations
- Segments content into logical paragraphs by speaker
- Saves transcripts in a readable format with speaker labels

Usage:
    python transcribe.py <audio_file_name>

Example:
    python transcribe.py interview.mp3

Input:
    - Audio file must be in MP3 format
    - File must be located in ./data/audio_files/ directory

Output:
    - Transcript saved as <audio_file_name>.txt in ./data/transcripts/ directory
    - Format: [Speaker Name] followed by their spoken content
    - Example:
        [Interviewer]
        Hello, welcome to our show today.

        [Expert]
        Thank you for having me. I'm excited to discuss this topic.

Dependencies:
    - OpenAI API key configured in settings.py
    - Required packages: openai, pydub, agents, pydantic
    - Audio file must exist in the specified directory

Author: Audio Summarizer API
"""

import os
import asyncio
import argparse
from agents import Runner

from settings import settings
from helper_agents.transcriber_agent_2 import transcriber_agent_2, Transcriber2Output

audio_files_folder = './data/audio_files/'
transcript_files_folder = './data/transcripts/'


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Audio Transcriber - Transcribe audio files with speaker identification')
    parser.add_argument(
        'audio_file',
        type=str,
        help='Audio file name to transcribe'
    )
    return parser.parse_args()


async def run_pipeline(audio_file_path: str):
    """
    Transcribe audio file and save transcript with speaker identification
    """
    try:
        print(f"\nTranscribing audio with speaker identification => ... ")
        transcript_result = await transcribe_audio(audio_file_path)
        
        print(f"\nSaving transcript => ... ")
        audio_file_name = os.path.basename(audio_file_path)
        transcript_file_name = audio_file_name.replace('.mp3', '.txt')
        transcript_file_path = os.path.join(transcript_files_folder, transcript_file_name)        
        os.makedirs(transcript_files_folder, exist_ok=True)        
        
        # Format transcript with speaker information
        formatted_transcript = format_transcript_with_speakers(transcript_result)
        
        with open(transcript_file_path, 'w', encoding='utf-8') as f:
            f.write(formatted_transcript)
        print(f"✓ Successfully saved transcript: {transcript_file_path}")
        
    except Exception as e:
        raise Exception(f"Failed to transcribe audio file: {str(e)}")

async def transcribe_audio(audio_file_path: str) -> Transcriber2Output:
    """
    Transcribe audio file using OpenAI Agents SDK with speaker identification
    """
    try:
        # Call the transcriber agent 2
        result = await Runner.run( 
            transcriber_agent_2, 
            f"Transcribe the audio file at {audio_file_path}"
        )
        
        if isinstance(result.final_output, Transcriber2Output):
            total_paragraphs = len(result.final_output.transcript)
            total_characters = sum(len(para.paragraph) for para in result.final_output.transcript)
            print(f"✓ Successfully transcribed via AI agent: {total_paragraphs} paragraphs, {total_characters} characters")
        else:
            # Fallback for string output
            assert len(str(result.final_output)) > 0, "Transcript should not be empty"
            print(f"✓ Successfully transcribed via AI agent: {len(str(result.final_output))} characters")

        return result.final_output
        
    except Exception as e:
        raise Exception(f"Failed to transcribe audio: {str(e)}")

def format_transcript_with_speakers(transcript_result: Transcriber2Output) -> str:
    """
    Format the transcript result into a readable text format with speaker information
    """
    formatted_lines = []
    
    for i, paragraph in enumerate(transcript_result.transcript, 1):
        formatted_lines.append(f"[{paragraph.speaker}]")
        formatted_lines.append(paragraph.paragraph)
        formatted_lines.append("")  # Empty line for separation
    
    return "\n".join(formatted_lines)


if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    
    # Set file path based on CLI argument
    audio_file_name = args.audio_file
    audio_file_path = audio_files_folder + audio_file_name

    print('\nAudio file that will be processed:')
    print(audio_file_path)

    print('\nTranscript file that will be saved:')
    transcript_file_name = audio_file_name.replace('.mp3', '.txt')
    transcript_file_path = os.path.join(transcript_files_folder, transcript_file_name)
    print(transcript_file_path)

    print('\n--------------------------------------------------------------------\n')
    
    # Run transcription
    success = asyncio.run(run_pipeline(audio_file_path))    
    # Exit with appropriate code
    exit(0 if success else 1)
