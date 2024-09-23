import unittest
from app import app

class FlaskTestCase(unittest.TestCase):
    # アプリケーションが正しく起動するかをテスト
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get('/')
        self.assertEqual(response.status_code, 200)

    # 出勤の処理のテスト
    def test_clock_in(self):
        tester = app.test_client(self)
        response = tester.post('/clock-in', data=dict(user="TestUser"))
        self.assertEqual(response.status_code, 302)  # リダイレクトを確認

    # 退勤の処理のテスト
    def test_clock_out(self):
        tester = app.test_client(self)
        response = tester.post('/clock-out', data=dict(user="TestUser"))
        self.assertEqual(response.status_code, 302)  # リダイレクトを確認

    # Gmail通知のテスト
    def test_send_email(self):
        from routes import send_email
        try:
            send_email("テストメール", "これはunittestから送信されたテストメールです。")
            result = True
        except:
            result = False
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
