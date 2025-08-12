from core import flow


def main() -> None:
    channel_id = "cli"
    while True:
        try:
            message = input("Escribe tu mensaje: ")
        except KeyboardInterrupt:
            print("\nInterrupción del usuario.")
            break

        responses = flow.on_incoming_message(channel_id, message)
        for resp in responses:
            print(resp)


if __name__ == "__main__":
    main()
