from agents import Agent, function_tool
from pydantic import BaseModel
from openai import OpenAI
from settings import settings

# Pydantic model for Summarizer output
class SummarizerOutput(BaseModel):
    summary: str

# Tool function for summary generation
@function_tool
def generate_summary(transcript: str, template_content: str) -> str:
    """Generate summary based on transcript and template using GPT-4"""
    try:
        openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        report_prompt = f"""
        Based on the following audio transcript and template, generate a comprehensive report.
        
        Transcript:
        {transcript}
        
        Template Content:
        {template_content}
        
        
        Format the report according to the template instructions, in a structured, professional manner suitable for a business document.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are a professional report writer. Create clear, well-structured reports."},
                {"role": "user", "content": report_prompt}
            ],
            max_tokens=4000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Summary generation failed: {str(e)}")

# Define the Summarizer agent
summarizer_agent = Agent(
    name="Summarizer", 
    instructions="""You are a professional report writer. Create clear, well-structured reports based on transcripts which are the source text to be summarized and templates which are the instructions for the summary.
    
    INPUT: You will receive a transcript string and template content string.
    OUTPUT: You must return a SummarizerOutput object with the generated summary text.
    
    When given a transcript and template content, use the generate_summary tool to create a comprehensive report.
    Return a SummarizerOutput object with the generated summary text.""",
    tools=[generate_summary],
    output_type=SummarizerOutput
) 