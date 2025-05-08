"""
Unit tests for the main Cloud Function handler (main.py)
"""

import unittest
from unittest.mock import patch, MagicMock, Mock
import json
import os

# Import the function to test
import main
from config import get_default_config

class MockResponse:
    """
    Mock response object to simulate Flask's jsonify return value
    """
    def __init__(self, data, status_code=200):
        self.data = json.dumps(data).encode('utf-8')
        self.status_code = status_code
    
    def get_data(self, as_text=False):
        if as_text:
            return self.data.decode('utf-8')
        return self.data

class TestLinkedInAIPoster(unittest.TestCase):
    """Test cases for the linkedin_ai_poster Cloud Function"""

    def setUp(self):
        """Set up test fixtures"""
        # Default valid request data
        self.valid_request_data = {
            'openai_api_key': 'test_api_key',
            'topic': 'AI in Healthcare',
            'links': ['https://example.com/ai-healthcare'],
            'generate_image': True,
            'max_length': 2000,
            'post_to_linkedin': True,
            'linkedin_token': 'test_linkedin_token'
        }
        
        # Test configurations
        self.config = get_default_config()

        # Mock for jsonify
        self.jsonify_patcher = patch('main.jsonify', side_effect=self._mock_jsonify)
        self.mock_jsonify = self.jsonify_patcher.start()

    def tearDown(self):
        """Clean up after each test"""
        self.jsonify_patcher.stop()

    def _mock_jsonify(self, *args, **kwargs):
        """Mock implementation of Flask's jsonify function"""
        # If args is provided, use the first arg as data
        if args:
            return MockResponse(args[0])
        # Otherwise use kwargs as data
        return MockResponse(kwargs)

    def _create_mock_request(self, data):
        """Helper to create a mock request with the specified JSON data"""
        mock_req = MagicMock()
        mock_req.method = 'POST'
        mock_req.get_json = MagicMock(return_value=data)
        return mock_req


    @patch('main.set_openai_api_env')
    @patch('main.openai_utils.setup_openai_client')
    @patch('main.openai_utils.search_web_content')
    @patch('main.openai_utils.generate_linkedin_post')
    @patch('main.openai_utils.generate_post_image')
    @patch('main.openai_utils.analyze_engagement_potential')
    @patch('main.send_email')
    def test_email_delivery_success(self, mock_send_email, mock_analyze, 
                                 mock_gen_image, mock_gen_post, mock_search, 
                                 mock_setup_client, mock_set_api_env):
        """Test successful email delivery flow"""
        # Configure mocks
        mock_search.return_value = {"verified": [], "additional": [], "summary": "Test summary"}
        mock_gen_post.return_value = "This is a test LinkedIn post"
        mock_gen_image.return_value = "https://example.com/test-image.jpg"
        mock_analyze.return_value = {"engagement_score": 85, "suggested_improvements": []}
        mock_send_email.return_value = True
        
        # Create request with email delivery
        email_request_data = {
            'openai_api_key': 'test_api_key',
            'topic': 'AI in Healthcare',
            'generate_image': True,
            'post_to_linkedin': False,
            'send_email': True,
            'email_app_password': 'test_password',
            'destination_email': 'test@example.com'
        }
        mock_request = self._create_mock_request(email_request_data)
        
        # Call the function
        response, status_code = main.linkedin_ai_poster(mock_request)
        response_data = json.loads(response.get_data())
        
        # Assertions
        self.assertEqual(status_code, 200)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['delivery_method'], 'email')
        self.assertTrue(response_data['email_sent'])
        self.assertEqual(response_data['destination_email'], 'test@example.com')
        
        # Verify mock calls
        mock_set_api_env.assert_called_once_with('test_api_key')
        mock_setup_client.assert_called_once()
        mock_send_email.assert_called_once()

    def test_invalid_request_method(self):
        """Test rejection of non-POST requests"""
        mock_request = MagicMock()
        mock_request.method = 'GET'
        
        response, status_code = main.linkedin_ai_poster(mock_request)
        response_data = json.loads(response.get_data())
        
        self.assertEqual(status_code, 405)
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['error'], 'Only POST requests are supported')

    def test_missing_required_parameters(self):
        """Test validation of required parameters"""
        # Test missing OpenAI API key
        request_data = self.valid_request_data.copy()
        del request_data['openai_api_key']
        mock_request = self._create_mock_request(request_data)
        
        response, status_code = main.linkedin_ai_poster(mock_request)
        response_data = json.loads(response.get_data())
        
        self.assertEqual(status_code, 400)
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['error'], 'Missing OpenAI API key')
        
        # Test missing topic
        request_data = self.valid_request_data.copy()
        del request_data['topic']
        mock_request = self._create_mock_request(request_data)
        
        response, status_code = main.linkedin_ai_poster(mock_request)
        response_data = json.loads(response.get_data())
        
        self.assertEqual(status_code, 400)
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['error'], 'Missing post topic')

    def test_conflicting_delivery_methods(self):
        """Test validation of delivery method selection"""
        # Test both delivery methods selected
        request_data = self.valid_request_data.copy()
        request_data['send_email'] = True
        request_data['email_app_password'] = 'test_password'
        request_data['destination_email'] = 'test@example.com'
        mock_request = self._create_mock_request(request_data)
        
        response, status_code = main.linkedin_ai_poster(mock_request)
        response_data = json.loads(response.get_data())
        
        self.assertEqual(status_code, 400)
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['error'], 
                         'Cannot both post to LinkedIn and send email - please choose one delivery method')


if __name__ == '__main__':
    unittest.main()