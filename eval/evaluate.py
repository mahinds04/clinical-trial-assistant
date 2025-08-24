"""Evaluation script for measuring retrieval accuracy."""
import json
from pathlib import Path
import pandas as pd
from src.rag.assistant import TrialAssistant

def load_test_cases():
    """Load test cases from JSON file."""
    with open(Path(__file__).parent / "test_cases.json") as f:
        return json.load(f)

def evaluate_retrieval(assistant, test_cases, k=5):
    """Evaluate retrieval accuracy on test cases."""
    results = {
        f"hit_rate@{k}": 0,
        f"precision@{k}": 0,
    }
    
    total = len(test_cases)
    hits = 0
    precision_sum = 0
    
    for case in test_cases:
        query = case["question"]
        expected_trials = set(case["relevant_trials"])
        
        retrieved_trials = assistant.retrieve_relevant_trials(query, k=k)
        retrieved_ids = set(trial.id for trial in retrieved_trials)
        
        # Calculate hits
        if len(expected_trials.intersection(retrieved_ids)) > 0:
            hits += 1
            
        # Calculate precision
        precision = len(expected_trials.intersection(retrieved_ids)) / k
        precision_sum += precision
    
    results[f"hit_rate@{k}"] = hits / total
    results[f"precision@{k}"] = precision_sum / total
    
    return results

def main():
    """Run evaluation and print results."""
    assistant = TrialAssistant()
    test_cases = load_test_cases()
    
    print("Running evaluation...")
    results = evaluate_retrieval(assistant, test_cases)
    
    print("\nResults:")
    for metric, value in results.items():
        print(f"{metric}: {value:.2f}")

if __name__ == "__main__":
    main()
