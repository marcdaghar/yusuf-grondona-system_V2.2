// SPDX-License-Identifier: CC BY-SA 4.0
pragma solidity ^0.8.0;

/**
 * @title ReputationToken – MREP (Muhtassib Reputation)
 * @author Marc Daghar
 * @notice Jeton de réputation NON-TRANSFÉRABLE pour les muhtassib
 * @dev Les muhtassib gagnent des points de réputation en effectuant
 *      des inspections de qualité. Ce jeton ne peut pas être échangé.
 *
 * Licence: CC BY-SA 4.0
 */

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

contract ReputationToken is ERC20, AccessControl {
    // ---- Rôles ----
    bytes32 public constant EMIR_ROLE = keccak256("EMIR_ROLE");
    bytes32 public constant MUHTASSIB_ROLE = keccak256("MUHTASSIB_ROLE");

    // ---- State ----
    mapping(address => uint256) public lastInspectionScore;
    mapping(address => uint256) public complaints;
    mapping(address => uint256) public inspectionsCount;

    uint256 public totalReputation = 0;

    // ---- Events ----
    event ReputationAwarded(
        address indexed muhtassib,
        uint256 amount,
        string reason
    );
    event InspectionRecorded(
        address indexed muhtassib,
        uint256 score,
        uint256 pointsAwarded
    );
    event ComplaintFiled(
        address indexed muhtassib,
        address indexed complainant,
        string reason
    );
    event ReputationBurned(
        address indexed muhtassib,
        uint256 amount,
        string reason
    );

    // ---- Constructor ----
    constructor() ERC20("Muhtassib Reputation", "MREP") {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(EMIR_ROLE, msg.sender);
    }

    // ---- Modifiers ----
    modifier onlyMuhtassib() {
        require(hasRole(MUHTASSIB_ROLE, msg.sender), "ReputationToken: not a muhtassib");
        _;
    }

    // ---- Gestion des rôles ----
    function registerMuhtassib(address muhtassib) external onlyRole(EMIR_ROLE) {
        _grantRole(MUHTASSIB_ROLE, muhtassib);
    }

    function revokeMuhtassib(address muhtassib) external onlyRole(EMIR_ROLE) {
        _revokeRole(MUHTASSIB_ROLE, muhtassib);
    }

    // ---- Attribution de réputation ----
    function awardReputation(address muhtassib, uint256 amount, string memory reason)
        external
        onlyRole(EMIR_ROLE)
    {
        require(muhtassib != address(0), "ReputationToken: invalid address");
        require(amount > 0, "ReputationToken: amount must be > 0");
        require(hasRole(MUHTASSIB_ROLE, muhtassib), "ReputationToken: not a muhtassib");

        _mint(muhtassib, amount);
        totalReputation += amount;

        emit ReputationAwarded(muhtassib, amount, reason);
    }

    // ---- Inspections ----
    function recordInspection(address muhtassib, uint256 score)
        external
        onlyRole(MUHTASSIB_ROLE)
    {
        require(muhtassib != address(0), "ReputationToken: invalid address");
        require(score <= 100, "ReputationToken: score must be <= 100");

        lastInspectionScore[muhtassib] = score;
        inspectionsCount[muhtassib]++;

        // Calcul des points gagnés
        uint256 points = 0;
        if (score >= 80) {
            points = 10;
        } else if (score >= 60) {
            points = 5;
        } else if (score >= 40) {
            points = 2;
        }

        if (points > 0) {
            _mint(muhtassib, points);
            totalReputation += points;
            emit InspectionRecorded(muhtassib, score, points);
        } else {
            emit InspectionRecorded(muhtassib, score, 0);
        }
    }

    // ---- Plaintes ----
    function fileComplaint(address muhtassib, string memory reason)
        external
        onlyMuhtassib
    {
        require(muhtassib != address(0), "ReputationToken: invalid address");
        require(muhtassib != msg.sender, "ReputationToken: cannot file against self");
        require(hasRole(MUHTASSIB_ROLE, muhtassib), "ReputationToken: not a muhtassib");

        complaints[muhtassib]++;

        // Pénalité : brûler 10% de la réputation si trop de plaintes
        if (complaints[muhtassib] > 3) {
            uint256 balance = balanceOf(muhtassib);
            uint256 penalty = balance / 10;
            if (penalty > 0) {
                _burn(muhtassib, penalty);
                totalReputation -= penalty;
                emit ReputationBurned(muhtassib, penalty, "Excessive complaints");
            }
        }

        emit ComplaintFiled(muhtassib, msg.sender, reason);
    }

    // ---- Transferts interdits ----
    function transfer(address, uint256) public pure override returns (bool) {
        revert("ReputationToken: non-transferable");
    }

    function transferFrom(address, address, uint256) public pure override returns (bool) {
        revert("ReputationToken: non-transferable");
    }

    function approve(address, uint256) public pure override returns (bool) {
        revert("ReputationToken: non-transferable");
    }

    function increaseAllowance(address, uint256) public pure override returns (bool) {
        revert("ReputationToken: non-transferable");
    }

    function decreaseAllowance(address, uint256) public pure override returns (bool) {
        revert("ReputationToken: non-transferable");
    }

    // ---- View functions ----
    function getMuhtassibStatus(address muhtassib)
        external
        view
        returns (
            uint256 reputation,
            uint256 lastScore,
            uint256 complaintsCount,
            uint256 inspectionsCountValue
        )
    {
        return (
            balanceOf(muhtassib),
            lastInspectionScore[muhtassib],
            complaints[muhtassib],
            inspectionsCount[muhtassib]
        );
    }

    function getTotalReputation() external view returns (uint256) {
        return totalReputation;
    }
}
