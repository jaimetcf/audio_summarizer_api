from agents import Agent, function_tool
from pydantic import BaseModel
from openai import OpenAI
from settings import settings

# Pydantic model for TranscriptReviewer output
class TranscriptReviewerOutput(BaseModel):
    reviewed_transcript: str

# Tool function for transcript review
@function_tool
def review_transcript(plain_text: str) -> str:
    """Review and format transcript text to identify speakers and organize paragraphs"""
    try:
        openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Create a detailed prompt for the review task
        prompt = f"""Please review and format the following transcript text. Your task is to:

1. Identify different speakers in the conversation and label them as Speaker 1, Speaker 2, Speaker 3, etc.
2. Break the text into appropriate paragraphs based on topic changes and speaker transitions
3. Format the output with proper line breaks and speaker identification

For each paragraph, start with the speaker identification like: "Speaker X: <paragraph content>"

Here is the transcript to review:

{plain_text}

Please return the formatted transcript with proper speaker identification and paragraph breaks."""

        # Use OpenAI to process the transcript
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a transcript reviewer and formatter. Your job is to identify speakers in conversations and organize text into proper paragraphs with clear speaker identification."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=10000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        raise Exception(f"Transcript review failed: {str(e)}")

# Define the TranscriptReviewer agent
transcript_reviewer_agent = Agent(
    name="TranscriptReviewer",
    instructions="""You are a transcript review specialist. Your job is to analyze plain text transcripts and format them properly.
    
    INPUT: You will receive a plain text transcript as a string.
    OUTPUT: You must return a TranscriptReviewerOutput object with the reviewed and formatted transcript.
    
    Your tasks:
    1. Identify different speakers in the conversation and label them as Speaker 1, Speaker 2, Speaker 3, etc.
    2. Break the text into appropriate paragraphs based on topic changes and speaker transitions
    3. Format the output with proper line breaks and speaker identification
    
    For each paragraph, start with the speaker identification like: "Speaker X: <paragraph content>"
    
    When given a plain text transcript, use the review_transcript tool to process and format it.
    Return a TranscriptReviewerOutput object with the reviewed transcript text.""",
    tools=[review_transcript],
    output_type=TranscriptReviewerOutput
)
