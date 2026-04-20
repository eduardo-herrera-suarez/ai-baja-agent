import os
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
import time

def safe_generate(llm, prompt, fallback_llm=None):
    try:
        return llm.invoke(prompt)

    except Exception as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            print("⚠️ Gemini quota exceeded. Switching to fallback...")

            if fallback_llm:
                return fallback_llm.invoke(prompt)

            time.sleep(2)
            return llm.invoke(prompt)

        raise e

def get_llm(task: str = "default"):

    # 🔥 SMART ROUTING (not env-based)
    if task in ["classifier", "preferences", "food", "budget", "critic"]:
        return ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.2,
            api_key=os.getenv("GROQ_API_KEY")
        )

    elif task == "travel":
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.3,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

    else:
        return ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.2,
            api_key=os.getenv("GROQ_API_KEY")
        )

def get_llm2(task: str = "default"):
    provider = os.getenv("LLM_PROVIDER", "gemini")  # 🔥 default to free

    # ========================
    # 🟣 GROQ
    # ========================
    if provider == "groq":
        if task == "travel":
            model = "llama-3.3-70b-versatile"
        else:
            model = "llama-3.1-8b-instant"

        return ChatGroq(
            model=model,
            temperature=0.3,
            api_key=os.getenv("GROQ_API_KEY")
        )

    # ========================
    # 🔵 GEMINI (Google AI Studio)
    # ========================
    elif provider == "gemini":

        # 🔥 Use ONE model that works
        model_name = "gemini-2.5-flash"
        
        if task == "travel":
            temp = 0.3
        elif task in ["classifier", "preferences"]:
            temp = 0.0
        else:
            temp = 0.2

        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temp,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

    raise ValueError(f"Unsupported LLM provider: {provider}")