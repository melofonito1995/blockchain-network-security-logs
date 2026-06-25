from web3 import Web3
import hashlib
import os
from pathlib import Path


# ============================================================
# 1. ΡΥΘΜΙΣΕΙΣ BLOCKCHAIN / SMART CONTRACT
# ============================================================

# RPC endpoint του Besu node.
# Μέσω αυτού το Python script επικοινωνεί με το blockchain.
RPC_URL = "https://rpc.dimikog.org/rpc/"

# Chain ID του συγκεκριμένου Besu network.
CHAIN_ID = 424242

# Διεύθυνση του ήδη deployed smart contract.
CONTRACT_ADDRESS = "0x3B23dAed4640F2FA7E2aCFaa62DF52073477f94E"

# Το αρχείο που περιέχει τα firewall logs.
LOG_FILE = "firewall_logs.txt"

# Το source που θα αποθηκευτεί στο smart contract.
# Στο contract είναι bytes32, άρα θα το μετατρέψουμε.
SOURCE_NAME = "FIREWALL"


# ============================================================
# 2. PRIVATE KEY
# ============================================================

# Παίρνουμε το private key από environment variable.
# Δεν το γράφουμε απευθείας στον κώδικα για λόγους ασφαλείας.
PRIVATE_KEY = os.getenv("FIREWALL_PRIVATE_KEY")

if not PRIVATE_KEY:
    raise ValueError("Missing FIREWALL_PRIVATE_KEY environment variable")

# Αν το private key δεν ξεκινά με 0x, το προσθέτουμε.
if not PRIVATE_KEY.startswith("0x"):
    PRIVATE_KEY = "0x" + PRIVATE_KEY


# ============================================================
# 3. ABI ΤΟΥ SMART CONTRACT
# ============================================================

# Το ABI λέει στο Python script ποιες functions έχει το contract.
# Εδώ χρειαζόμαστε μόνο τη storeLogHash(bytes32, bytes32).
ABI = [
    {
        "inputs": [
            {
                "internalType": "bytes32",
                "name": "logHash",
                "type": "bytes32"
            },
            {
                "internalType": "bytes32",
                "name": "source",
                "type": "bytes32"
            }
        ],
        "name": "storeLogHash",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]


# ============================================================
# 4. ΣΥΝΑΡΤΗΣΗ: ΥΠΟΛΟΓΙΣΜΟΣ SHA-256 HASH ΑΡΧΕΙΟΥ
# ============================================================

def sha256_file(filename: str) -> bytes:
    """
    Διαβάζει ένα αρχείο σε binary μορφή και επιστρέφει SHA-256 hash.

    Επιστρέφει bytes, δηλαδή ακριβώς αυτό που χρειάζεται το Solidity bytes32.
    """

    file_path = Path(filename)

    if not file_path.exists():
        raise FileNotFoundError(f"Log file not found: {filename}")

    sha256 = hashlib.sha256()

    # Διαβάζουμε το αρχείο σε chunks.
    # Αυτό είναι καλύτερο από το να διαβάζουμε όλο το αρχείο στη μνήμη.
    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(4096)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.digest()


# ============================================================
# 5. ΣΥΝΑΡΤΗΣΗ: STRING ΣΕ bytes32
# ============================================================

def to_bytes32(text: str) -> bytes:
    """
    Μετατρέπει ένα μικρό string σε bytes32.

    Παράδειγμα:
    FIREWALL -> b'FIREWALL\\x00\\x00...'
    """

    encoded = text.encode("utf-8")

    if len(encoded) > 32:
        raise ValueError("Text is too long for bytes32")

    return encoded.ljust(32, b"\x00")


# ============================================================
# 6. ΣΥΝΔΕΣΗ ΜΕ BESU BLOCKCHAIN
# ============================================================

w3 = Web3(Web3.HTTPProvider(RPC_URL))
print("Connected:", w3.is_connected())
print("RPC URL:", RPC_URL)
print("Chain ID from RPC:", w3.eth.chain_id)
print("Latest block from RPC:", w3.eth.block_number)

if not w3.is_connected():
    raise ConnectionError("Could not connect to Besu RPC endpoint")

print("Connected to Besu network")


# ============================================================
# 7. ΦΟΡΤΩΣΗ FIREWALL WALLET
# ============================================================

account = w3.eth.account.from_key(PRIVATE_KEY)
wallet_address = account.address

print(f"Firewall wallet address: {wallet_address}")


# ============================================================
# 8. ΣΥΝΔΕΣΗ ΜΕ ΤΟ SMART CONTRACT
# ============================================================

contract = w3.eth.contract(
    address=Web3.to_checksum_address(CONTRACT_ADDRESS),
    abi=ABI
)

print(f"Smart contract loaded: {CONTRACT_ADDRESS}")


# ============================================================
# 9. ΔΗΜΙΟΥΡΓΙΑ HASH ΤΩΝ FIREWALL LOGS
# ============================================================

log_hash = sha256_file(LOG_FILE)

print("SHA-256 log hash:")
print("0x" + log_hash.hex())


# ============================================================
# 10. ΜΕΤΑΤΡΟΠΗ SOURCE ΣΕ bytes32
# ============================================================

source = to_bytes32(SOURCE_NAME)

print("Source bytes32:")
print("0x" + source.hex())


# ============================================================
# 11. NONCE
# ============================================================

# Το nonce είναι ο αριθμός των transactions που έχει στείλει το wallet.
# Χρειάζεται για να υπογραφεί σωστά η νέα transaction.
nonce = w3.eth.get_transaction_count(wallet_address)

print(f"Nonce: {nonce}")


# ============================================================
# 12. ΔΗΜΙΟΥΡΓΙΑ TRANSACTION
# ============================================================

tx = contract.functions.storeLogHash(
    log_hash,
    source
).build_transaction({
    "from": wallet_address,
    "nonce": nonce,
    "gas": 300000,
    "maxFeePerGas": w3.to_wei("1", "gwei"),
    "maxPriorityFeePerGas": w3.to_wei("1", "gwei"),
    "chainId": CHAIN_ID
})


# ============================================================
# 13. ΥΠΟΓΡΑΦΗ TRANSACTION
# ============================================================

# Εδώ το firewall wallet υπογράφει το transaction.
# Αυτό αποδεικνύει ότι το συγκεκριμένο wallet έκανε την καταχώρηση.
signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)


# ============================================================
# 14. ΑΠΟΣΤΟΛΗ TRANSACTION ΣΤΟ BLOCKCHAIN
# ============================================================

tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

print("Transaction sent:")
print(w3.to_hex(tx_hash))


# ============================================================
# 15. ΑΝΑΜΟΝΗ ΓΙΑ CONFIRMATION
# ============================================================

print("Waiting for transaction receipt...")

receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print("Transaction confirmed")
print(f"Block number: {receipt.blockNumber}")
print(f"Gas used: {receipt.gasUsed}")
print(f"Status: {receipt.status}")

if receipt.status == 1:
    print("SUCCESS: Firewall log hash stored on-chain")
else:
    print("FAILED: Transaction reverted")
    print("Transaction confirmed")
print(f"Transaction hash: {w3.to_hex(tx_hash)}")
print(f"Explorer URL: https://blockexplorer.dimikog.org/tx/{w3.to_hex(tx_hash)}")
print(f"Block number: {receipt.blockNumber}")
print(f"Gas used: {receipt.gasUsed}")
print(f"Status: {receipt.status}")
