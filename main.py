import argparse

from src import tools
from src.agent import StoreAgent
from src.history import delete_history, load_history, save_history


def main():
    parser = argparse.ArgumentParser(description="Empório da Música virtual assistant")
    parser.add_argument("--session", default="default", help="conversation ID (e.g. customer phone)")
    parser.add_argument("--debug", action="store_true", help="show the tools called by the agent")
    args = parser.parse_args()

    tools.SHOW_CALLS = args.debug
    agent = StoreAgent(history=load_history(args.session))

    print("Empório da Música - Sua música começa aqui.")
    print("Comandos: /novo (reinicia a conversa)  /sair\n")

    while True:
        try:
            message = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not message:
            continue
        if message == "/sair":
            break
        if message == "/novo":
            delete_history(args.session)
            agent = StoreAgent()
            print("(conversa reiniciada)\n")
            continue

        try:
            answer = agent.reply(message)
        except Exception as error:
            print(f"[erro ao falar com o modelo: {error}]\n")
            continue

        print(f"\nLia: {answer}\n")
        save_history(args.session, agent.history())

    print("\nAté mais! 🎸")


if __name__ == "__main__":
    main()
