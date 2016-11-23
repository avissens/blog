import os
import unittest
from urllib.parse import urlparse

from werkzeug.security import generate_password_hash

# Configure your app to use the testing configuration
if not "CONFIG_PATH" in os.environ:
    os.environ["CONFIG_PATH"] = "blog.config.TestingConfig"

from blog import app
from blog.database import Base, engine, session, User, Entry

class TestViews(unittest.TestCase):
    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create an example user
        self.user = User(name="Alice", email="alice@example.com",
                         password=generate_password_hash("test"))
        session.add(self.user)
        session.commit()
        
    def simulate_login(self):
        with self.client.session_transaction() as http_session:
            http_session["user_id"] = str(self.user.id)
            http_session["_fresh"] = True
            
# Test add entry when user logged in
    def test_add_entry(self):
        self.simulate_login()

        response = self.client.post("/entry/add", data={
            "title": "Test Entry",
            "content": "Test content"
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, "/")
        entries = session.query(Entry).all()
        self.assertEqual(len(entries), 1)

        entry = entries[0]
        self.assertEqual(entry.title, "Test Entry")
        self.assertEqual(entry.content, "Test content")
        self.assertEqual(entry.author, self.user)
        
# Test delete entry when user logged in
    def test_delete_entry(self):
        self.simulate_login()
        
        # Create an test entry
        test_entry = Entry(title="Test title", content="Testing editing entry", author=self.user)
        session.add(test_entry)
        session.commit()
        
        response = self.client.post("/entry/1/delete", data={
            "title": "Title edited",
            "content": "Content edited"
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, "/")
        entries = session.query(Entry).all()
        self.assertEqual(len(entries), 0)

# Test edit entry when user logged in
    def test_edit_entry(self):
        self.simulate_login()
        
        # Create an test entry
        test_entry = Entry(title="Test title", content="Testing editing entry", author=self.user)
        session.add(test_entry)
        session.commit()
        
        response = self.client.post("/entry/1/edit", data={
            "title": "Title edited",
            "content": "Content edited"
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, "/")
        entries = session.query(Entry).all()
        self.assertEqual(len(entries), 1)

        entry = entries[0]
        self.assertEqual(entry.title, "Title edited")
        self.assertEqual(entry.content, "Content edited")
        self.assertEqual(entry.author, self.user)

# Test signup a user
    def test_signup_user(self):

        response = self.client.post("/signup", data={
            "name": "Bob",
            "email": "bob@example.com",
            "password": "thisisbobspassword",
            "password_2": "thisisbobspassword",
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, "/login")
        users = session.query(User).all()
        self.assertEqual(len(users), 2)

        user = users[1]
        self.assertEqual(user.name, "Bob")
        self.assertEqual(user.email, "bob@example.com")
#        self.assertEqual(user.password, generate_password_hash("thisisbobspassword"))

    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)

if __name__ == "__main__":
    unittest.main()