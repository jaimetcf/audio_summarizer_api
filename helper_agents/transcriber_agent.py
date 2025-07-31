from agents import Agent, function_tool
from pydantic import BaseModel
from openai import OpenAI
from settings import settings

# Pydantic model for Transcriber output
class TranscriberOutput(BaseModel):
    transcript: str

# Tool function for transcription
@function_tool
def transcribe_audio(audio_file_path: str) -> str:
    """Transcribe audio file using OpenAI Whisper API"""
    try:
        openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        with open(audio_file_path, "rb") as audio_file:
            transcript = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        return transcript
    except Exception as e:
        raise Exception(f"Transcription failed: {str(e)}")

# Define the Transcriber agent
transcriber_agent = Agent(
    name="Transcriber",
    instructions="""You are a transcription specialist. Your job is to transcribe audio files accurately.
    
    INPUT: You will receive an audio file path as a string.
    OUTPUT: You must return a TranscriberOutput object with the transcript text.
    
    When given an audio file path, use the transcribe_audio tool to convert it to text.
    Return a TranscriberOutput object with the transcript text.""",
    tools=[transcribe_audio],
    output_type=TranscriberOutput
) 