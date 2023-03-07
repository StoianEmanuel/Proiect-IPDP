from flask import Flask, request, jsonify
import sqlite3, json
from json import dumps

app = Flask(__name__)

app.config['SQLITE_DB_DIR'] = 'C:/Users/manue/Desktop/Proiect IPDP/'
app.config['SQLITE_DB_NAME'] = 'books.db'

# Retrieve all books from the database
def get_all_books():
    conn = sqlite3.connect(f"{app.config['SQLITE_DB_DIR']}/{app.config['SQLITE_DB_NAME']}")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()
    books = []
    for row in rows:
        book = {
            'id': row[0],
            'title': row[1],
            'author': row[2],
            'isbn': row[3]
        }
        books.append(book)
    conn.close()
    return books

# Function to establish connection with the database
def get_db_connection():
    conn = sqlite3.connect('books.db')
    conn.row_factory = sqlite3.Row
    return conn

# Define the route to retrieve all books
@app.route('/books', methods=['GET'])
def get_books():
    # Retrieve all books
    books = get_all_books()

    # Create JSON-LD document
    context = {
        "@schema": "sqlite"
    }
    data = {
        "@context": context,
        "@type": "books",
        "@list": books
    }
    json_ld_doc = json.dumps(data)

    # Return response in JSON-LD format
    response = app.response_class(
        response=json_ld_doc,
        status=200,
        mimetype='application/ld+json'
    )
    return response

# Retrieve a book from the database by id
def get_book_by_id(id):
    conn = sqlite3.connect(f"{app.config['SQLITE_DB_DIR']}/{app.config['SQLITE_DB_NAME']}")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books WHERE id=?", (id,))
    row = cursor.fetchone()
    if row:
        book = {
            '@id': row[0],
            'title': row[1],
            'author': row[2],
            'isbn': row[3]
        }
    else:
        book = None
    conn.close()
    return book

# Define the route to retrieve book by id
@app.route('/books/get_data', methods=['GET'])
def get_book_data():
    # Check if the id is provided in the query string
    id = request.args.get('id')
    if id is None:
        # Return error response if id is not provided
        error_response = {
            'error': 'id parameter is missing'
        }
        return jsonify(error_response), 400

    # Retrieve book by id
    book = get_book_by_id(id)

    if book is None:
        # Return error response if book is not found
        error_response = {
            'error': 'Book not found'
        }
        return jsonify(error_response), 404

    # Create JSON-LD document
    context = {
        "@schema": "sqlite"
    }
    data = {
        "@context": context,
        "@type": "books",
        "@list": [book]
    }
    json_ld_doc = json.dumps(data)

    # Return response in JSON-LD format
    response = app.response_class(
        response=json_ld_doc,
        status=200,
        mimetype='application/ld+json'
    )
    return response


# Function to add a new book
@app.route('/books', methods=['POST'])
def add_book():
    conn = get_db_connection()
    book_data = request.json
    book = (book_data['title'], book_data['author'], book_data['isbn'])
    conn.execute('INSERT INTO books (title, author, isbn) VALUES (?, ?, ?)', book)
    conn.commit()
    conn.close()
    return jsonify({'message': 'Book added successfully'}), 201

# Function to update a book
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    conn = get_db_connection()
    book_data = request.json
    book = (book_data['title'], book_data['author'], book_data['isbn'], book_id)
    conn.execute('UPDATE books SET title = ?, author = ?, isbn = ? WHERE id = ?', book)
    conn.commit()
    conn.close()
    return jsonify({'message': 'Book updated successfully'})

# Function to delete a book
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Book deleted successfully'})

if __name__ == '__main__':
    app.run(port=8000)
