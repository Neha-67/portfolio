"""
QUAL-AI Agent - Direct execution script
"""
import asyncio
from agents import root_agent


async def main():
    """Main entry point for running the QUAL-AI agent."""
    print("🎯 QUAL-AI - Qualitative Research Analysis Agent")
    print("=" * 60)
    print(f"Agent: {root_agent.name}")
    print(f"Model: {root_agent.model.model}")
    print(f"Description: {root_agent.description}")
    print("=" * 60)
    print("\nAgent is ready to process qualitative data.")
    print("\nCapabilities:")
    print("  • Thematic analysis")
    print("  • Grounded theory approaches")
    print("  • Narrative analysis")
    print("  • Content analysis")
    print("  • Evidence-based insights")
    print("\nSupported data sources:")
    print("  • Interview transcripts")
    print("  • Survey responses")
    print("  • Focus group discussions")
    print("  • Field notes and observations")
    print("  • Social media conversations")
    print("  • Customer feedback")
    print("  • And more...")
    print("\n" + "=" * 60)
    print("Ready for analysis. Send your qualitative dataset to begin.")


if __name__ == "__main__":
    asyncio.run(main())
