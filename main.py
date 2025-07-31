from typing import Optional
import asyncio
import argparse
from agents import Runner
from docx import Document
import tempfile
import shutil

from settings import settings
from helper_agents.transcriber_agent import transcriber_agent, TranscriberOutput
from helper_agents.summarizer_agent import summarizer_agent, SummarizerOutput


# Default values
default_audio_file_name = 'transformer-paper-introduction.mp3'
default_template_file_name = 'default_report_template.docx'

audio_files_folder = './data/audio_files/'
template_files_folder = './data/report_templates/'
reports_folder = './data/reports/'


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Audio Summarizer - Transcribe and summarize audio files')
    parser.add_argument(
        '--audio-file', 
        '-a',
        type=str, 
        default=default_audio_file_name,
        help=f'Audio file name (default: {default_audio_file_name})'
    )
    parser.add_argument(
        '--template-file', 
        '-t',
        type=str, 
        default=default_template_file_name,
        help=f'Template file name (default: {default_template_file_name})'
    )
    return parser.parse_args()


async def summarize_audio(
    file_locator: str,
    template_locator: str,
):
    """
    Transcribe audio file and generate report using OpenAI Agents SDK
    """
    try:
        print(f"\nTranscribing audio => ... ")
        transcript = await transcribe_audio(audio_file_path)
        print(f"\nExtracting template content => ... ")
        template_content = extract_template_content(template_file_path)
        print(f"\nSummarizing transcript => ... ")
        summary = await summarize_transcript(transcript, template_content)
        print(f"\nSaving report => ... ")
        save_report(summary, report_file_path)
        print('\n\n')
        
    except Exception as e:
        raise Exception(f"Failed to summarize audio: {str(e)}")


async def transcribe_audio(audio_file_path: str) -> str:
    """
    Transcribe audio file using OpenAI Agents SDK
    """
    try:
        # Call the transcriber agent
        result = await Runner.run( 
            transcriber_agent, 
            f"Transcribe the audio file at {audio_file_path}"
        )
        
        if isinstance(result.final_output, TranscriberOutput):
            assert len(result.final_output.transcript) > 0, "Transcript should not be empty"
            print(f"✓ Successfully transcribed via AI agent: {len(result.final_output.transcript)} characters")
            #print(f"  Sample transcript: {result.final_output.transcript[:100]}...")
        else:
            # Fallback for string output
            assert len(str(result.final_output)) > 0, "Transcript should not be empty"
            print(f"✓ Successfully transcribed via AI agent: {len(str(result.final_output))} characters")
            #print(f"  Sample transcript: {str(result.final_output)[:100]}...")

        return result.final_output.transcript
        
    except Exception as e:
        raise Exception(f"Failed to transcribe audio: {str(e)}")


def extract_template_content(template_path: str) -> str:
    """Extract content from template Word document"""
    try:
        doc = Document(template_path)
        content = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                content.append(paragraph.text)
        print(f"✓ Successfully extracted template content: {len(content)} paragraphs")
        #print(f"  Sample template content: {content[:100]}...")
        return "\n".join(content)

    except Exception as e:
        raise Exception(f"Failed to extract template content: {str(e)}")


async def summarize_transcript(transcript: str, template_content: str) -> str:
    """
    Generate report using OpenAI Agents SDK
    """
    try:
        result = await Runner.run(
            summarizer_agent,
            f"Generate a report based on the following transcript and template: {transcript}\n\nTemplate: {template_content}"
        )
        
        if isinstance(result.final_output, SummarizerOutput):
            assert len(result.final_output.summary) > 0, "Summary should not be empty"
            print(f"✓ Successfully generated summary via AI agent: {len(result.final_output.summary)} characters")
            #print(f"  Sample summary: {result.final_output.summary[:100]}...")
            return result.final_output.summary
        else:
            # Fallback for string output
            assert len(str(result.final_output)) > 0, "Summary should not be empty"
            print(f"✓ Successfully generated summary via AI agent: {len(str(result.final_output))} characters")
            #print(f"  Sample summary: {str(result.final_output)[:100]}...")
            return str(result.final_output)

    except Exception as e:
        raise Exception(f"Failed to summarize transcript: {str(e)}")


def save_report(summary: str, report_file_path: str) -> str:
    """Create Word document with summary"""
    try:
        doc = Document()
        doc.add_heading('Audio Transcription Report', 0)
                        
        # Add generated report
        doc.add_heading('Analysis Report', level=1)
        doc.add_paragraph(summary)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as temp_doc:
            doc.save(temp_doc.name)
            temp_file_path = temp_doc.name
        
        # Close the document to release the file handle
        del doc
        
        # Now move the file after the document is closed
        shutil.move(temp_file_path, report_file_path)
        print(f"✓ Successfully saved report: {report_file_path}")
        return report_file_path

    except Exception as e:
        raise Exception(f"Failed to save report: {str(e)}")


if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    
    # Set file paths based on CLI arguments
    audio_file_name = args.audio_file
    template_file_name = args.template_file
    
    audio_file_path = audio_files_folder + audio_file_name
    template_file_path = template_files_folder + template_file_name
    report_file_path = reports_folder + audio_file_name.replace('.mp3', '.docx')

    print('\nFiles that will be processed:    ')
    print(audio_file_path)
    print(template_file_path)

    print('\nReport file that will be saved:')
    print(report_file_path)

    print('\n--------------------------------------------------------------------\n')
    
    # Run all tests
    success = asyncio.run(summarize_audio(audio_file_path, template_file_path))    
    # Exit with appropriate code
    exit(0 if success else 1) 
