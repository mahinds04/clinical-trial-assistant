import pandas as pd
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_demo_dataset(input_file: str, output_file: str, sample_size: int = 5000):
    """
    Create a smaller demo dataset from the full clinical trials data.
    Ensures a good distribution of different trial types and phases.
    """
    print(f"Reading full dataset from {input_file}")
    df = pd.read_csv(input_file)
    
    # Stratified sampling to maintain distribution of trial phases and conditions
    demo_df = df.copy()
    
    # Ensure we have a good mix of trial phases
    phases = demo_df['Phases'].unique()
    sample_per_phase = sample_size // len(phases)
    
    sampled_dfs = []
    for phase in phases:
        phase_df = demo_df[demo_df['Phases'] == phase]
        if len(phase_df) > sample_per_phase:
            sampled_phase = phase_df.sample(n=sample_per_phase, random_state=42)
        else:
            sampled_phase = phase_df
        sampled_dfs.append(sampled_phase)
    
    # Combine all sampled data
    demo_df = pd.concat(sampled_dfs)
    
    # If we haven't reached our sample size, add more random trials
    if len(demo_df) < sample_size:
        remaining = sample_size - len(demo_df)
        additional = df[~df.index.isin(demo_df.index)].sample(n=remaining, random_state=42)
        demo_df = pd.concat([demo_df, additional])
    
    # Save the demo dataset
    print(f"Saving demo dataset with {len(demo_df)} trials to {output_file}")
    demo_df.to_csv(output_file, index=False)
    
    return demo_df

if __name__ == "__main__":
    # Get project root directory
    root_dir = Path(__file__).parent.parent.parent
    
    # Set up paths
    input_file = root_dir / "data" / "clin_trials.csv"
    output_file = root_dir / "data" / "clin_trials_demo.csv"
    
    # Get sample size from environment variable or use default
    sample_size = int(os.getenv("DEMO_SAMPLE_SIZE", 5000))
    
    # Create demo dataset
    create_demo_dataset(input_file, output_file, sample_size)
