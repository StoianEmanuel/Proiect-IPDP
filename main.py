from flask import Flask, jsonify, request
import parts_controller
from db import create_tables

app = Flask(__name__)


@app.route("/parts", methods=["GET"])
def get_parts():
    parts = parts_controller.get_parts()
    return jsonify(parts)


"""metadata TEXT NOT NULL,                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code_producer TEXT,                name TEXT NOT NULL,                brand TEXT,
                series TEXT,                connections TEXT,                link_address TEXT,
                frequency REAL,                functions TEXT,                weight INTEGER,
				price REAL,				resolution TEXT"""
@app.route("/parts", methods=["POST"])
def insert_part():
    part_details = request.get_json()
    metadata = part_details["metadata"]
    code_producer = part_details["code_producer"]
    name = part_details["name"]
    brand = part_details["brand"]
    series = part_details["series"]
    connections = part_details["connections"]
    link_address = part_details["link_address"]
    frequency = part_details["frequency"]
    functions = part_details["functions"]
    weight = part_details["weight"]
    price = part_details["price"]
    resolution = part_details["resolution"]
    result = parts_controller.insert_part(metadata, code_producer, name, brand, series, connections, link_address,
                                          frequency, functions, weight, price, resolution)
    return jsonify(result)


@app.route("/parts", methods=["PUT"])
def update_part():
    part_details = request.get_json()
    metadata = part_details["metadata"]
    code_producer = part_details["code_producer"]
    name = part_details["name"]
    brand = part_details["brand"]
    series = part_details["series"]
    connections = part_details["connections"]
    link_address = part_details["link_address"]
    frequency = part_details["frequency"]
    functions = part_details["functions"]
    weight = part_details["weight"]
    price = part_details["price"]
    resolution = part_details["resolution"]
    id = part_details["id"]
    result = parts_controller.update_part(id, metadata, code_producer, name, brand, series, connections, link_address, frequency, functions, weight,
                price, resolution)
    return jsonify(result)


@app.route("/parts/<id>", methods=["DELETE"])
def delete_part(id):
    result = parts_controller.delete_part(id)
    return jsonify(result)


@app.route("/parts/<id>", methods=["GET"])
def get_part_by_id(id):
    part = parts_controller.get_by_id(id)
    return jsonify(part)


if __name__ == "__main__":
    create_tables()
    """
    Here you can change debug and port
    Remember that, in order to make this API functional, you must set debug in False
    """
    app.run(host='0.0.0.0', port=8000, debug=False)