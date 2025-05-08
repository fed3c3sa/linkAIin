import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import logging
import requests  # Add this import to fetch the image

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def send_email(sender_email, app_password, recipient_email, subject, body, html_body=None, image_data=None):
    """
    Send an email using Gmail's SMTP server with an app password.
    Supports both plain text and HTML emails, with optional image attachment.
    
    Parameters:
    sender_email (str): Your Gmail email address
    app_password (str): Your Gmail app password (NOT your regular Gmail password)
                        Generate at: https://myaccount.google.com/apppasswords
    recipient_email (str): Recipient's email address
    subject (str): Email subject
    body (str): Email body content (plain text)
    html_body (str, optional): HTML version of the email body
    image_data (str, optional): URL to the image to include in the email
    
    Returns:
    bool: True if email was sent successfully, False otherwise
    """
    # Convert strings from bytes if needed
    if isinstance(body, bytes):
        body = body.decode('utf-8')
        
    if html_body is not None and isinstance(html_body, bytes):
        html_body = html_body.decode('utf-8')
    
    if subject is not None and isinstance(subject, bytes):
        subject = subject.decode('utf-8')
    
    # Create a multipart message
    message = MIMEMultipart('alternative' if html_body else 'mixed')
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject
    
    # Add plain text body to email
    text_part = MIMEText(body, "plain")
    message.attach(text_part)
    
    # If HTML body is provided, add it to the email
    if html_body:
        html_part = MIMEText(html_body, "html")
        message.attach(html_part)
    
    # If image data (URL) is provided, download and add it as an attachment
    if image_data and isinstance(image_data, str) and image_data.startswith('http'):
        try:
            # Download the image from the URL
            logger.info(f"Downloading image from URL: {image_data[:60]}...")
            response = requests.get(image_data, timeout=30)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            # Get the image data as bytes
            img_bytes = response.content
            
            # Create the image attachment
            image = MIMEImage(img_bytes)
            image.add_header('Content-Disposition', 'attachment', filename='image.jpg')
            message.attach(image)
            logger.info("Image successfully attached to email")
        except Exception as e:
            logger.error(f"Error downloading or processing image: {str(e)}")
            # Continue without the image rather than failing the whole email
    
    # Initialize server variable outside try block
    server = None
    
    try:
        # Create SMTP session
        logger.info("Connecting to Gmail SMTP server...")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()  # Identify ourselves to the server
        server.starttls()  # Secure the connection
        server.ehlo()  # Re-identify ourselves over TLS connection
        
        # Login to sender email with app password
        logger.info(f"Logging in as {sender_email}...")
        server.login(sender_email, app_password)
        
        # Send email
        text = message.as_string()
        logger.info(f"Sending email to {recipient_email}...")
        server.sendmail(sender_email, recipient_email, text)
        
        logger.info("Email sent successfully!")
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error("Authentication failed. Make sure you're using an app password, not your regular Gmail password.")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending email: {e}")
        return False
    finally:
        # Close the connection if it was opened
        if server:
            server.quit()
            logger.info("SMTP connection closed")