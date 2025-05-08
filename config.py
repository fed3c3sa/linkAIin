from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class OpenAIConfig:
    """Configuration settings for OpenAI integration."""
    model: str = "gpt-4"  # Default model for text generation
    image_model: str = "gpt-image-1"  # Updated default model for image generation
    temperature: float = 0.7
    max_tokens: int = 4000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

@dataclass
class SearchConfig:
    """Configuration settings for web search."""
    max_search_results: int = 5
    min_relevance_score: float = 0.7
    search_timeout: int = 30  # seconds

@dataclass
class PostConfig:
    """Configuration settings for LinkedIn post generation."""
    default_max_length: int = 3000
    min_post_length: int = 100
    max_hashtags: int = 5
    image_size: str = "1024x1024"
    image_quality: str = "standard"
    image_style: str = "natural"  # Added for GPT-Image-1

def get_default_config() -> Dict[str, Any]:
    """
    Get the default configuration settings.
    
    Returns:
        Dict[str, Any]: Dictionary containing all configuration settings
    """
    return {
        "openai": OpenAIConfig(),
        "search": SearchConfig(),
        "post": PostConfig()
    }