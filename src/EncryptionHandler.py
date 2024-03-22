from cryptography.fernet import Fernet

class EncryptionHandler:
    key = b'W57u_9geKwq5CrgZWYUnf23z_1s8SEsy7kKJ7IOCxxQ='

    @staticmethod
    def encrypt(data):
        try:
            cipher = Fernet(EncryptionHandler.key)
            encrypted_data = cipher.encrypt(data)
            return encrypted_data
        except Exception as e:
            print(f"ENCRYPT ERROR : {e}")
            return None

    @staticmethod
    def decrypt(encrypted_data):
        try:
            cipher = Fernet(EncryptionHandler.key)
            decrypted_data = cipher.decrypt(bytes(encrypted_data))
            return decrypted_data
        except Exception as e:
            print(f"DECRYPT ERROR: {e}")
            return None
