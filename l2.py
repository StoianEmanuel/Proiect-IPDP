from flask import Flask, request, jsonify

app = Flask(__name__)

books = [
    {
        "id": 1,
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald"
    },
    {
        "id": 2,
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee"
    }
]

books_ = books


# Define the JSON-LD context for the books endpoint
books_context = {
    "@context": {"@schema": "sqlite"},
    "@type": "products",
}

# GET /books
@app.route('/books', methods=['GET'])
def get_books():
    return jsonify(books_context, books)

# GET /books/<int:id>
@app.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    book = next((book for book in books if book['id'] == id), None)
    if book is None:
        return jsonify(books_context, {'error': 'Book not found'}), 404
    return jsonify(books_context, book)

# POST /books
@app.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    if data is None or 'title' not in data or 'author' not in data:
        return jsonify(books_context, {'error': 'Invalid book data'}), 400
    book = {
        'id': len(books) + 1,
        'title': data['title'],
        'author': data['author']
    }
    books.append(book)
    return jsonify(books_context, {'message': 'Book created successfully', 'book': book})

# PUT /books/<int:id>
@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    data = request.get_json()
    book = next((book for book in books if book['id'] == id), None)
    if book is None:
        return jsonify(books_context, {'error': 'Book not found'}), 404
    if data is not None:
        if 'title' in data:
            book['title'] = data['title']
        if 'author' in data:
            book['author'] = data['author']
    return jsonify(books_context, {'message': 'Book updated successfully'})

# DELETE /books/<int:id>
@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = next((book for book in books if book['id'] == id), None)
    if book is None:
        return jsonify(books_context, {'error': 'Book not found'}), 404
    books.remove(book)
    return jsonify(books_context, {'message': 'Book deleted successfully'})

if __name__ == '__main__':
    app.run(port=3000,debug=False)