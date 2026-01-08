import argparse
import sys
from connection import Connection
from card import Card


def send_data(server_ip, server_port, data):
    """
    Send data to server in address (server_ip, server_port).
    """
    with Connection.connect(server_ip, server_port) as conn:
        conn.send(data)


def get_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    args: server_ip, server_port, card_name, card_creator, card_riddle, card_solution, card_image_path
    """
    parser = argparse.ArgumentParser(description="Send data to server.")
    parser.add_argument("server_ip", type=str, help="the server ip")
    parser.add_argument("server_port", type=int, help="the server port")
    parser.add_argument("card_name", type=str, help="the card name")
    parser.add_argument("card_creator", type=str, help="the card creator")
    parser.add_argument("card_riddle", type=str, help="the card riddle")
    parser.add_argument("card_solution", type=str, help="the card solution")
    parser.add_argument("card_image_path", type=str, help="the card image path")
    return parser.parse_args()


def main(args: argparse.Namespace) -> int:
    """
    Implementation of CLI and sending data to server.
    """
    try:
        card = Card.create_from_path(
            name=args.card_name,
            creator=args.card_creator,
            image_path=args.card_image_path,
            riddle=args.card_riddle,
            solution=args.card_solution,
        )
        card.image.encrypt(card.solution)
        print(f"Sending card: {card}")
        serilizied_card = card.serialize()
        send_data(args.server_ip, args.server_port, serilizied_card)
        print("Card sent successfully.")
        return 0
    except Exception as error:
        print(f"ERROR: {error}")
        return 1


if __name__ == "__main__":
    args = get_args()
    sys.exit(main(args))
