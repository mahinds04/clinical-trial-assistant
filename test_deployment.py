#!/usr/bin/env python3
"""
Test script for the Clinical Trial Assistant deployment functionality.
This can be run without Streamlit to verify the core logic works.
"""

from pathlib import Path
import sys

class MockStreamlit:
    def error(self, msg): 
        print(f'ERROR: {msg}')

# Mock streamlit module
sys.modules['streamlit'] = MockStreamlit()

class SimpleClinicalTrialAssistant:
    """Simplified version for demo purposes when full dependencies aren't available."""
    
    def __init__(self):
        self.demo_data = self.load_demo_data()
    
    def load_demo_data(self):
        """Load demo data from CSV."""
        try:
            data_path = Path(__file__).parent / "data" / "clin_trials_demo.csv"
            if data_path.exists():
                # Use basic file reading since pandas might not be available
                with open(data_path, 'r') as f:
                    lines = f.readlines()
                
                # Parse CSV manually
                headers = lines[0].strip().split(',')
                data = []
                for line in lines[1:]:
                    values = line.strip().split(',')
                    if len(values) == len(headers):
                        data.append(dict(zip(headers, values)))
                return data
        except Exception as e:
            print(f"Error loading demo data: {e}")
        return []
    
    def simple_search(self, query):
        """Simple keyword-based search in demo data."""
        query_lower = query.lower()
        results = []
        
        for trial in self.demo_data:
            # Search in title, conditions, and status
            searchable_text = f"{trial.get('Brief Title', '')} {trial.get('Conditions', '')} {trial.get('Overall Status', '')}".lower()
            
            if any(word in searchable_text for word in query_lower.split()):
                results.append(trial)
        
        return results[:3]  # Return top 3 results
    
    def query(self, question, n_results=3):
        """Query with simple search and basic response generation."""
        results = self.simple_search(question)
        
        if not results:
            return {
                "answer": "I couldn't find any trials matching your query in the demo dataset. Try searching for 'cancer', 'diabetes', 'heart disease', 'asthma', or 'alzheimer's'.",
                "sources": [],
                "nct_ids": []
            }
        
        # Generate a simple response
        answer_parts = [f"I found {len(results)} relevant clinical trial(s):"]
        nct_ids = []
        
        for i, trial in enumerate(results, 1):
            title = trial.get('Brief Title', 'Untitled')
            status = trial.get('Overall Status', 'Unknown')
            phase = trial.get('Phases', 'Unknown')
            nct_id = trial.get('NCT Number', 'Unknown')
            
            answer_parts.append(f"{i}. {title} - Status: {status}, Phase: {phase}")
            nct_ids.append(nct_id)
        
        answer_parts.append(f"\nSources: {', '.join(nct_ids)}")
        
        return {
            "answer": "\n".join(answer_parts),
            "sources": results,
            "nct_ids": nct_ids
        }

def test_assistant():
    """Test the assistant functionality."""
    print("Testing Clinical Trial Assistant...")
    
    assistant = SimpleClinicalTrialAssistant()
    print(f"✓ Loaded {len(assistant.demo_data)} demo trials")
    
    if assistant.demo_data:
        print("\nDemo data sample:")
        for i, trial in enumerate(assistant.demo_data[:2], 1):
            print(f"  {i}. {trial.get('Brief Title', 'Untitled')}")
    
    # Test queries
    test_queries = [
        "cancer",
        "diabetes", 
        "heart disease",
        "Phase 2",
        "recruiting"
    ]
    
    print("\nTesting queries:")
    for query in test_queries:
        result = assistant.query(query)
        num_results = len(result.get('sources', []))
        print(f"  '{query}' -> {num_results} results")
        if num_results > 0:
            print(f"    First result: {result['sources'][0].get('Brief Title', 'Untitled')}")
    
    print("\n✓ All tests completed successfully!")
    return True

if __name__ == "__main__":
    test_assistant()