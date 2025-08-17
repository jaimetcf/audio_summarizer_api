"""
Audio File Chunker Tool

This script provides a command-line interface for breaking down large audio files into smaller,
more manageable chunks. It's useful for processing audio files that exceed size limits for
various APIs or applications, or for creating smaller segments for easier handling.

Features:
- Breaks down MP3 audio files into smaller chunks of specified size
- Maintains audio quality during the chunking process
- Automatically calculates optimal chunk duration based on file size
- Uses consistent naming convention for chunk files
- Provides detailed progress and size information

Usage:
    python break.py <audio_file_name> <chunk_size_mb>

Examples:
    python break.py large_podcast.mp3 10
    python break.py interview.mp3 5
    python break.py lecture.mp3 25

Parameters:
    audio_file_name: Name of the MP3 file to break down (must be in ./data/audio_files/)
    chunk_size_mb: Size of each chunk in megabytes (can be decimal, e.g., 10.5)

Input:
    - Audio file must be in MP3 format
    - File must be located in ./data/audio_files/ directory
    - Chunk size specified in megabytes

Output:
    - Chunk files saved in ./data/audio_files/ directory
    - Naming convention: <original_name>_part01.mp3, _part02.mp3, etc.
    - Example: large_podcast_part01.mp3, large_podcast_part02.mp3

Behavior:
    - If file is already smaller than specified chunk size, returns original file
    - Calculates optimal number of chunks based on target size
    - Splits audio evenly across chunks while maintaining quality
    - Shows progress and actual chunk sizes after creation

Dependencies:
    - pydub library for audio processing
    - Audio file must exist in the specified directory
    - Sufficient disk space for chunk files

Author: Audio Summarizer API
"""

import os
import argparse
from pydub import AudioSegment
import math
from typing import List

audio_files_folder = './data/audio_files/'


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Audio File Chunker - Break down audio files into smaller chunks')
    parser.add_argument(
        'audio_file',
        type=str,
        help='Audio file name to break down'
    )
    parser.add_argument(
        'chunk_size_mb',
        type=float,
        help='Size of each chunk in megabytes'
    )
    return parser.parse_args()


def break_down_audio_file(audio_file_path: str, chunk_size_mb: float) -> List[str]:
    """
    Break down audio file into smaller chunks of specified size
    
    Args:
        audio_file_path: Path to the original audio file
        chunk_size_mb: Size of each chunk in megabytes
        
    Returns:
        List of paths to the smaller audio files
    """
    try:
        # Load the audio file
        audio = AudioSegment.from_mp3(audio_file_path)
        
        # Get file size in bytes
        file_size = os.path.getsize(audio_file_path)
        file_size_mb = file_size / (1024 * 1024)  # Convert to MB
        
        print(f"Original file size: {file_size_mb:.2f} MB")
        print(f"Target chunk size: {chunk_size_mb:.2f} MB")
        
        # If file is already smaller than or equal to chunk size, return the original file path
        if file_size_mb <= chunk_size_mb:
            print(f"✓ File is already within size limit ({chunk_size_mb:.2f} MB or less)")
            return [audio_file_path]
        
        # Calculate number of chunks needed
        # n = file_size_mb / chunk_size_mb + 1 (if there's a remainder)
        n_chunks = math.ceil(file_size_mb / chunk_size_mb)
        print(f"Breaking down into {n_chunks} chunks")
        
        # Calculate duration per chunk
        total_duration_ms = len(audio)
        chunk_duration_ms = total_duration_ms // n_chunks
        
        # Get base filename without extension
        base_name = os.path.splitext(os.path.basename(audio_file_path))[0]
        base_path = os.path.dirname(audio_file_path)
        
        chunk_files = []
        
        for i in range(n_chunks):
            # Calculate start and end times for this chunk
            start_time = i * chunk_duration_ms
            end_time = start_time + chunk_duration_ms if i < n_chunks - 1 else total_duration_ms
            
            # Extract the chunk
            chunk = audio[start_time:end_time]
            
            # Create chunk filename
            chunk_filename = f"{base_name}_part{i+1:02d}.mp3"
            chunk_path = base_path + '/' + chunk_filename
            
            # Export the chunk
            chunk.export(chunk_path, format="mp3")
            
            # Verify the chunk size
            chunk_size_mb_actual = os.path.getsize(chunk_path) / (1024 * 1024)
            print(f"✓ Created chunk {i+1}/{n_chunks}: {chunk_filename} ({chunk_size_mb_actual:.2f} MB)")
            
            chunk_files.append(chunk_path)
        
        return chunk_files
        
    except Exception as e:
        raise Exception(f"Failed to break down audio file: {str(e)}")


def main():
    """Main function to break down audio file"""
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Set file path based on CLI arguments
        audio_file_name = args.audio_file
        chunk_size_mb = args.chunk_size_mb
        audio_file_path = audio_files_folder + audio_file_name

        print('\nAudio file that will be processed:')
        print(audio_file_path)
        print(f'\nChunk size: {chunk_size_mb:.2f} MB')

        print('\n--------------------------------------------------------------------\n')
        
        # Check if file exists
        if not os.path.exists(audio_file_path):
            print(f"❌ Error: Audio file '{audio_file_path}' not found!")
            print(f"Please make sure the file exists in the '{audio_files_folder}' directory.")
            exit(1)
        
        # Break down the audio file
        chunk_files = break_down_audio_file(audio_file_path, chunk_size_mb)
        
        print(f"\n✓ Successfully created {len(chunk_files)} chunk file(s):")
        for chunk_file in chunk_files:
            print(f"  - {os.path.basename(chunk_file)}")
        
        print(f"\nAll chunk files saved in: {audio_files_folder}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()
