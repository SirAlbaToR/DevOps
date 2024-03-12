import unittest
from app import app, db  # Замени 'your_application_file' на реальное имя файла приложения

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_count_route(self):
        with app.app_context():
            response = self.app.get('/count')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'\xd0\xa4\xd0\xbe\xd1\x80\xd0\xbc\xd1\x8b \xd0\xbe\xd0\xb1\xd1\x83\xd1\x87\xd0\xb5\xd0\xbd\xd0\xb8\xd1\x8f', response.data)

    def test_students_route(self):
        with app.app_context():
            response = self.app.get('/students')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'\xd0\x98\xd0\xbd\xd1\x84\xd0\xbe\xd1\x80\xd0\xbc\xd0\xb0\xd1\x86\xd0\xb8\xd1\x8f \xd0\xbe \xd1\x81\xd1\x82\xd1\x83\xd0\xb4\xd0\xb5\xd0\xbd\xd1\x82\xd0\xb0\xd1\x85', response.data)

    def test_discs_route(self):
        with app.app_context():
            response = self.app.get('/discs')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'\xd0\xa3\xd1\x87\xd0\xb5\xd0\xb1\xd0\xbd\xd1\x8b\xd0\xb9 \xd0\xbf\xd0\xbb\xd0\xb0\xd0\xbd', response.data)

if __name__ == '__main__':
    unittest.main()

# запуск тестов: python test_app.py
# Установка unittest и Flask-Testing: pip install Flask-Testing