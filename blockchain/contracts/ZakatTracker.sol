// SPDX-License-Identifier: CC BY-SA 4.0
pragma solidity ^0.8.0;

/**
 * @title ZakatTracker – Traçabilité des transactions Zakat
 * @author Marc Daghar
 * @notice Enregistrement des paiements de Zakat
 * @dev La Zakat est payable UNIQUEMENT en nuqud (or/argent).
 *      Ce contrat assure la traçabilité des transactions.
 *
 * Licence: CC BY-SA 4.0
 */

import "@openzeppelin/contracts/access/AccessControl.sol";

contract ZakatTracker is AccessControl {
    // ---- Rôles ----
    bytes32 public constant EMIR_ROLE = keccak256("EMIR_ROLE");
    bytes32 public constant COLLECTOR_ROLE = keccak256("COLLECTOR_ROLE");

    // ---- Types ----
    enum ZakatCategory {
        FUQARA,          // Les pauvres
        MASAKIN,         // Les nécessiteux
        AMILIN,          // Collecteurs de Zakat
        MUALLAFATI,      // Nouveaux musulmans
        RIQAAB,          // Affranchissement
        GHARIMIN,        // Endettés
        FI_SABILILLAH,   // Cause d'Allah
        IBN_AL_SABIL     // Voyageurs
    }

    struct ZakatTransaction {
        uint256 id;
        address payer;
        address collector;
        uint256 amount; // en grammes d'équivalent or
        ZakatCategory category;
        uint256 timestamp;
        string receiptHash;
        bool distributed;
        address recipient;
        uint256 distributionTimestamp;
    }

    // ---- State ----
    ZakatTransaction[] public transactions;
    mapping(address => uint256[]) public userTransactions;
    mapping(ZakatCategory => uint256) public categoryTotals;

    uint256 public totalCollected = 0;
    uint256 public totalDistributed = 0;

    // ---- Events ----
    event ZakatCollected(
        uint256 indexed id,
        address indexed payer,
        uint256 amount,
        ZakatCategory category
    );
    event ZakatDistributed(
        uint256 indexed id,
        address indexed recipient,
        uint256 amount,
        ZakatCategory category
    );
    event ZakatRefunded(
        uint256 indexed id,
        address indexed payer,
        uint256 amount
    );

    // ---- Constructor ----
    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(EMIR_ROLE, msg.sender);
        _grantRole(COLLECTOR_ROLE, msg.sender);
    }

    // ---- Collecte de la Zakat ----
    function recordCollection(
        address payer,
        uint256 amount,
        ZakatCategory category,
        string memory receiptHash
    ) external onlyRole(COLLECTOR_ROLE) returns (uint256) {
        require(payer != address(0), "ZakatTracker: invalid payer");
        require(amount > 0, "ZakatTracker: amount must be > 0");
        require(bytes(receiptHash).length > 0, "ZakatTracker: receipt required");

        uint256 id = transactions.length;
        transactions.push(ZakatTransaction({
            id: id,
            payer: payer,
            collector: msg.sender,
            amount: amount,
            category: category,
            timestamp: block.timestamp,
            receiptHash: receiptHash,
            distributed: false,
            recipient: address(0),
            distributionTimestamp: 0
        }));

        userTransactions[payer].push(id);
        categoryTotals[category] += amount;
        totalCollected += amount;

        emit ZakatCollected(id, payer, amount, category);

        return id;
    }

    // ---- Distribution de la Zakat ----
    function markDistributed(
        uint256 id,
        address recipient,
        ZakatCategory category
    ) external onlyRole(EMIR_ROLE) {
        require(id < transactions.length, "ZakatTracker: invalid transaction");
        require(!transactions[id].distributed, "ZakatTracker: already distributed");
        require(recipient != address(0), "ZakatTracker: invalid recipient");

        ZakatTransaction storage tx = transactions[id];
        tx.distributed = true;
        tx.recipient = recipient;
        tx.distributionTimestamp = block.timestamp;

        totalDistributed += tx.amount;

        emit ZakatDistributed(id, recipient, tx.amount, category);
    }

    function distributeBulk(
        uint256[] memory ids,
        address[] memory recipients,
        ZakatCategory[] memory categories
    ) external onlyRole(EMIR_ROLE) {
        require(ids.length == recipients.length, "ZakatTracker: length mismatch");
        require(ids.length == categories.length, "ZakatTracker: length mismatch");

        for (uint256 i = 0; i < ids.length; i++) {
            markDistributed(ids[i], recipients[i], categories[i]);
        }
    }

    // ---- Refund ----
    function refundZakat(uint256 id) external onlyRole(EMIR_ROLE) {
        require(id < transactions.length, "ZakatTracker: invalid transaction");
        require(!transactions[id].distributed, "ZakatTracker: already distributed");

        address payer = transactions[id].payer;
        uint256 amount = transactions[id].amount;

        // Marquer comme distribuée à payer (refund)
        ZakatTransaction storage tx = transactions[id];
        tx.distributed = true;
        tx.recipient = payer;
        tx.distributionTimestamp = block.timestamp;

        emit ZakatRefunded(id, payer, amount);
    }

    // ---- View functions ----
    function getTransactionsByPayer(address payer)
        external
        view
        returns (ZakatTransaction[] memory)
    {
        uint256[] storage ids = userTransactions[payer];
        ZakatTransaction[] memory result = new ZakatTransaction[](ids.length);

        for (uint256 i = 0; i < ids.length; i++) {
            result[i] = transactions[ids[i]];
        }

        return result;
    }

    function getTransactionsByCategory(ZakatCategory category)
        external
        view
        returns (ZakatTransaction[] memory)
    {
        uint256 count = 0;
        for (uint256 i = 0; i < transactions.length; i++) {
            if (transactions[i].category == category) {
                count++;
            }
        }

        ZakatTransaction[] memory result = new ZakatTransaction[](count);
        uint256 index = 0;
        for (uint256 i = 0; i < transactions.length; i++) {
            if (transactions[i].category == category) {
                result[index] = transactions[i];
                index++;
            }
        }

        return result;
    }

    function getCategoryTotal(ZakatCategory category)
        external
        view
        returns (uint256)
    {
        return categoryTotals[category];
    }

    function getCategoryTotals()
        external
        view
        returns (
            uint256 fuqara,
            uint256 masakin,
            uint256 amilin,
            uint256 muallafati,
            uint256 riqaab,
            uint256 gharimin,
            uint256 fiSabilillah,
            uint256 ibnAlSabil
        )
    {
        return (
            categoryTotals[ZakatCategory.FUQARA],
            categoryTotals[ZakatCategory.MASAKIN],
            categoryTotals[ZakatCategory.AMILIN],
            categoryTotals[ZakatCategory.MUALLAFATI],
            categoryTotals[ZakatCategory.RIQAAB],
            categoryTotals[ZakatCategory.GHARIMIN],
            categoryTotals[ZakatCategory.FI_SABILILLAH],
            categoryTotals[ZakatCategory.IBN_AL_SABIL]
        );
    }

    function getStatistics()
        external
        view
        returns (
            uint256 total,
            uint256 collected,
            uint256 distributed,
            uint256 pending
        )
    {
        return (
            transactions.length,
            totalCollected,
            totalDistributed,
            totalCollected - totalDistributed
        );
    }
}
