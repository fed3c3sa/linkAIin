"""
Pytest configuration file containing shared fixtures
"""

import pytest
from unittest.mock import MagicMock
import os

@pytest.fixture
def mock_openai_client():
    """
    Fixture that provides a mock OpenAI client.
    
    Returns:
        MagicMock: A mock OpenAI client object
    """
    client = MagicMock()
    # Configure image generation mock
    images = MagicMock()
    generate_response = MagicMock()
    generate_response.data = [MagicMock(url="https://example.com/generated-image.jpg")]
    images.generate.return_value = generate_response
    client.images = images
    
    return client

@pytest.fixture
def mock_linkedin_api():
    """
    Fixture that provides a mock LinkedIn API client.
    
    Returns:
        MagicMock: A mock LinkedIn API client object
    """
    api = MagicMock()
    api.get_user_info.return_value = {"id": "123456", "name": "Test User"}
    api.create_text_post.return_value = {"id": "post123", "url": "https://linkedin.com/post/123"}
    api.create_image_post.return_value = {"id": "post456", "url": "https://linkedin.com/post/456"}
    api.get_post_url.return_value = "https://linkedin.com/post/789"
    
    return api

@pytest.fixture
def set_env_vars():
    """
    Fixture that sets required environment variables for testing.
    """
    old_env = dict(os.environ)
    os.environ["OPENAI_API_KEY"] = "test_openai_api_key"
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(old_env)

@pytest.fixture
def mock_request_factory():
    """
    Fixture that returns a factory function for creating mock Flask requests.
    
    Returns:
        function: A factory function that creates mock requests with given JSON data
    """
    def _create_mock_request(data, method='POST'):
        mock_req = MagicMock()
        mock_req.method = method
        mock_req.get_json = MagicMock(return_value=data)
        return mock_req
    
    return _create_mock_request

@pytest.fixture
def sample_post_data():
    """
    Fixture that provides sample LinkedIn post data.
    
    Returns:
        str: A sample LinkedIn post content
    """
    return """
    🚀 Exciting New Developments in AI Engineering!
    
    Did you know that 78% of enterprises are now implementing AI in their operations? The landscape is evolving rapidly!
    
    Here are some key insights:
    • AI engineering frameworks have matured significantly in 2024
    • Companies adopting AI-first approaches see 35% higher productivity
    • Cross-functional AI teams deliver better results than siloed approaches
    
    What's your organization's AI adoption strategy? Let's discuss in the comments below!
    
    #AIEngineering #TechTrends #Innovation
    """

@pytest.fixture
def sample_search_results():
    """
    Fixture that provides sample search results data.
    
    Returns:
        dict: Sample structured search results
    """
    return {
        "verified": [
            {
                "fact": "78% of enterprises are implementing AI in their operations as of 2024",
                "title": "State of AI Report 2024",
                "author": "Tech Research Group",
                "date": "2024-02-15",
                "url": "https://example.com/ai-report-2024"
            },
            {
                "fact": "Companies with AI-first approaches report 35% higher productivity",
                "title": "AI Productivity Impact Study",
                "author": "Business Analytics Institute",
                "date": "2024-03-20",
                "url": "https://example.com/ai-productivity"
            }
        ],
        "additional": [
            {
                "fact": "Cross-functional AI teams show 40% better implementation success rates",
                "title": "Organizational Approaches to AI",
                "author": "Management Today",
                "date": "2024-01-10",
                "url": "https://example.com/ai-teams"
            }
        ],
        "stats": [
            {
                "label": "AI Implementation Rate",
                "value": 78,
                "unit": "%",
                "source": "https://example.com/ai-report-2024"
            },
            {
                "label": "Productivity Improvement",
                "value": 35,
                "unit": "%",
                "source": "https://example.com/ai-productivity"
            }
        ],
        "summary": "AI engineering is seeing rapid enterprise adoption with 78% of companies implementing AI solutions. Those taking AI-first approaches report significant productivity gains, and cross-functional teams show better implementation success rates than siloed approaches."
    }