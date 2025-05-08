
from agents import function_tool
from openai import OpenAI

import os
import logging


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@function_tool
def generate_linkedin_image(prompt: str) -> str:
    """
    Generate a business-appropriate image with DALL-E 3 and
    return the temporary CDN URL.

    Args:
        prompt: A concise description of the desired image

    Returns:
        str: URL of the generated image
    """
    try:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        # Use DALL-E 3 instead of GPT-Image-1
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="standard"  # DALL-E 3 specific parameter
        )
        return response.data[0].url
    except Exception as e:
        logger.error(f"Error generating image: {str(e)}")
        return f"Error generating image: {str(e)}"