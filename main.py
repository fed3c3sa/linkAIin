import functions_framework
from flask import jsonify, Request
from typing import Optional, List, Dict, Any, Tuple
import os
import openai_utils
from linkedin_api import LinkedInAPI
import json
import logging
from agents import Runner
from email_send import send_email  # Import the email sending function
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set the OpenAI API key from the environment
def set_openai_api_env(api_key: str):
    """Set the OpenAI API key in the environment for the agents SDK."""
    os.environ["OPENAI_API_KEY"] = api_key
    

def format_engagement_analysis(engagement_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the engagement analysis for better readability.
    
    Args:
        engagement_analysis (Dict[str, Any]): Raw engagement analysis from the API
        
    Returns:
        Dict[str, Any]: Formatted engagement analysis
    """
    # If the engagement analysis is already formatted or is a string, return it as is
    if isinstance(engagement_analysis, str):
        return engagement_analysis
    
    # If it's a dictionary, format it better
    formatted_analysis = {}
    
    # Example formatting - adjust based on your actual response structure
    if 'score' in engagement_analysis:
        formatted_analysis['Engagement Score'] = f"{engagement_analysis['score']}/10"
    
    if 'strengths' in engagement_analysis:
        formatted_analysis['Key Strengths'] = engagement_analysis['strengths']
    
    if 'suggestions' in engagement_analysis:
        formatted_analysis['Improvement Suggestions'] = engagement_analysis['suggestions']
    
    if 'potential_reach' in engagement_analysis:
        formatted_analysis['Potential Reach'] = engagement_analysis['potential_reach']
    
    if 'target_audience' in engagement_analysis:
        formatted_analysis['Target Audience'] = engagement_analysis['target_audience']
    
    return formatted_analysis

@functions_framework.http
def linkedin_ai_poster(request):
    """
    Google Cloud Function that generates and posts content to LinkedIn OR sends the content via email.
    
    This function accepts HTTP POST requests with the following parameters:
    
    Args:
        request (flask.Request): The HTTP request object containing:
            - openai_api_key (str): OpenAI API key for AI content generation
            - topic (str): Main topic/subject for the post
            - links (List[str], optional): List of URLs to include in the post
            - generate_image (bool, optional): Flag to generate an AI image (default: False)
            - max_length (int, optional): Maximum character length for the post (default: 3000)
            - post_to_linkedin (bool, optional): Flag to post the content to LinkedIn (default: True)
            - linkedin_token (str, conditional): LinkedIn OAuth access token (required if post_to_linkedin is True)
            - send_email (bool, optional): Flag to send the post content via email (default: False)
            - email_app_password (str, conditional): App password for email sending (required if send_email is True)
            - destination_email (str, conditional): Email address to send the post to (required if send_email is True)
    
    Returns:
        tuple: A tuple containing:
            - dict: Response containing:
                - success (bool): Whether the operation was successful
                - post_url (str, optional): URL of the created LinkedIn post (if posted to LinkedIn)
                - email_sent (bool, optional): Whether the email was sent successfully (if sent via email)
                - error (str, optional): Error message if something went wrong
            - int: HTTP status code
    """
    # Check if request is a POST request
    if request.method != 'POST':
        return jsonify({
            'success': False,
            'error': 'Only POST requests are supported'
        }), 405
    
    try:
        # Parse request data
        request_json = request.get_json()
        if not request_json:
            return jsonify({
                'success': False,
                'error': 'Request body must contain valid JSON'
            }), 400
        
        # Extract common required parameters
        openai_api_key = request_json.get('openai_api_key')
        topic = request_json.get('topic')
        
        # Validate common required parameters
        if not openai_api_key:
            return jsonify({
                'success': False,
                'error': 'Missing OpenAI API key'
            }), 400
        if not topic:
            return jsonify({
                'success': False,
                'error': 'Missing post topic'
            }), 400
        
        # Extract optional parameters
        links = request_json.get('links', [])
        generate_image = request_json.get('generate_image', False)
        max_length = request_json.get('max_length', 3000)
        
        # Determine delivery method (LinkedIn or Email)
        post_to_linkedin = request_json.get('post_to_linkedin', True)
        send_email_flag = request_json.get('send_email', False)
        
        # Ensure only one delivery method is selected
        if post_to_linkedin and send_email_flag:
            return jsonify({
                'success': False,
                'error': 'Cannot both post to LinkedIn and send email - please choose one delivery method'
            }), 400
        
        # If neither delivery method is selected, default to LinkedIn
        if not post_to_linkedin and not send_email_flag:
            post_to_linkedin = True
        
        # Extract delivery-specific parameters
        linkedin_token = request_json.get('linkedin_token') if post_to_linkedin else None
        email_app_password = request_json.get('email_app_password') if send_email_flag else None
        destination_email = request_json.get('destination_email') if send_email_flag else None
        
        # Validate delivery-specific parameters
        if post_to_linkedin and not linkedin_token:
            return jsonify({
                'success': False,
                'error': 'Missing LinkedIn token for LinkedIn posting'
            }), 400
        
        if send_email_flag:
            if not email_app_password:
                return jsonify({
                    'success': False,
                    'error': 'Missing email app password for email delivery'
                }), 400
            if not destination_email:
                return jsonify({
                    'success': False,
                    'error': 'Missing destination email for email delivery'
                }), 400
        
        # Set OpenAI API key in environment for agents SDK
        set_openai_api_env(openai_api_key)
        
        # Initialize OpenAI client for direct API calls (like image generation)
        logger.info("Initializing OpenAI client")
        client = openai_utils.setup_openai_client(openai_api_key)
        
        # Search for content related to the topic
        logger.info(f"Searching for content related to: {topic}")
        search_results = openai_utils.search_web_content(topic, links)
        
        # Generate post content
        logger.info("Generating post content")
        post_content = openai_utils.generate_linkedin_post(topic, search_results, max_length)
        
        # Generate image if requested
        image_url = None
        image_data = None
        if generate_image:
            logger.info("Generating image for post")
            image_url = openai_utils.generate_post_image(topic, post_content, client)
            
            if image_url and send_email_flag:
                # Download the image for email embedding
                try:
                    logger.info("Downloading image for email embedding")
                    image_response = requests.get(image_url)
                    if image_response.status_code == 200:
                        image_data = image_response.content
                    else:
                        logger.warning(f"Failed to download image: HTTP {image_response.status_code}")
                except Exception as e:
                    logger.warning(f"Error downloading image: {str(e)}")
        
        # Analyze engagement potential
        logger.info("Analyzing engagement potential")
        engagement_analysis = openai_utils.analyze_engagement_potential(post_content)
        
        # Format engagement analysis for better readability
        formatted_engagement_analysis = format_engagement_analysis(engagement_analysis)
        
        # Initialize response variables
        post_url = None
        email_sent = False
        
        # Post to LinkedIn OR send email based on selected method
        if post_to_linkedin:
            logger.info("Posting content to LinkedIn")
            post_url = post_to_linkedin(linkedin_token, post_content, image_url)
            
            # Return success response for LinkedIn posting
            response = {
                'success': True,
                'delivery_method': 'linkedin',
                'post_url': post_url,
                'engagement_analysis': engagement_analysis,
                'post_content': post_content,
                'image_url': image_url
            }
            
        elif send_email_flag:
            try:
                logger.info(f"Sending email to {destination_email}")
                email_subject = f"AI-Generated Post: {topic}"
                
                # Format engagement analysis for better readability
                engagement_html = ""
                if isinstance(engagement_analysis, dict):
                    for key, value in engagement_analysis.items():
                        if isinstance(value, list):
                            items = "".join([f"• {item}<br>" for item in value])
                            engagement_html += f"<strong>{key}:</strong><br>{items}<br>"
                        else:
                            engagement_html += f"<strong>{key}:</strong> {value}<br><br>"
                else:
                    engagement_html = f"{engagement_analysis}"
                
                # Download image for embedding if available
                image_data = None
                if image_url and generate_image:
                    try:
                        logger.info("Downloading image for email embedding")
                        image_response = requests.get(image_url)
                        if image_response.status_code == 200:
                            image_data = image_response.content
                    except Exception as e:
                        logger.warning(f"Error downloading image: {str(e)}")
                
                # Create HTML email with the image embedded
                image_html = ""
                if image_url:
                    if image_data:
                        import base64
                        image_b64 = base64.b64encode(image_data).decode()
                        image_html = f'<div style="margin: 20px 0;"><img src="data:image/jpeg;base64,{image_b64}" style="max-width: 100%; height: auto;" alt="Generated image for post"></div>'
                    else:
                        image_html = f'<div style="margin: 20px 0;"><a href="{image_url}" target="_blank"><img src="{image_url}" style="max-width: 100%; height: auto;" alt="Generated image for post"></a></div>'
                
                # Format post content with proper spacing
                formatted_post = post_content.replace('\n', '<br>')
                
                # Create the HTML email body
                email_body = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                        .header {{ background-color: #0077B5; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                        .post-content {{ background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin-bottom: 20px; }}
                        .engagement {{ background-color: #f0f0f0; border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin-bottom: 20px; }}
                        .section-title {{ font-weight: bold; margin-top: 20px; margin-bottom: 10px; font-size: 18px; }}
                        .note {{ font-style: italic; color: #666; margin-top: 20px; font-size: 0.9em; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h2>AI-Generated LinkedIn Post: {topic}</h2>
                        </div>
                        
                        <div class="section-title">Post Content</div>
                        <div class="post-content">
                            {formatted_post}
                        </div>
                        
                        <div class="section-title">Engagement Analysis</div>
                        <div class="engagement">
                            {engagement_html}
                        </div>
                        
                        {image_html}
                        
                        <div class="note">
                            * You can copy and paste this content directly to LinkedIn. The engagement analysis is for your reference only.
                        </div>
                    </div>
                </body>
                </html>
                """
                
                # Create plain text version as fallback
                plain_email_body = f"""
                AI-Generated Post: {topic}
                
                {post_content}
                
                === ENGAGEMENT ANALYSIS ===
                {engagement_analysis}
                
                {f"Image URL: {image_url}" if image_url else "No image generated"}
                """
                
                # Call the email_send module's send_email function with HTML support
                send_email(
                    sender_email=destination_email,
                    recipient_email=destination_email,
                    subject=email_subject,
                    body=plain_email_body,
                    app_password=email_app_password,
                    html_body=email_body,
                    image_data=image_url if image_url else None
                )
                
                email_sent = True
                logger.info("Email sent successfully")
                
                # Return success response for email delivery
                response = {
                    'success': True,
                    'delivery_method': 'email',
                    'email_sent': email_sent,
                    'destination_email': destination_email,
                    'engagement_analysis': formatted_engagement_analysis,
                    'post_content': post_content,
                    'image_url': image_url
                }
                
            except Exception as e:
                logger.error(f"Error sending email: {str(e)}")
                return jsonify({
                    'success': False,
                    'delivery_method': 'email',
                    'error': f"Failed to send email: {str(e)}"
                }), 500
        
        return jsonify(response), 200
        
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return jsonify({
            'success': False,
            'error': str(ve)
        }), 400
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"An unexpected error occurred: {str(e)}"
        }), 500


