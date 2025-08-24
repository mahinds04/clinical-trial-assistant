import pandas as pd
from chromadb import Client, Settings
from tqdm import tqdm
from pathlib import Path

# Get the project root directory
ROOT_DIR = Path(__file__).parent.parent.parent

def load_clinical_trials(csv_path: str) -> pd.DataFrame:
    """Load clinical trials data from CSV file."""
    return pd.read_csv(csv_path)

def create_vector_store(df: pd.DataFrame, persist_directory: str):
    """Create and persist a vector store from clinical trials data."""
    print(f"Initializing ChromaDB with persist_directory: {persist_directory}")
    client = Client(Settings(
        persist_directory=persist_directory,
        is_persistent=True
    ))
    
    print("Checking for existing collections...")
    existing_collections = client.list_collections()
    print(f"Found collections: {[c.name for c in existing_collections]}")
    
    # Delete collection if it exists
    try:
        client.delete_collection("clinical_trials")
        print("Deleted existing clinical_trials collection")
    except:
        print("No existing collection to delete")
        
    print("Creating new clinical_trials collection...")
    collection = client.create_collection(
        name="clinical_trials",
        metadata={"description": "Clinical trials database"}
    )
    print("Collection created successfully")
    
    # Process in batches of 500 for better performance
    BATCH_SIZE = 500
    total_batches = (len(df) + BATCH_SIZE - 1) // BATCH_SIZE
    
    for batch_idx in tqdm(range(total_batches), desc="Processing batches"):
        start_idx = batch_idx * BATCH_SIZE
        end_idx = min((batch_idx + 1) * BATCH_SIZE, len(df))
        batch = df.iloc[start_idx:end_idx]
        
        documents = []
        ids = []
        metadatas = []
        
        for idx, row in batch.iterrows():
            # Create document text combining brief and full title with conditions
            doc_text = f"Brief Title: {row['Brief Title']}\n\n"
            doc_text += f"Full Title: {row['Full Title']}\n\n"
            doc_text += f"Conditions: {row['Conditions']}\n\n"
            if pd.notna(row['Intervention Description']):
                doc_text += f"Intervention: {row['Intervention Description']}"
            
            documents.append(doc_text)
            ids.append(str(idx))
            metadatas.append({
                "brief_title": str(row["Brief Title"]),
                "status": str(row["Overall Status"]),
                "phase": str(row["Phases"]),
                "condition": str(row["Conditions"]),
                "purpose": str(row["Primary Purpose"]),
                "start_date": str(row["Start Date"])
            })
        
        # Add batch to collection
        collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
    
    return collection

if __name__ == "__main__":
    deployment_env = os.getenv("DEPLOYMENT_ENV", "cloud")
    
    # Use demo dataset for cloud deployment
    if deployment_env == "cloud":
        data_path = ROOT_DIR / "data" / "clin_trials_demo.csv"
    else:
        data_path = ROOT_DIR / "data" / "clin_trials.csv"
    
    chroma_path = ROOT_DIR / "data" / "chroma_db"
    print(f"Loading data from: {data_path}")
    print(f"Creating index in: {chroma_path}")
    
    # Load the data
    df = load_clinical_trials(str(data_path))
    print(f"Loaded {len(df)} trials")
    
    # Create the vector store
    create_vector_store(df, str(chroma_path))
