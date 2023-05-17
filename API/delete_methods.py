import sqlite3
from flask import jsonify, request


# Delete item from database with id argument 
def delete_item_by_id(db_path = "./Data/gaming.sqlite"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    data_type = request.args.get("data_type")
    item_id = request.args.get("id")
    valid_data_types = ["mice", "video_games", "consoles"]

    # Check if data_type is valid
    if data_type not in valid_data_types:
        error_response = {"error": "Invalid data type"}
        return jsonify(error_response), 400

    if not item_id:
        error_response = {"error": "Missing id argument"}
        return jsonify(error_response), 400

    # Delete item with specific ID
    if data_type == "video_games":
        c.execute("DELETE FROM VideoGames WHERE id = ?", (item_id,))
        conn.commit()
        c.close()
        conn.close()
        return jsonify({'message': f'Deleted video game with id {item_id}'}), 200

    elif data_type == "consoles":
        c.execute("DELETE FROM Consoles WHERE id = ?", (item_id,))
        conn.commit()
        c.close()
        conn.close()
        return jsonify({'message': f'Deleted console with id {item_id}'}), 200

    elif data_type == "mice":
        c.execute("DELETE FROM Mice WHERE id = ?", (item_id,))
        conn.commit()
        c.close()
        conn.close()
        return jsonify({'message': f'Deleted mice with id {item_id}'}), 200

    c.close()
    conn.close()
    error_response = {"error": "Invalid data type"}
    return jsonify(error_response), 400


# Delete item from database with model and manufacturer arguments 
def delete_item_by_model_and_manufacturer(db_path = "./Data/gaming.sqlite"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    data_type = request.args.get("data_type")
    model = request.args.get("model")
    manufacturer = request.args.get("manufacturer")
    valid_data_types = ["CPU", "GPU"]

    # Check if data_type is valid
    if data_type not in valid_data_types:
        error_response = {"error": "Invalid data type"}
        return jsonify(error_response), 400

    if not model or not manufacturer:
        error_response = {"error": "Missing model or manufacturer"}
        return jsonify(error_response), 400

    # Delete item with specific model and manufacturer
    if data_type == "CPU":
        c.execute("DELETE FROM CPU WHERE model = ? AND manufacturer = ?", (model, manufacturer))
        conn.commit()
        return jsonify({'message': f'Deleted CPU with model {model} and manufacturer {manufacturer}'}), 200

    elif data_type == "GPU":
        c.execute("DELETE FROM GPU WHERE model = ? AND manufacturer = ?", (model, manufacturer))
        conn.commit()
        return jsonify({'message': f'Deleted GPU with model {model} and manufacturer {manufacturer}'}), 200

    else:
        error_response = {"error": "Invalid data type"}
        return jsonify(error_response), 400