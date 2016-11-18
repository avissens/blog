# Test edit entry when user logged in
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

        entry = entries[0]
        self.assertEqual(entry.title, "Title edited")
        self.assertEqual(entry.content, "Content edited")
        self.assertEqual(entry.author, self.user)
  

    def test_signup_correct(self):
        self.browser.visit("http://127.0.0.1:8080/signup")
        self.browser.fill("name", "Bob")
        self.browser.fill("email", "bob@example.com")
        self.browser.fill("password", "thisisbobspassword")
        self.browser.fill("password_2", "thisisbobspassword")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/login")
        
    def test_signup_incorrect_password(self):
        self.browser.visit("http://127.0.0.1:8080/signup")
        self.browser.fill("name", "Bob")
        self.browser.fill("email", "bob@example.com")
        self.browser.fill("password", "thisisbobspassword")
        self.browser.fill("password_2", "thisisnotbobspassword")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/signup")

    def test_signup_incorrect_mail(self):
        self.browser.visit("http://127.0.0.1:8080/signup")
        self.browser.fill("name", "Bob")
        self.browser.fill("email", "alice@example.com")
        self.browser.fill("password", "thisisbobspassword")
        self.browser.fill("password_2", "thisisbobspassword")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/signup")
        
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
        self.assertEqual(user.password, generate_password_hash("thisisbobspassword"))