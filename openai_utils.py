from typing import List, Dict, Optional
from agents import Runner
from ai_agents import search_agent, linkedin_poster_agent, image_generation_agent
import openai
from config import get_default_config
from tools import generate_linkedin_image
import asyncio
import nest_asyncio
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Apply nest_asyncio to allow running asyncio in already running event loops
# This helps with Google Cloud Functions environment
nest_asyncio.apply()

def setup_openai_client(api_key: str) -> openai.OpenAI:
    """
    Initialize the OpenAI client with the provided API key.
    
    Args:
        api_key (str): OpenAI API key
    
    Returns:
        openai.OpenAI: Initialized OpenAI client
    
    Raises:
        ValueError: If the API key is invalid or empty
    """
    if not api_key or not isinstance(api_key, str):
        raise ValueError("Invalid OpenAI API key provided")
    
    client = openai.OpenAI(api_key=api_key)
    return client


def search_web_content(topic: str, links: Optional[List[str]] = None) -> Dict:
    """
    Use OpenAI to search and analyze web content related to the topic.
    
    Args:
        topic (str): The main topic to search for
        links (Optional[List[str]]): Optional list of specific URLs to analyze
    
    Returns:
        Dict: A dictionary containing:
            - search_results (List[Dict]): List of relevant search results
            - summary (str): Brief summary of the findings
            - key_points (List[str]): Main points extracted from the content
    
    Raises:
        Exception: If the search or analysis fails
    """
    try:
        # Create search query
        search_query = f"Latest information about {topic}"
        
        # Add specific links if provided
        if links:
            search_query += f" focusing on these sources: {', '.join(links)}"
        
        # Create a new event loop if one doesn't exist
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError("Event loop is closed")
        except (RuntimeError, AssertionError):
            # Create a new event loop and set it as the current one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Define an async function to run the agent
        async def run_search_agent():
            return await Runner.run(search_agent, search_query)
        
        # Run the async function in the event loop
        if loop.is_running():
            # Use nest_asyncio to run in an already running loop
            result = asyncio.run_coroutine_threadsafe(
                run_search_agent(), loop
            ).result()
        else:
            # Run the coroutine in the loop
            result = loop.run_until_complete(run_search_agent())
        
        # Extract the response
        search_results = result.final_output
        
        if not search_results:
            raise Exception("No search results found")
        
        return search_results
    
    except Exception as e:
        logger.error(f"Error in search_web_content: {str(e)}")
        raise Exception(f"Failed to search and analyze web content: {str(e)}")


def generate_linkedin_post(topic: str, 
                         search_results: Dict,
                         max_length: int = 3000) -> str:
    """
    Generate a LinkedIn post based on the search results and topic.
    
    Args:
        topic (str): The main topic of the post
        search_results (Dict): Results from web search and analysis
        max_length (int): Maximum length of the post in characters
    
    Returns:
        str: Generated LinkedIn post content
    
    Raises:
        ValueError: If the content cannot be generated within max_length
    """
    config = get_default_config()
    
    # Ensure max_length is within allowed range
    if max_length < config["post"].min_post_length:
        max_length = config["post"].min_post_length
    elif max_length > config["post"].default_max_length:
        max_length = config["post"].default_max_length
    
    try:
        # Format the input for the LinkedIn post generator agent
        input_text = f"""
        Generate a LinkedIn post about {topic} within {max_length} characters.
        
        Use these search results:
        
        Summary: {search_results}
        
        
        Use maximum {config["post"].max_hashtags} hashtags and follow LinkedIn best practices.
        """
        
        # Create a new event loop if one doesn't exist
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError("Event loop is closed")
        except (RuntimeError, AssertionError):
            # Create a new event loop and set it as the current one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Define an async function to run the agent
        async def run_linkedin_agent():
            return await Runner.run(linkedin_poster_agent, input_text)
        
        # Run the async function in the event loop
        if loop.is_running():
            # Use nest_asyncio to run in an already running loop
            result = asyncio.run_coroutine_threadsafe(
                run_linkedin_agent(), loop
            ).result()
        else:
            # Run the coroutine in the loop
            result = loop.run_until_complete(run_linkedin_agent())
        
        # Extract the post content
        post_content = result.final_output
        
        # Validate post content
        if not post_content or not isinstance(post_content, str):
            raise ValueError("Failed to generate valid LinkedIn post content")
        
        # Truncate if necessary to ensure we're within the max_length
        if len(post_content) > max_length:
            post_content = post_content[:max_length]
        
        return post_content
    
    except Exception as e:
        logger.error(f"Error in generate_linkedin_post: {str(e)}")
        raise ValueError(f"Failed to generate LinkedIn post: {str(e)}")


