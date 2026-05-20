from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_rsa_key_pair(passphrase: str):
# GENERATE PRIVATE KEY
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # SERIALIZE AND SAVE PRIVATE KEY (ENCRYPTED)
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(passphrase.encode())
    )
    with open("snowflake_private_key.p8", "wb") as f:
        f.write(pem_private)

    # SERIALIZE AND SAVE PUBLIC KEY
    pem_public = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open("snowflake_public_key.pub", "wb") as f:
        f.write(pem_public)

if __name__ == "__main__":
    passphrase = "Cybersecurity123!"  # REPLACE WITH YOUR DESIRED PASSPHRASE
    generate_rsa_key_pair(passphrase)
