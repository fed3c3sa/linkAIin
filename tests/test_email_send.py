"""
Unit tests for the email sending functionality (utils/email/email_send.py)
"""

import unittest
from unittest.mock import patch, MagicMock, call
import io
import requests

# Import the function to test
from utils.email.email_send import send_email

class TestEmailSending(unittest.TestCase):
    """Test cases for email sending functionality"""

    def setUp(self):
        """Set up test fixtures"""
        # Default parameters for email sending
        self.sender_email = "sender@example.com"
        self.recipient_email = "recipient@example.com"
        self.subject = "Test Subject"
        self.body = "This is a test email body."
        self.app_password = "app_password_123"
        self.html_body = "<html><body><h1>Test Email</h1><p>This is a test.</p></body></html>"
        self.image_url = "https://example.com/image.jpg"

    @patch('smtplib.SMTP')
    def test_send_email_plain_text(self, mock_smtp):
        """Test sending a plain text email without HTML or image"""
        # Configure mock
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Call the function
        result = send_email(
            sender_email=self.sender_email,  # Make sure sender_email is first parameter
            app_password=self.app_password,
            recipient_email=self.recipient_email,
            subject=self.subject,
            body=self.body
        )
        
        # Assertions
        self.assertTrue(result)
        mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
        mock_server.ehlo.assert_called()
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with(self.sender_email, self.app_password)
        mock_server.sendmail.assert_called_once()
        self.assertEqual(mock_server.sendmail.call_args[0][0], self.sender_email)
        self.assertEqual(mock_server.sendmail.call_args[0][1], self.recipient_email)
        mock_server.quit.assert_called_once()

    @patch('smtplib.SMTP')
    def test_send_email_with_html(self, mock_smtp):
        """Test sending an email with HTML content"""
        # Configure mock
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Call the function
        result = send_email(
            sender_email=self.sender_email,  # Make sure sender_email is first parameter
            app_password=self.app_password,
            recipient_email=self.recipient_email,
            subject=self.subject,
            body=self.body,
            html_body=self.html_body
        )
        
        # Assertions
        self.assertTrue(result)
        mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
        mock_server.login.assert_called_once_with(self.sender_email, self.app_password)
        mock_server.sendmail.assert_called_once()
        
        # Check that the email contains both plain text and HTML parts
        email_content = mock_server.sendmail.call_args[0][2]
        self.assertIn('Content-Type: text/plain', email_content)
        self.assertIn('Content-Type: text/html', email_content)
        self.assertIn(self.body, email_content)
        self.assertIn(self.html_body, email_content)

    @patch('smtplib.SMTP')
    @patch('requests.get')
    def test_send_email_with_image(self, mock_requests_get, mock_smtp):
        """Test sending an email with an image attachment from URL"""
        # Configure mocks
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Mock successful image download with REAL image data for MIME type detection
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Use some minimal valid JPEG data
        mock_response.content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x15\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xbf\x80\x01\xff\xd9'
        mock_requests_get.return_value = mock_response
        
        # Call the function
        result = send_email(
            sender_email=self.sender_email,  # Make sure sender_email is first parameter
            app_password=self.app_password,
            recipient_email=self.recipient_email,
            subject=self.subject,
            body=self.body,
            image_data=self.image_url
        )
        
        # Assertions
        self.assertTrue(result)
        mock_requests_get.assert_called_once_with(self.image_url, timeout=30)
        mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
        mock_server.login.assert_called_once_with(self.sender_email, self.app_password)
        mock_server.sendmail.assert_called_once()
        
        # Just verify we attempted to send an email
        self.assertTrue(mock_server.sendmail.called)

    @patch('smtplib.SMTP')
    def test_authentication_error(self, mock_smtp):
        """Test handling of SMTP authentication errors"""
        # Configure mock to raise auth error
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, "Invalid credentials")
        
        # Call the function
        result = send_email(
            sender_email=self.sender_email,  # Make sure sender_email is first parameter
            app_password=self.app_password,
            recipient_email=self.recipient_email,
            subject=self.subject,
            body=self.body
        )
        
        # Assertions
        self.assertFalse(result)
        mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
        mock_server.login.assert_called_once_with(self.sender_email, self.app_password)
        mock_server.sendmail.assert_not_called()

    @patch('smtplib.SMTP')
    @patch('requests.get')
    def test_image_download_error(self, mock_requests_get, mock_smtp):
        """Test handling of image download errors"""
        # Configure mocks
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Mock failed image download
        mock_requests_get.side_effect = requests.RequestException("Connection error")
        
        # Call the function
        result = send_email(
            sender_email=self.sender_email,  # Make sure sender_email is first parameter
            app_password=self.app_password,
            recipient_email=self.recipient_email,
            subject=self.subject,
            body=self.body,
            image_data=self.image_url
        )
        
        # Assertions
        self.assertTrue(result)  # Email should still be sent, just without the image
        mock_requests_get.assert_called_once_with(self.image_url, timeout=30)
        mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
        mock_server.login.assert_called_once_with(self.sender_email, self.app_password)
        mock_server.sendmail.assert_called_once()
        
        # Email should not contain image attachment
        email_content = mock_server.sendmail.call_args[0][2]
        self.assertNotIn('Content-Disposition: attachment; filename="image.jpg"', email_content)


# Need to import the actual module to mock its exceptions
import smtplib

if __name__ == '__main__':
    unittest.main()