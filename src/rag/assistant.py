from typing import List, Dict, Optional
from pathlib import Path
import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain_community.llms import Ollama, HuggingFaceHub
from chromadb import Client, Settings

# Load environment variables
load_dotenv()

def get_llm(model_name: str = "google/flan-t5-large"):
    """
    Get the appropriate LLM based on environment and configuration.
    """
    deployment_env = os.getenv("DEPLOYMENT_ENV", "cloud")
    
    if deployment_env == "local":
        return Ollama(model=model_name)
    else:
        # Cloud deployment - use HuggingFace's free models
        from huggingface_hub.inference._text_generation import TextGenerationService
        from langchain_community.llms import HuggingFaceEndpoint

        return HuggingFaceEndpoint(
            endpoint_url="https://api-inference.huggingface.co/models/google/flan-t5-large",
            task="text2text-generation",
            temperature=0.7,
            max_length=512
        )

class ClinicalTrialAssistant:
    def __init__(self, model_name: Optional[str] = None, persist_directory: Optional[str] = None):
        """Initialize the clinical trial assistant with the appropriate LLM and ChromaDB."""
        if persist_directory is None:
            persist_directory = str(Path(__file__).parent.parent.parent / "data" / "chroma_db")
        print(f"Initializing ChromaDB with persist_directory: {persist_directory}")
        
        # Initialize LLM
        deployment_env = os.getenv("DEPLOYMENT_ENV", "cloud")
        if deployment_env == "local":
            self.model_name = model_name or "llama2"
        else:
            self.model_name = model_name or "gpt-3.5-turbo"
        
        self.llm = get_llm(self.model_name)
        
        # Initialize ChromaDB
        self.client = Client(Settings(
            persist_directory=persist_directory,
            is_persistent=True
        ))
        
        # List all collections
        collections = self.client.list_collections()
        print(f"Available collections: {[c.name for c in collections]}")
        
        try:
            self.collection = self.client.get_collection("clinical_trials")
            print("Successfully connected to clinical_trials collection")
        except Exception as e:
            print(f"Error accessing collection: {e}")
            print("Creating new collection...")
            self.collection = self.client.create_collection(
                name="clinical_trials",
                metadata={"description": "Clinical trials database"}
            )
        self.llm = Ollama(model=model_name)
        
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a helpful clinical trial assistant. Use the following context about clinical trials to answer the question. Be concise and focus on the most relevant trials.
            
Context about clinical trials:
{context}

Question: {question}

Answer the question based on the above context. Include key information such as trial status, phase, and start date when relevant. If specific details aren't available in the context, don't make assumptions."""
        )
        
    def query(self, question: str, n_results: int = 3) -> Dict:
        """Query the clinical trials database and generate a response."""
        # Get relevant documents
        results = self.collection.query(
            query_texts=[question],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        
        # Sort results by relevance score
        sorted_indices = sorted(range(len(results["distances"][0])), 
                              key=lambda i: results["distances"][0][i])
        
        # Take only the most relevant parts of each document
        contexts = []
        metadata_list = []
        for idx in sorted_indices[:2]:  # Use only top 2 most relevant results
            doc = results["documents"][0][idx]
            # Extract just the title and first 100 characters of description
            if "\n\n" in doc:
                title, desc = doc.split("\n\n", 1)
                context = f"{title}\n{desc[:100]}..."
            else:
                context = doc[:150] + "..."
            contexts.append(context)
            metadata_list.append(results["metadatas"][0][idx])
        
        context = "\n---\n".join(contexts)
        
        # Generate response using Ollama with timeout
        prompt = self.prompt_template.format(context=context, question=question)
        try:
            response = self.llm(prompt, temperature=0.7, timeout=10)  # 10 second timeout
        except Exception as e:
            print(f"Model response timeout: {e}")
            response = "I apologize, but I'm taking too long to process this request. Could you try rephrasing your question?"
        
        return {
            "answer": response,
            "sources": metadata_list
        }
