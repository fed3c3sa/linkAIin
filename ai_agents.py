from agents import Agent, function_tool, WebSearchTool
from tools import generate_linkedin_image
from typing import List, Dict, Any, Optional
import os

# Tool for web searches
@function_tool
def web_search(query: str) -> Dict[str, Any]:
    """
    Search the web for information.
    
    Args:
        query (str): The search query
        
    Returns:
        Dict[str, Any]: A dictionary containing search results
    """
    # In a real implementation, this would call an actual search API
    # This is a placeholder implementation
    return {
        "results": [
            {"title": f"Search result for {query}", "snippet": f"This is a snippet for {query}"}
        ],
        "summary": f"Summary of search results for {query}",
        "key_points": [f"Key point about {query}"]
    }

# Create search agent
search_agent = Agent(
    name="Search Agent",
    instructions="""You are a search agent that searches the web for information.
    1. If you receive a list of links, those results needs to be put in the <verified results section>
    2. In case there are links the information not coming from the verified links needs to be put in the <unverified links section>
    3. In case there are no links, just put all the information in a text with no sections""",
    tools=[WebSearchTool()],
)

# Create LinkedIn post generator agent
linkedin_poster_agent = Agent(
    name="LinkedIn Post Generator",
    instructions="""You are a professional LinkedIn content creator. Your task is to:
    1. Take search results and convert them into engaging LinkedIn posts
    2. Follow LinkedIn best practices for professional content
    3. Include relevant hashtags
    4. Maintain a professional yet engaging tone
    5. Structure the post with clear sections and formatting
    6. Ensure the content is within the specified character limit
    7. Add a call-to-action when appropriate
    8. Include relevant statistics or data points when available
    9. Make the content shareable and valuable to the professional community
    10. Add links to the content when appropriate citing the source
    11. You might receive verified and unverified sections, respect the sections in the final post""",
    tools=[WebSearchTool()],
)

# Create image generation agent
# Create image generation agent
image_generation_agent = Agent(
    name="LinkedIn Image Generator",
    instructions="""You are a professional image creator for LinkedIn posts. Your task is to:
    1. Generate professional, business-appropriate images for LinkedIn posts
    2. Create images that directly complement the post content
    3. Ensure images are optimized for LinkedIn's display
    4. Generate images with a professional and modern aesthetic
    5. Create visually appealing compositions suitable for business context
    6. Consider brand consistency in the generated images
    7. Ensure images enhance the post's message
    8. Create accessible and inclusive imagery
    9. Do not include any text in the images, just the image itself
    10. Use appropriate color schemes for professional contexts
    
    You have access to the generate_linkedin_image tool for image generation. 
    
    IMPORTANT: When asked to create an image, you should:
    1. First create a detailed image prompt based on the context provided
    2. Then call the generate_linkedin_image tool with these parameters:
       - prompt: Your detailed image description
       - size: "1024x1024"
    3. Return only the image URL from the tool's response, no other text, nothing else. Just the url starting with https://
    
    Always use the exact parameter names and string values shown above.
    """,
    tools=[generate_linkedin_image],  # Include your tool here
)