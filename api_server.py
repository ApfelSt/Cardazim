from __future__ import annotations
from flask import Flask, jsonify, request, send_file, Response, render_template
from card import Card
from saver import Saver
from card_driver import CardDriver
from os import PathLike, abort
import os
from typing import Union
from sql_driver import SQLDriver
from crypt_image import CryptImage
from PIL import Image

ERROR_MSG = {"message": "404 not found :()"}


def create_app(saver: Saver) -> Flask:
    app = Flask(__name__)

    def get_creator_cards(
        creator: str, solved: bool = True, all: bool = True
    ) -> Response:
        """return str(card) for each card of the creator that satisfies solved, or all of them if all is True"""
        cards = saver.get_creator_cards(creator, solved, all)
        cards_str = [str(card) for card in cards]
        return jsonify(cards_str)

    @app.route("/creators", methods=["GET"])
    def get_creators() -> Response:
        creators = saver.get_creators()
        return jsonify(creators)

    @app.route("/creators/<creator>/cards", methods=["GET"])
    def get_all_cards(creator: str) -> Response:
        return get_creator_cards(creator)

    @app.route("/creators/<creator>/cards/solved", methods=["GET"])
    def get_solved_cards(creator: str) -> Response:
        return get_creator_cards(creator, solved=True, all=False)

    @app.route("/creators/<creator>/cards/unsolved", methods=["GET"])
    def get_unsolved_cards(creator: str) -> Response:
        return get_creator_cards(creator, solved=False, all=False)

    @app.route("/creators/<creator>/cards/<name>", methods=["GET"])
    def get_card(creator: str, name: str) -> Union[str, Response]:
        """load the card from the DB"""
        card = saver.load(name, creator)
        return render_template("card.html", card=card) if card else jsonify(ERROR_MSG)

    @app.route("/creators/<creator>/cards/<name>/image.png", methods=["GET"])
    def get_card_image(creator: str, name: str) -> Response:
        """get the image of the card"""
        img_path = saver.get_image_path(name, creator)
        return (
            send_file(img_path)
            if img_path and os.path.exists(img_path)
            else jsonify(ERROR_MSG)
        )

    @app.route("/cards/find", methods=["GET"])
    def find_cards() -> Union[Response, str]:
        """find cards by query parameters"""
        query_params = request.args.to_dict()
        cards = saver.find_cards(**query_params)
        cards_str = [str(card) for card in cards]
        return render_template("find_cards.html", cards=cards)

    @app.route("/creators/<creator>/cards/<name>/solve", methods=["GET", "POST"])
    def solve_card(creator: str, name: str) -> Union[Response, str]:
        """solve the card with the given identifier using the provided key"""
        card = saver.load(name, creator)
        if not card:
            return jsonify(ERROR_MSG)
        if card.solution:
            return render_template("solve_card.html", card=card, solved=True)
        check_solution = False
        if request.method == "POST":
            solution = request.form.get("solution")
            if not solution:
                return render_template("solve_card.html", card=card, solved=False)
            check_solution = saver.solve_card(name, creator, solution)

        return render_template("solve_card.html", card=card, solved=check_solution)

    @app.route("/", methods=["GET"])
    def home() -> str:
        return render_template("home.html")

    @app.route("/cards/create", methods=["GET", "POST"])
    def create_card() -> Union[Response, str]:
        """create a new card with the provided data and image"""
        if request.method == "POST":
            name = request.form.get("name")
            creator = request.form.get("creator")
            riddle = request.form.get("riddle")
            solution = request.form.get("solution")
            image = request.files.get("image")

            if not all([name, creator, riddle, solution, image]):
                return render_template(
                    "create_card.html", error="All fields are required."
                )

            # save the image to a temporary location and encrypt it
            os.makedirs("temp_images", exist_ok=True)
            temp_image_path = os.path.join("temp_images", image.filename)
            image.save(temp_image_path)
            # show the image for debugging
            crypt_img = CryptImage.create_from_path(temp_image_path)
            crypt_img.encrypt(solution)
            # show the encrypted image for debugging
            card = Card(
                name=name,
                creator=creator,
                riddle=riddle,
                solution=None,
                image=crypt_img,
            )
            saver.save(card)
            # remove the temporary image file
            os.remove(temp_image_path)

            return render_template(
                "create_card.html", success="Card created successfully!"
            )

        return render_template("create_card.html")

    return app


if __name__ == "__main__":
    driver = SQLDriver()
    image_dir: Union[str, PathLike] = "./images"
    saver = Saver(driver, image_dir)
    saver.init_db()
    app = create_app(saver)
    app.run(host="127.0.0.1", port=5000)