def post_to_linkedin(linkedin_token: str, post_content: str, image_url: Optional[str] = None) -> str:
    """
    Post content to LinkedIn using the LinkedIn API.
    
    Args:
        linkedin_token (str): LinkedIn OAuth access token
        post_content (str): Content for the LinkedIn post
        image_url (Optional[str]): URL of an image to include in the post
    
    Returns:
        str: URL of the created LinkedIn post
    
    Raises:
        Exception: If posting to LinkedIn fails
    """
    try:
        # Initialize LinkedIn API client
        linkedin_api = LinkedInAPI(linkedin_token)
        
        # Get user info to ensure the token is valid
        user_info = linkedin_api.get_user_info()
        
        # Create post with or without image
        if image_url:
            logger.info("Creating LinkedIn post with image")
            post_data = linkedin_api.create_image_post(post_content, image_url)
        else:
            logger.info("Creating text-only LinkedIn post")
            post_data = linkedin_api.create_text_post(post_content)
        
        # Get the post URL
        post_url = linkedin_api.get_post_url(post_data)
        
        return post_url
        
    except Exception as e:
        logger.error(f"Error posting to LinkedIn: {str(e)}")
        raise Exception(f"Failed to post to LinkedIn: {str(e)}")


# We've removed the helper functions here to simplify the solution