# 加密：aes cbc pkcs7 key：7q9oko0vqb3la20r iv：31673371716468346a7662736b623978
import base64
from Crypto.Util.Padding import unpad
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

def encrypt_aes_cbc_pkcs7(message, key, iv):
    cipher = AES.new(key.encode(), AES.MODE_CBC, bytes.fromhex(iv))
    ciphertext = cipher.encrypt(pad(message.encode(), AES.block_size))
    return base64.b64encode(ciphertext).decode()

def decrypt_aes_cbc_pkcs7(encrypted_message, key, iv):
    cipher = AES.new(key.encode(), AES.MODE_CBC, bytes.fromhex(iv))
    decrypted_message = unpad(cipher.decrypt(base64.b64decode(encrypted_message)), AES.block_size)
    return decrypted_message.decode()


if __name__ == '__main__':
    key = '7q9oko0vqb3la20r'
    # 视频播放页面的key：azp53h0kft7qi78q
    #key = "azp53h0kft7qi78q"
    iv = '31673371716468346a7662736b623978'
    message = "9381843700"
    encrypted_message = encrypt_aes_cbc_pkcs7(message, key, iv)
    print(encrypted_message)
    while True:
        encrypted_message = input("输入加密后的信息：")
        decrypted_message = decrypt_aes_cbc_pkcs7(
            encrypted_message,
            key, iv)
        print(decrypted_message)