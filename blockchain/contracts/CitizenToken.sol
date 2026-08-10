// SPDX-License-Identifier: CC BY-SA 4.0
pragma solidity ^0.8.0;

/**
 * @title CitizenToken – CPT (Citizen Participation Token)
 * @author Marc Daghar
 * @notice Jeton de participation citoyenne (Social Credit)
 * @dev Les citoyens gagnent des CPT en participant à la vie économique
 *      et sociale. Les CPT permettent des réductions, des votes locaux,
 *      et l'accès à des services.
 *
 * Licence: CC BY-SA 4.0
 */

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

contract CitizenToken is ERC20, ERC20Burnable, AccessControl {
    // ---- Rôles ----
    bytes32 public constant EMIR_ROLE = keccak256("EMIR_ROLE");
    bytes32 public constant MERCHANT_ROLE = keccak256("MERCHANT_ROLE");
    bytes32 public constant CITIZEN_ROLE = keccak256("CITIZEN_ROLE");

    // ---- State ----
    mapping(address => uint256) public citizenshipScore;
    mapping(address => uint256) public lastRewardDate;
    mapping(address => uint256) public totalEarned;
    mapping(address => uint256) public totalSpent;
    mapping(uint256 => uint256) public proposalVotes;

    uint256 public totalCitizens = 0;
    uint256 public totalCPTInCirculation = 0;

    // ---- Events ----
    event CitizenRewarded(
        address indexed citizen,
        uint256 amount,
        string reason
    );
    event MerchantRewarded(
        address indexed merchant,
        uint256 amount
    );
    event DiscountUsed(
        address indexed citizen,
        uint256 amount,
        uint256 discountPercent
    );
    event VoteCast(
        address indexed citizen,
        uint256 proposalId,
        bool support,
        uint256 weight
    );

    // ---- Constructor ----
    constructor() ERC20("Citizen Participation Token", "CPT") {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(EMIR_ROLE, msg.sender);
    }

    // ---- Modifiers ----
    modifier onlyCitizen() {
        require(hasRole(CITIZEN_ROLE, msg.sender), "CitizenToken: not a citizen");
        _;
    }

    // ---- Gestion des citoyens ----
    function registerCitizen(address citizen) external onlyRole(EMIR_ROLE) {
        _grantRole(CITIZEN_ROLE, citizen);
        totalCitizens++;
    }

    function revokeCitizen(address citizen) external onlyRole(EMIR_ROLE) {
        _revokeRole(CITIZEN_ROLE, citizen);
        totalCitizens--;
    }

    // ---- Récompenses ----
    function rewardCitizen(address citizen, uint256 amount, string memory reason)
        external
        onlyRole(EMIR_ROLE)
    {
        require(citizen != address(0), "CitizenToken: invalid address");
        require(amount > 0, "CitizenToken: amount must be > 0");
        require(hasRole(CITIZEN_ROLE, citizen), "CitizenToken: not a citizen");

        _mint(citizen, amount);
        lastRewardDate[citizen] = block.timestamp;
        totalEarned[citizen] += amount;
        totalCPTInCirculation += amount;

        emit CitizenRewarded(citizen, amount, reason);
    }

    function rewardMerchant(address merchant, uint256 amount)
        external
        onlyRole(MERCHANT_ROLE)
    {
        require(merchant != address(0), "CitizenToken: invalid address");
        require(amount > 0, "CitizenToken: amount must be > 0");

        _mint(merchant, amount);
        totalEarned[merchant] += amount;
        totalCPTInCirculation += amount;

        emit MerchantRewarded(merchant, amount);
    }

    // ---- Utilisation ----
    function useDiscount(uint256 amount) external onlyCitizen {
        require(amount > 0, "CitizenToken: amount must be > 0");
        require(balanceOf(msg.sender) >= amount, "CitizenToken: insufficient balance");

        _burn(msg.sender, amount);
        totalSpent[msg.sender] += amount;
        totalCPTInCirculation -= amount;

        // Calcul du pourcentage de réduction (1 CPT = 1% de réduction, max 20%)
        uint256 discountPercent = amount > 20 ? 20 : amount;

        emit DiscountUsed(msg.sender, amount, discountPercent);
    }

    // ---- Vote local ----
    function voteOnProposal(uint256 proposalId, bool support)
        external
        onlyCitizen
    {
        uint256 weight = balanceOf(msg.sender);
        require(weight > 0, "CitizenToken: no voting power");

        // Enregistrement du vote (simplifié)
        if (support) {
            proposalVotes[proposalId] += weight;
        } else {
            proposalVotes[proposalId] -= weight;
        }

        emit VoteCast(msg.sender, proposalId, support, weight);
    }

    // ---- View functions ----
    function getCitizenStatus(address citizen)
        external
        view
        returns (
            bool isCitizen,
            uint256 balance,
            uint256 earned,
            uint256 spent,
            uint256 lastReward
        )
    {
        return (
            hasRole(CITIZEN_ROLE, citizen),
            balanceOf(citizen),
            totalEarned[citizen],
            totalSpent[citizen],
            lastRewardDate[citizen]
        );
    }

    function getProposalVotes(uint256 proposalId)
        external
        view
        returns (uint256)
    {
        uint256 votes = proposalVotes[proposalId];
        if (votes > 0) {
            return votes;
        } else {
            return 0;
        }
    }

    function getProposalResult(uint256 proposalId)
        external
        view
        returns (bool passed, uint256 forVotes, uint256 againstVotes)
    {
        uint256 votes = proposalVotes[proposalId];
        if (votes > 0) {
            return (true, votes, 0);
        } else if (votes < 0) {
            return (false, 0, uint256(-votes));
        } else {
            return (false, 0, 0);
        }
    }

    function getTotalCirculation() external view returns (uint256) {
        return totalCPTInCirculation;
    }

    // ---- Admin ----
    function addMerchant(address merchant) external onlyRole(EMIR_ROLE) {
        _grantRole(MERCHANT_ROLE, merchant);
    }

    function removeMerchant(address merchant) external onlyRole(EMIR_ROLE) {
        _revokeRole(MERCHANT_ROLE, merchant);
    }

    // ---- Overrides ----
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal override {
        super._beforeTokenTransfer(from, to, amount);
        // Les CPT peuvent être transférés librement entre citoyens
    }
}
