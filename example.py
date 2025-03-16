import weaviate
from weaviate.classes.init import Auth, AdditionalConfig, Timeout
from dotenv import load_dotenv
import os

load_dotenv()

# Recommended: save sensitive data as environment variables
WEAVIATE_API_URL = os.getenv("WEAVIATE_API_URL", "http://localhost:8080")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
headers = {
    "X-OpenAI-Api-Key": OPENAI_API_KEY,
}

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=WEAVIATE_API_URL,                       # `weaviate_url`: your Weaviate URL
    auth_credentials=Auth.api_key(WEAVIATE_API_KEY),      # `weaviate_key`: your Weaviate API key
    headers=headers,
    additional_config=AdditionalConfig(
        timeout=Timeout(init=2, query=45, insert=120),  # Values in seconds
    )
)

print(client.is_ready())

