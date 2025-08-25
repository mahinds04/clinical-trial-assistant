"""Simplified assistant for cloud deployment."""
from typing import Optional, Dict
import os

class SimpleClinicalTrialAssistant:
    """Simplified version that works without heavy dependencies."""
    
    def __init__(self):
        self.sample_trials = [
            {
                "brief_title": "Immunotherapy for Advanced Melanoma",
                "phase": "Phase 3",
                "status": "Recruiting",
                "purpose": "Treatment",
                "start_date": "2024-01-15",
                "nct_id": "NCT12345678",
                "condition": "Melanoma"
            },
            {
                "brief_title": "Novel Diabetes Drug Trial",
                "phase": "Phase 2",
                "status": "Active",
                "purpose": "Treatment", 
                "start_date": "2024-03-20",
                "nct_id": "NCT87654321",
                "condition": "Type 2 Diabetes"
            },
            {
                "brief_title": "COVID-19 Vaccine Safety Study",
                "phase": "Phase 3",
                "status": "Completed",
                "purpose": "Prevention",
                "start_date": "2023-11-10",
                "nct_id": "NCT11111111", 
                "condition": "COVID-19"
            },
            {
                "brief_title": "Alzheimer's Disease Treatment Trial",
                "phase": "Phase 2",
                "status": "Recruiting",
                "purpose": "Treatment",
                "start_date": "2024-05-01",
                "nct_id": "NCT22222222",
                "condition": "Alzheimer's Disease"
            },
            {
                "brief_title": "Breast Cancer Combination Therapy",
                "phase": "Phase 3", 
                "status": "Active",
                "purpose": "Treatment",
                "start_date": "2024-02-28",
                "nct_id": "NCT33333333",
                "condition": "Breast Cancer"
            }
        ]
    
    def query(self, question: str, n_results: int = 3) -> Dict:
        """Simple query using keyword matching."""
        question_lower = question.lower()
        
        # Simple keyword matching
        relevant_trials = []
        for trial in self.sample_trials:
            score = 0
            trial_text = f"{trial['brief_title']} {trial['condition']} {trial['purpose']}".lower()
            
            # Basic keyword scoring
            keywords = ["cancer", "diabetes", "covid", "alzheimer", "breast", "melanoma", 
                       "immunotherapy", "vaccine", "treatment", "phase"]
            
            for keyword in keywords:
                if keyword in question_lower and keyword in trial_text:
                    score += 1
            
            if score > 0:
                relevant_trials.append((trial, score))
        
        # Sort by relevance and take top results
        relevant_trials.sort(key=lambda x: x[1], reverse=True)
        top_trials = [trial for trial, score in relevant_trials[:n_results]]
        
        # If no relevant trials found, return some sample trials
        if not top_trials:
            top_trials = self.sample_trials[:n_results]
        
        # Generate simple response
        if "cancer" in question_lower:
            answer = f"Found {len(top_trials)} cancer-related clinical trials. These studies are investigating new treatments and therapies."
        elif "diabetes" in question_lower:
            answer = f"Found {len(top_trials)} diabetes-related trials focusing on novel therapeutic approaches."
        elif "covid" in question_lower or "vaccine" in question_lower:
            answer = f"Found {len(top_trials)} COVID-19 and vaccine-related studies."
        else:
            answer = f"Found {len(top_trials)} relevant clinical trials based on your query."
        
        # Add trial IDs to response
        nct_ids = [trial["nct_id"] for trial in top_trials]
        answer += f"\n\nSources: {', '.join(nct_ids)}"
        
        return {
            "answer": answer,
            "sources": top_trials,
            "nct_ids": nct_ids
        }
