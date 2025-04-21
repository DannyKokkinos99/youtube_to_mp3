import unittest
import os
from app import app  # Import your Flask app
from dotenv import load_dotenv

load_dotenv()


class AppTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SECRET_KEY"] = os.getenv("FLASK_KEY")
        self.app = app.test_client()
        self.assertEqual(app.debug, False)

    def tearDown(self):
        pass

    def test_index_page_loads(self):
        response = self.app.get("/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_get_form_route_albums(self):
        response = self.app.get("/get-form?form=albums", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Artist", response.data)

    def test_get_form_route_playlists(self):
        response = self.app.get("/get-form?form=playlists", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Link", response.data)

    def test_get_form_route_song(self):
        response = self.app.get("/get-form?form=song", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Link", response.data)

    def test_get_form_route_default(self):
        response = self.app.get("/get-form?form=", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"form-container", response.data)


if __name__ == "__main__":
    unittest.main()
