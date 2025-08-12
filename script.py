import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


def read_context(path: str) -> str:
    """Read the content of a text file."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def respond_to_message(user_message: str, context: str) -> str:
    """Send the user's message to OpenAI API along with the context."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": user_message},
        ],
        temperature=0.7,
        max_tokens=300,
    )
    return response["choices"][0]["message"]["content"].strip()


def main() -> None:
    context1 = read_context("archivo1.txt")
    context2 = read_context("archivo2.txt")
    context = context1 + "\n" + context2
    try:
        message = input("Escribe tu mensaje: ")
    except KeyboardInterrupt:
        print("\nInterrupción del usuario.")
        return
    response = respond_to_message(message, context)
    print("Respuesta de la IA:\n", response)


if __name__ == "__main__":
    main()
