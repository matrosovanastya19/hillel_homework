from flask import Flask
from flask import render_template

app = Flask(__name__)

classic_books = [
    {"title": "Гордість і упередження", "author": "Джейн Остін", "year": 1813},
    {"title": "Джейн Ейр", "author": "Шарлотта Бронте", "year": 1847},
    {"title": "Собор Паризької богоматері", "author":"Віктор Гюго", "year": 1831 },
    {"title":"Айвенго", "author":"Вальтер Скотт", "year":1819},
    {"title": "Енн із Зелених Мезонінів", "author": "Люсі Мод Монтгомері", "year": 1908},
    {"title": "Ніч у Лісабоні", "author": "Еріх Марія Ремарк", "year": 1962},
    {"title": "Агнес Грей", "author": "Енн Бронте", "year": 1847}
]

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/books')
def books():
    return render_template('books.html', books_list=classic_books)
@app.route('/about')
def about():
    return render_template('about.html')
if __name__ == '__main__':
    app.run(debug=True)
