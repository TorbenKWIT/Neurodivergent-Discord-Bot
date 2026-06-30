from google import genai
from config import GEMINI_API_KEY
import database

# Initialize the Gemini client
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    client = None
    print("Warning: GEMINI_API_KEY is not set in environment variables.")

# Use the modern gemini-2.5-flash model
MODEL_NAME = "gemini-2.5-flash"

async def _query_gemini(prompt: str) -> str:
    """Helper to query the Gemini API with caching."""
    if not client:
        return "Error: Gemini API key is not configured. Please set the GEMINI_API_KEY in your .env file."
        
    # Check cache first
    cached = database.get_cached_ai_response(prompt)
    if cached:
        return cached

    try:
        response = await client.aio.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
        text = response.text.strip()
        
        # Cache the response
        database.cache_ai_response(prompt, text)
        return text
    except Exception as e:
        return f"Error communicating with Gemini API: {str(e)}"

async def get_task_breakdown(task: str) -> str:
    """Uses Gemini API to break down an intimidating task into small, actionable steps."""
    prompt = (
        "You are an empathetic executive dysfunction helper. Break down the following task "
        "into small, manageable, bite-sized steps that are easy to start and complete. "
        "Use simple, concrete actions. Format the output as a clear list with checkboxes "
        "like `- [ ] Step detail`. Do not include any conversational filler (no hello, no here is your breakdown, "
        "no good luck) at the beginning or end.\n\n"
        f"Task: {task}"
    )
    return await _query_gemini(prompt)

async def reformat_readability(text: str) -> str:
    """Restructures a wall of text to improve visual readability (short paragraphs, bold key terms, lists)."""
    prompt = (
        "You are a readability helper for neurodivergent readers. Reformat the text below "
        "to make it extremely easy to read, scan, and digest. Follow these rules:\n"
        "1. Break any large blocks of text into short, clear paragraphs (maximum 2-3 sentences each).\n"
        "2. Bold key terms, action items, or critical facts so they stand out when scanning.\n"
        "3. Convert lists or sequences of steps into bullet points or numbered lists.\n"
        "4. Do NOT change the meaning or remove important information. Keep the original tone.\n"
        "5. Do NOT include any introductory or concluding conversational text. Return only the reformatted content.\n\n"
        f"Text to format:\n{text}"
    )
    return await _query_gemini(prompt)

async def summarize_text(text: str) -> str:
    """Generates a concise bulleted summary (TL;DR) of a long message."""
    prompt = (
        "Summarize the text below into a brief, clear, bulleted TL;DR list. "
        "Focus on the main takeaways and keep the wording simple and direct. "
        "Do NOT include any introductory or concluding conversational text.\n\n"
        f"Text to summarize:\n{text}"
    )
    return await _query_gemini(prompt)

async def suggest_tone_indicator(text: str) -> str:
    """Suggests tone indicators and provides brief reasons based on message text."""
    prompt = (
        "Analyze the emotional tone of the message below and suggest 1 or 2 standard "
        "tone indicators (e.g., /j for joking, /s for sarcasm, /srs for serious, /lh for lighthearted, "
        "/g or /gen for genuine, /nm for not mad, /pos for positive intent, /neg for negative intent, etc.) "
        "that best match the writer's intent.\n"
        "Format the output as follows:\n"
        "- **[tone indicator]** ([name]): [brief explanation of why it fits]\n\n"
        "Provide ONLY the suggestions. Do not write any greetings or concluding text.\n\n"
        f"Message:\n\"{text}\""
    )
    return await _query_gemini(prompt)
