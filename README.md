# linkAIin - LinkedIn AI Auto-Poster

A Python-powered Google Cloud Function that automatically generates and posts engaging content to LinkedIn using AI. This project leverages OpenAI's GPT models to create professional, data-driven LinkedIn posts based on specified topics, and can optionally include AI-generated images.

## Features

- 🤖 AI-powered LinkedIn content generation
- 🔍 Web research capability to incorporate relevant information
- 🖼️ Optional AI image generation using OpenAI's image models
- 📊 Engagement analysis for created content
- 📧 Email delivery option as an alternative to direct LinkedIn posting
- 🔗 Integration with external web content through provided links
- ✏️ Customizable post length

## How It Works

1. **Research Phase**: The system searches the web for content related to your topic, with special focus on any links you provide.
2. **Content Generation**: Using OpenAI's models, it creates an engaging LinkedIn post based on the research.
3. **Image Creation**: Optionally generates a relevant image for your post.
4. **Engagement Analysis**: Analyzes the potential engagement of your post.
5. **Delivery**: Either posts directly to LinkedIn OR sends the content via email.

## Prerequisites

- Google Cloud Platform account
- LinkedIn Developer account with API access (for posting to LinkedIn)
- OpenAI API key
- Python 3.9+
- For email delivery: App password for your email account

## Local Setup

1. Clone this repository:
```bash
git clone https://github.com/federicocesarini1/linkAIin.git
cd linkAIin
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file for local environment variables:
```
OPENAI_API_KEY=your_openai_api_key
```

5. Run the function locally using Functions Framework:
```bash
functions-framework --target=linkedin_ai_poster --debug
```

6. Test the function with curl (or use Postman):
```bash
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "openai_api_key": "your_openai_api_key",
    "topic": "Latest trends in AI engineering",
    "links": ["https://example.com/article1"],
    "generate_image": true,
    "max_length": 2000,
    "post_to_linkedin": true,
    "linkedin_token": "your_linkedin_token"
  }'
```

## Email Delivery Option

If you prefer to receive the generated content via email instead of posting directly to LinkedIn:

```bash
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "openai_api_key": "your_openai_api_key",
    "topic": "Latest trends in AI engineering",
    "links": ["https://example.com/article1"],
    "generate_image": true,
    "max_length": 2000,
    "post_to_linkedin": false,
    "send_email": true,
    "email_app_password": "your_email_app_password",
    "destination_email": "your_email@example.com"
  }'
```

## Deploying to Google Cloud Functions

1. Ensure you have the Google Cloud SDK installed and configured.

2. Deploy the function:
```bash
gcloud functions deploy linkedin_ai_poster \
  --runtime python39 \
  --trigger-http \
  --allow-unauthenticated
```

3. For better security in production, add authentication:
```bash
gcloud functions deploy linkedin_ai_poster \
  --runtime python39 \
  --trigger-http \
  --no-allow-unauthenticated
```

4. Set necessary environment variables (optional but recommended):
```bash
gcloud functions deploy linkedin_ai_poster \
  --update-env-vars OPENAI_API_KEY=your_openai_api_key
```

## API Parameters

The function accepts the following parameters via POST request:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `openai_api_key` | string | Yes | OpenAI API key for AI content generation |
| `topic` | string | Yes | Main topic/subject for the post |
| `links` | array | No | List of URLs to include in research |
| `generate_image` | boolean | No | Whether to generate an AI image (default: false) |
| `max_length` | integer | No | Maximum character length for the post (default: 3000) |
| `post_to_linkedin` | boolean | No | Post content to LinkedIn (default: true) |
| `linkedin_token` | string | Conditional | Required if `post_to_linkedin` is true |
| `send_email` | boolean | No | Send content via email (default: false) |
| `email_app_password` | string | Conditional | Required if `send_email` is true |
| `destination_email` | string | Conditional | Required if `send_email` is true |

## Getting a LinkedIn Access Token

To get a LinkedIn access token for posting:

1. Create a LinkedIn Developer application at https://www.linkedin.com/developers/
2. Set up OAuth 2.0 settings with appropriate scopes (r_liteprofile, w_member_social)
3. Use the authorization flow to get your access token:

```bash
curl -X POST https://www.linkedin.com/oauth/v2/accessToken \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=authorization_code&code=YOUR_AUTH_CODE&client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET&redirect_uri=YOUR_REDIRECT_URI'
```

## Security Considerations

- Never commit API keys or tokens to the repository
- Use environment variables or secure secret management for sensitive data
- In production, implement proper authentication for the function endpoint
- Consider adding rate limiting to prevent abuse

## Project Structure

- `main.py`: Main Cloud Function entry point
- `config.py`: Configuration settings
- `ai_agents.py`: Definitions for AI agents handling various tasks
- `linkedin_api.py`: LinkedIn API integration

## Limitations

- LinkedIn access tokens expire after a limited time and need to be refreshed
- OpenAI API usage incurs costs based on token consumption
- LinkedIn API limitations may apply based on your developer account

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.