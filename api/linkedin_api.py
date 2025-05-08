from typing import Optional, Dict, Any
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LinkedInAPI:
    """
    A class to handle interactions with the LinkedIn API.
    """
    
    def __init__(self, access_token: str):
        """
        Initialize the LinkedIn API client.
        
        Args:
            access_token (str): LinkedIn OAuth access token
        """
        self.access_token = access_token
        self.base_url = "https://api.linkedin.com/v2"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        self.user_urn = None
    
    def get_user_info(self) -> Dict[str, Any]:
        """
        Get information about the authenticated user.
        
        Returns:
            Dict[str, Any]: User information
            
        Raises:
            Exception: If the API request fails
        """
        endpoint = f"{self.base_url}/me"
        response = requests.get(endpoint, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get user info: {response.text}")
        
        user_info = response.json()
        self.user_urn = user_info.get("id")
        
        return user_info
    
    def register_image(self, user_urn: str) -> Dict[str, Any]:
        """
        Register an image upload with LinkedIn.
        
        Args:
            user_urn (str): LinkedIn user URN
            
        Returns:
            Dict[str, Any]: Registration information including upload URL and asset ID
            
        Raises:
            Exception: If the API request fails
        """
        endpoint = f"{self.base_url}/assets?action=registerUpload"
        data = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": f"urn:li:person:{user_urn}",
                "serviceRelationships": [{
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }]
            }
        }
        
        response = requests.post(endpoint, json=data, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to register image upload: {response.text}")
        
        return response.json()
    
    def upload_image(self, upload_url: str, image_data: bytes) -> bool:
        """
        Upload an image to LinkedIn using the provided upload URL.
        
        Args:
            upload_url (str): URL for uploading the image
            image_data (bytes): Raw image data
            
        Returns:
            bool: True if upload was successful, False otherwise
            
        Raises:
            Exception: If the API request fails
        """
        # Upload headers without content type and authorization
        upload_headers = {
            "Content-Type": "image/jpeg"  # Assuming JPEG format
        }
        
        response = requests.put(upload_url, data=image_data, headers=upload_headers)
        
        if response.status_code < 200 or response.status_code >= 300:
            logger.error(f"Failed to upload image: {response.text}")
            return False
        
        return True
    
    def create_text_post(self, text_content: str) -> Dict[str, Any]:
        """
        Create a text-only post on LinkedIn.
        
        Args:
            text_content (str): The text content of the post
            
        Returns:
            Dict[str, Any]: Response data from LinkedIn API
            
        Raises:
            Exception: If the API request fails or if user_urn is not available
        """
        if not self.user_urn:
            self.get_user_info()
        
        endpoint = f"{self.base_url}/ugcPosts"
        data = {
            "author": f"urn:li:person:{self.user_urn}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text_content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        response = requests.post(endpoint, json=data, headers=self.headers)
        
        if response.status_code < 200 or response.status_code >= 300:
            raise Exception(f"Failed to create post: {response.text}")
        
        return response.json()
    
    def create_image_post(self, text_content: str, image_url: str) -> Dict[str, Any]:
        """
        Create a post with an image on LinkedIn.
        
        Args:
            text_content (str): The text content of the post
            image_url (str): URL of the image to include
            
        Returns:
            Dict[str, Any]: Response data from LinkedIn API
            
        Raises:
            Exception: If the API request fails or if user_urn is not available
        """
        if not self.user_urn:
            self.get_user_info()
        
        try:
            # Download the image
            image_response = requests.get(image_url)
            
            if image_response.status_code != 200:
                logger.warning(f"Failed to download image from {image_url}")
                # Fall back to text-only post
                return self.create_text_post(text_content)
            
            # Register the image with LinkedIn
            register_info = self.register_image(self.user_urn)
            
            # Extract upload URL and asset ID
            upload_url = register_info.get("value", {}).get("uploadMechanism", {}).get("com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {}).get("uploadUrl")
            asset_id = register_info.get("value", {}).get("asset")
            
            if not upload_url or not asset_id:
                logger.warning("Failed to get upload URL or asset ID")
                # Fall back to text-only post
                return self.create_text_post(text_content)
            
            # Upload the image
            upload_success = self.upload_image(upload_url, image_response.content)
            
            if not upload_success:
                # Fall back to text-only post
                return self.create_text_post(text_content)
            
            # Create post with the image
            endpoint = f"{self.base_url}/ugcPosts"
            data = {
                "author": f"urn:li:person:{self.user_urn}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text_content
                        },
                        "shareMediaCategory": "IMAGE",
                        "media": [{
                            "status": "READY",
                            "description": {
                                "text": "Generated image for the post"
                            },
                            "media": asset_id
                        }]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            response = requests.post(endpoint, json=data, headers=self.headers)
            
            if response.status_code < 200 or response.status_code >= 300:
                raise Exception(f"Failed to create post with image: {response.text}")
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error creating image post: {str(e)}")
            # Fall back to text-only post
            return self.create_text_post(text_content)
    
    def get_post_url(self, post_data: Dict[str, Any]) -> str:
        """
        Get the URL for a created LinkedIn post.
        
        Args:
            post_data (Dict[str, Any]): Response data from post creation
            
        Returns:
            str: URL of the LinkedIn post
        """
        post_id = post_data.get("id", "")
        
        if not post_id:
            return "https://www.linkedin.com/feed"
        
        # Construct post URL
        return f"https://www.linkedin.com/feed/update/{post_id}"