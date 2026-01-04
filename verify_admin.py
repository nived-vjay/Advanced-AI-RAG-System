import os
import io
import unittest
from admin_app import app, UPLOAD_FOLDER

class FlaskAdminTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        # Create a dummy file in data folder for listing test
        with open(os.path.join(UPLOAD_FOLDER, 'test_existing.txt'), 'w') as f:
            f.write('content')

    def tearDown(self):
        # Cleanup
        if os.path.exists(os.path.join(UPLOAD_FOLDER, 'test_existing.txt')):
            os.remove(os.path.join(UPLOAD_FOLDER, 'test_existing.txt'))
        if os.path.exists(os.path.join(UPLOAD_FOLDER, 'test_upload.txt')):
            os.remove(os.path.join(UPLOAD_FOLDER, 'test_upload.txt'))

    def test_index_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'test_existing.txt', response.data)

    def test_upload_route(self):
        data = {
            'file': (io.BytesIO(b"test content"), 'test_upload.txt')
        }
        response = self.app.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'File uploaded successfully', response.data)
        self.assertTrue(os.path.exists(os.path.join(UPLOAD_FOLDER, 'test_upload.txt')))

if __name__ == '__main__':
    unittest.main()
