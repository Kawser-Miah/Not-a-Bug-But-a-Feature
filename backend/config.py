from pydantic_settings import BaseSettings, SettingsConfigDict # pip install langchain-google-genai google-generativeai
from langchain.chat_models import init_chat_model
from langchain_groq import ChatGroq

class Settings(BaseSettings):
    GOOGLE_API_KEY:str
    GROQ_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings() #type: ignore

# llm = init_chat_model(
#     "gemini-2.5-flash",
#     model_provider="google_genai",
#     google_api_key=settings.GOOGLE_API_KEY
# )
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.3,
    api_key=settings.GROQ_API_KEY,
    max_tokens=2048
)

