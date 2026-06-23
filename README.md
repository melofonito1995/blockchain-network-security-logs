Blockchain Firewall Log Integrity
Overview

This project demonstrates how blockchain technology can be used to ensure the integrity of firewall security logs. Instead of storing the actual logs on-chain, the system stores only the SHA-256 hash of the log file in a smart contract deployed on a Hyperledger Besu blockchain network.

The solution provides an immutable and tamper-evident audit trail for firewall logs while preserving privacy and minimizing blockchain storage requirements.

Architecture
Firewall Logs
      ↓
Python Collector Agent
      ↓
SHA-256 Hash Generation
      ↓
Smart Contract (Solidity)
      ↓
Hyperledger Besu Blockchain
      ↓
Integrity Verification
Components
Smart Contract

NetworkLogIntegrity.sol

The smart contract is responsible for:

Storing log hashes on-chain
Managing authorized writers
Recording timestamps
Maintaining immutable audit records
Verifying stored hashes
Python Collector

Securitylogs.py

The Python script:

Reads firewall log files
Generates SHA-256 hashes
Connects to the Besu RPC endpoint
Signs transactions using the firewall wallet
Calls the smart contract function storeLogHash()
Technologies Used
Hyperledger Besu
Solidity
Python 3
Web3.py
SHA-256
Remix IDE
MetaMask
Security Considerations
Actual firewall logs remain off-chain.
Only cryptographic hashes are stored on-chain.
Private keys must be securely protected.
Blockchain ensures integrity but does not guarantee log authenticity.
Future Improvements
Batch processing of log files
Automated Syslog integration
SIEM integration (Wazuh / Splunk)
Merkle Tree verification
Multi-firewall support
Authors

Smart contract: 0x3B23dAed4640F2FA7E2aCFaa62DF52073477f94E  

<img width="1672" height="941" alt="transaction details" src="https://github.com/user-attachments/assets/d6aff8e2-8493-4be0-be1a-54ff4460f143" />


The sample firewall logs are provided as an encrypted 7z archive for privacy reasons.

Xenofon Batsis 
Dionysia Kavallieratou

MSc Cybersecurity
University of West Attica
<img width="600" height="400" alt="image" src="https://github.com/user-attachments/assets/42b24b05-d63b-4151-8421-8c3173ef8252" />

