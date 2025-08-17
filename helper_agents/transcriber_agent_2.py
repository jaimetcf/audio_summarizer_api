from agents import Agent, function_tool
from pydantic import BaseModel
from openai import OpenAI
from settings import settings
from typing import List


# Pydantic models for Transcriber2 output
class TranscriberParagraph(BaseModel):
    speaker: str        # name of the speaker
    paragraph: str      # what was said by the speaker in this paragraph

class Transcriber2Output(BaseModel):
    transcript: List[TranscriberParagraph]

# Tool function for transcription with speaker identification
@function_tool
def transcribe_audio_with_speakers(audio_file_path: str) -> str:
    """Transcribe audio file using OpenAI Whisper API with speaker identification"""
    try:
        openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        with open(audio_file_path, "rb") as audio_file:
            transcript = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="json",
            )
        return transcript
    except Exception as e:
        raise Exception(f"Transcription failed: {str(e)}")

# Tool function for speaker identification and paragraph segmentation
@function_tool
def identify_speakers_and_segments(transcript_json: str) -> str:
    """Analyze transcript to identify speakers and segment into paragraphs"""
    try:
        openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Create a prompt for speaker identification
        prompt = f"""
        Analyze the following transcript and identify different speakers. 
        Segment the content into paragraphs where each paragraph represents a continuous speech from one speaker.
        
        Transcript data: {transcript_json}
        
        Please return a JSON array where each object has:
        - "speaker": The identified speaker name (e.g., "Speaker 1", "Speaker 2", "Interviewer", "Interviewee", etc.)
        - "paragraph": The complete text spoken by that speaker in this segment
        
        Rules for speaker identification:
        1. Look for natural breaks in conversation
        2. Identify when different people are speaking. To do that, break from one speaker to the other when you find a question mark, '?'. 
        Usually the sentence before a question mark was spelled by one speaker, and the sentence after a question mark was spelled by another speaker. Consider the question mark itself as a break.
        3. Use descriptive speaker names when possible (e.g., "Interviewer", "Expert", "Host", "Guest")
        4. If you can't determine specific names, use "Speaker 1", "Speaker 2", etc.
        5. Combine consecutive segments from the same speaker into single paragraphs
        6. Ensure each paragraph contains complete thoughts or responses
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are an expert at analyzing transcripts and identifying different speakers in conversations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Speaker identification failed: {str(e)}")

# Define the Transcriber2 agent
transcriber_agent_2 = Agent(
    name="Transcriber2",
    instructions="""You are an advanced transcription specialist with speaker identification capabilities. 
    Your job is to transcribe audio files and identify different speakers in the conversation.
    
    INPUT: You will receive an audio file path as a string.
    OUTPUT: You must return a Transcriber2Output object with a list of TranscriberParagraph objects.
    
    Process:
    1. Use the transcribe_audio_with_speakers tool to get a detailed transcript
    2. Use the identify_speakers_and_segments tool to analyze the transcript and identify speakers
    3. Parse the speaker identification results into TranscriberParagraph objects
    4. Return a Transcriber2Output object with the list of paragraphs
    
    Each TranscriberParagraph should contain:
    - speaker: The name of the speaker (e.g., "Speaker 1", "Interviewer", "Expert")
    - paragraph: The complete text spoken by that speaker in that segment
    
    Ensure the output is well-structured and accurately represents the conversation flow.""",
    tools=[transcribe_audio_with_speakers, identify_speakers_and_segments],
    output_type=Transcriber2Output
)
