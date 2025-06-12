"""Entry point to start the local agentic bot."""

from src.agent import chat_loop


def main() -> None:
    """Run the interactive chat loop."""
    chat_loop()


if __name__ == "__main__":
    main()
