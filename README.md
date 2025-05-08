# LinkedIn AI Auto-Poster

A Google Cloud Function that automatically generates and posts content to LinkedIn using AI. This function leverages OpenAI's capabilities to create engaging content based on specified topics and optionally includes AI-generated images.

## Features

- AI-powered content generation for LinkedIn posts
- Optional AI image generation
- Web content integration through provided links
- Customizable post length
- Secure handling of API keys and tokens

## Prerequisites

- Google Cloud Platform account
- LinkedIn Developer account with API access
- OpenAI API key
- Python 3.9+

## Setup

1. Clone this repository:
```bash
git clone https://github.com/yourusername/linkedin-ai-poster.git
cd linkedin-ai-poster
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Deploy to Google Cloud Functions:
```bash
gcloud functions deploy linkedin_ai_poster \
  --runtime python39 \
  --trigger-http \
  --allow-unauthenticated
```

## Usage

Send a POST request to the function endpoint with the following parameters:

```json
{
    "linkedin_token": "your_linkedin_token",
    "openai_api_key": "your_openai_key",
    "topic": "Your Topic",
    "links": ["https://example.com/article1"],
    "generate_image": true,
    "max_length": 2000
}
```

### Parameters

- `linkedin_token` (required): LinkedIn OAuth access token
- `openai_api_key` (required): OpenAI API key
- `topic` (required): Main topic for the post
- `links` (optional): List of URLs to include
- `generate_image` (optional): Whether to generate an AI image (default: false)
- `max_length` (optional): Maximum post length in characters (default: 3000)

## Security

- Never commit API keys or tokens to the repository
- Use environment variables or secure secret management for sensitive data
- Implement proper authentication for the function endpoint

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


curl -X POST https://www.linkedin.com/oauth/v2/accessToken \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=client_credentials&client_id=77le2gu24g5hrj&client_secret=WPL_AP1.hFtqaBLSian8gU96.8NmR5w=='



