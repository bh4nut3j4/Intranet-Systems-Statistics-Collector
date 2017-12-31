import unittest
from ClientScript import encrypt_jsondata
from ServerScript import decrypt_data


class EncryptionTest(unittest.TestCase):


    def test_checkEncryption(self):
        stringdata = "HelloWorld_TestString"
        data = encrypt_jsondata(stringdata)
        decrypted_data = decrypt_data(data)
        self.assertEqual(stringdata, decrypted_data)

unittest.main()

