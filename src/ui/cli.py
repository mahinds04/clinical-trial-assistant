import typer
from rich.console import Console
from rich.panel import Panel
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.rag.assistant import ClinicalTrialAssistant

app = typer.Typer()
console = Console()

@app.command()
def chat(
    model: str = typer.Option("llama2", help="Name of the Ollama model to use"),
    n_results: int = typer.Option(2, help="Number of relevant trials to consider")
):
    """Start an interactive chat session with the Clinical Trial Assistant."""
    console.print(Panel(
        "[bold green]Welcome to the Clinical Trial Assistant![/bold green]\n"
        "- Type your questions about clinical trials\n"
        "- Keep questions specific and focused for faster responses\n"
        "- Type 'exit' to quit",
        title="Clinical Trial Assistant"
    ))
    
    # Initialize assistant
    with console.status("Initializing assistant..."):
        assistant = ClinicalTrialAssistant(model_name=model)
    
    while True:
        question = typer.prompt("\n[bold blue]What would you like to know about clinical trials?[/bold blue]")
        
        if question.lower() == "exit":
            break
            
        with console.status("[bold yellow]Searching trials...[/bold yellow]") as status:
            try:
                response = assistant.query(question, n_results=n_results)
                status.update("[bold green]Generating response...[/bold green]")
                
                # Display the response in a neat panel
                console.print(Panel(
                    response["answer"],
                    title="[bold green]Response[/bold green]",
                    border_style="green"
                ))
                
                # Display relevant trials in a more compact format
                if response["sources"]:
                    console.print("\n[bold blue]Relevant Trials:[/bold blue]")
                    for i, source in enumerate(response["sources"], 1):
                        title = source.get('brief_title', 'Untitled')
                        phase = source.get('phase', 'Unknown Phase')
                        status = source.get('status', '')
                        console.print(f"{i}. [yellow]{title}[/yellow]")
                        console.print(f"   Phase: {phase} | Status: {status}")
                        
            except Exception as e:
                console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
                console.print("Please try rephrasing your question or try again in a moment.")

if __name__ == "__main__":
    app()