def generate_post_image(topic: str, post_content: str, client) -> str:
    """
    Generate an AI image related to the post content using the generate_linkedin_image tool with DALL-E 3.
    
    Args:
        topic (str): The main topic
        post_content (str): The generated post content
        client: The OpenAI client instance (kept for compatibility)
    
    Returns:
        str: URL of the generated image
    
    Raises:
        Exception: If image generation fails
    """
    config = get_default_config()
    
    try:
        # Format the input for the image generation agent
        input_text = f"""
        Generate a detailed prompt for a professional LinkedIn image about {topic}.
        
        The post content is:
        {post_content[:300]}... (shortened for brevity)
        
        Create a detailed, high-quality prompt for DALL-E 3 that will produce a visually appealing and professional image.
        Make sure your prompt is detailed, specific, and designed to create a business-appropriate image.
        
        Then, use the generate_linkedin_image tool to create the image with your prompt.
        
        Return the image URL from the tool.
        """
        
        # Create a new event loop if one doesn't exist
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError("Event loop is closed")
        except (RuntimeError, AssertionError):
            # Create a new event loop and set it as the current one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Define an async function to run the agent
        async def run_image_agent():
            return await Runner.run(image_generation_agent, input_text)
        
        # Run the async function in the event loop
        if loop.is_running():
            # Use nest_asyncio to run in an already running loop
            result = asyncio.run_coroutine_threadsafe(
                run_image_agent(), loop
            ).result()
        else:
            # Run the coroutine in the loop
            result = loop.run_until_complete(run_image_agent())
        
        # Extract the image URL from the result
        image_url = result.final_output
        
        # Check if the result is a valid URL
        if not image_url or not isinstance(image_url, str) or not image_url.startswith("http"):
            logger.warning("Agent did not return a valid image URL. Attempting fallback...")
            
            # Fallback: try to extract a prompt from the result and generate image directly
            if hasattr(result, 'messages') and result.messages:
                prompt_text = None
                for msg in result.messages:
                    if hasattr(msg, 'content') and msg.content:
                        # Look for a detailed image description
                        for line in msg.content.split('\n'):
                            if len(line) > 40 and ":" not in line[:10] and not line.startswith("generate_linkedin_image"):
                                prompt_text = line
                                break
                
                if prompt_text:
                    # Try using our tool function directly
                    try:
                        image_url = generate_linkedin_image(prompt=prompt_text)
                    except Exception as e:
                        logger.error(f"Fallback attempt 1 failed: {str(e)}")
                        # Last resort - direct API call
                        response = client.images.generate(
                            model="dall-e-3",
                            prompt=f"Professional business image related to {topic}",
                            n=1,
                            size="1024x1024",
                            quality="standard"
                        )
                        image_url = response.data[0].url
                else:
                    # Last resort - direct API call
                    response = client.images.generate(
                        model="dall-e-3",
                        prompt=f"Professional business image related to {topic}",
                        n=1,
                        size="1024x1024",
                        quality="standard"
                    )
                    image_url = response.data[0].url
            else:
                # Last resort - direct API call
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=f"Professional business image related to {topic}",
                    n=1,
                    size="1024x1024",
                    quality="standard"
                )
                image_url = response.data[0].url
        
        return image_url
    
    except Exception as e:
        logger.error(f"Error in generate_post_image: {str(e)}")
        raise Exception(f"Failed to generate post image: {str(e)}")

def analyze_engagement_potential(post_content: str) -> Dict:
    """
    Analyze the potential engagement of the generated post.
    
    Args:
        post_content (str): The generated post content
    
    Returns:
        Dict: Analysis results containing:
            - engagement_score (float): Predicted engagement score
            - suggested_improvements (List[str]): List of suggestions
            - hashtag_suggestions (List[str]): Relevant hashtags
    
    Raises:
        Exception: If analysis fails
    """
    try:
        # Create a simple analysis of the post content
        word_count = len(post_content.split())
        
        # Calculate a basic engagement score (0-100)
        engagement_score = min(100, max(0, word_count / 30))
        
        # Generate suggestions based on post content
        suggestions = []
        
        if word_count < 50:
            suggestions.append("Consider adding more content for better engagement")
        elif word_count > 500:
            suggestions.append("Post might be too long for optimal engagement")
        
        if "#" not in post_content:
            suggestions.append("Consider adding relevant hashtags")
        
        # Extract or suggest hashtags
        hashtags = []
        for word in post_content.split():
            if word.startswith("#"):
                hashtags.append(word)
        
        if not hashtags:
            # Default hashtags if none found
            hashtags = ["#linkedin", "#professional", "#business"]
        
        return {
            "engagement_score": engagement_score,
            "suggested_improvements": suggestions,
            "hashtag_suggestions": hashtags
        }
    
    except Exception as e:
        logger.error(f"Error in analyze_engagement_potential: {str(e)}")
        raise Exception(f"Failed to analyze engagement potential: {str(e)}")