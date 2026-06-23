// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract NetworkLogIntegrity {

    address public owner;
    bool public paused;

    mapping(address => bool) public writers;

    enum RecordType {
        ORIGINAL,
        CORRECTION,
        REVOCATION
    }

    struct LogRecord {
        bytes32 logHash;
        bytes32 source;
        uint256 timestamp;
        address submittedBy;
        RecordType recordType;
        uint256 relatedRecordId;
    }

    LogRecord[] private records;

    event LogStored(uint256 indexed recordId, bytes32 indexed logHash, bytes32 source, address submittedBy);
    event CorrectionStored(uint256 indexed recordId, uint256 indexed relatedRecordId, bytes32 indexed newHash);
    event RecordRevoked(uint256 indexed recordId, uint256 indexed relatedRecordId);
    event WriterSet(address indexed account, bool allowed);
    event Paused(bool status);

    constructor() {
        owner = msg.sender;
        writers[msg.sender] = true;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "OWNER_ONLY");
        _;
    }

    modifier onlyWriter() {
        require(writers[msg.sender], "WRITER_ONLY");
        _;
    }

    modifier whenNotPaused() {
        require(!paused, "PAUSED");
        _;
    }

    modifier recordExists(uint256 id) {
        require(id < records.length, "NOT_FOUND");
        _;
    }

    function setWriter(address account, bool allowed) external onlyOwner {
        writers[account] = allowed;
        emit WriterSet(account, allowed);
    }

    function setPaused(bool status) external onlyOwner {
        paused = status;
        emit Paused(status);
    }

    function storeLogHash(
        bytes32 logHash,
        bytes32 source
    ) external onlyWriter whenNotPaused {
        require(logHash != bytes32(0), "BAD_HASH");
        require(source != bytes32(0), "BAD_SOURCE");

        records.push(LogRecord({
            logHash: logHash,
            source: source,
            timestamp: block.timestamp,
            submittedBy: msg.sender,
            recordType: RecordType.ORIGINAL,
            relatedRecordId: type(uint256).max
        }));

        emit LogStored(records.length - 1, logHash, source, msg.sender);
    }

    function storeCorrection(
        uint256 originalRecordId,
        bytes32 newHash,
        bytes32 source
    ) external onlyWriter whenNotPaused recordExists(originalRecordId) {
        require(newHash != bytes32(0), "BAD_HASH");

        records.push(LogRecord({
            logHash: newHash,
            source: source,
            timestamp: block.timestamp,
            submittedBy: msg.sender,
            recordType: RecordType.CORRECTION,
            relatedRecordId: originalRecordId
        }));

        emit CorrectionStored(records.length - 1, originalRecordId, newHash);
    }

    function revokeRecord(
        uint256 originalRecordId
    ) external onlyWriter whenNotPaused recordExists(originalRecordId) {
        records.push(LogRecord({
            logHash: bytes32(0),
            source: bytes32("REVOCATION"),
            timestamp: block.timestamp,
            submittedBy: msg.sender,
            recordType: RecordType.REVOCATION,
            relatedRecordId: originalRecordId
        }));

        emit RecordRevoked(records.length - 1, originalRecordId);
    }

    function getRecord(uint256 recordId)
        external
        view
        recordExists(recordId)
        returns (
            bytes32 logHash,
            bytes32 source,
            uint256 timestamp,
            address submittedBy,
            RecordType recordType,
            uint256 relatedRecordId
        )
    {
        LogRecord memory r = records[recordId];
        return (
            r.logHash,
            r.source,
            r.timestamp,
            r.submittedBy,
            r.recordType,
            r.relatedRecordId
        );
    }

    function verifyLogHash(
        uint256 recordId,
        bytes32 hashToVerify
    ) external view recordExists(recordId) returns (bool) {
        return records[recordId].logHash == hashToVerify;
    }

    function getTotalRecords() external view returns (uint256) {
        return records.length;
    }
}