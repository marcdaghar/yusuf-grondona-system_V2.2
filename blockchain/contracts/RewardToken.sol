// SPDX-License-Identifier: CC BY-SA 4.0
pragma solidity ^0.8.0;

/**
 * @title RewardToken – YGR (Yusuf-Grondona Reward)
 * @author Marc Daghar
 * @notice Jeton de récompense pour le staking
 * @dev Émis en récompense pour le staking de YGDAO.
 *      Peut être brûlé pour des réductions ou des services.
 *
 * Licence: CC BY-SA 4.0
 */

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

contract RewardToken is ERC20, ERC20Burnable, AccessControl {
    // ---- Rôles ----
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant STAKING_CONTRACT_ROLE = keccak256("STAKING_CONTRACT_ROLE");
    bytes32 public constant EMIR_ROLE = keccak256("EMIR_ROLE");

    // ---- Events ----
    event RewardMinted(address indexed to, uint256 amount, string reason);
    event RewardBurned(address indexed from, uint256 amount, string reason);

    // ---- Constructor ----
    constructor() ERC20("Yusuf-Grondona Reward", "YGR") {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(EMIR_ROLE, msg.sender);
        _grantRole(MINTER_ROLE, msg.sender);
    }

    // ---- Minting ----
    function mint(address to, uint256 amount, string memory reason)
        external
        onlyRole(MINTER_ROLE)
    {
        require(to != address(0), "RewardToken: invalid address");
        require(amount > 0, "RewardToken: amount must be > 0");

        _mint(to, amount);
        emit RewardMinted(to, amount, reason);
    }

    function mintBatch(
        address[] memory to,
        uint256[] memory amounts,
        string memory reason
    ) external onlyRole(MINTER_ROLE) {
        require(to.length == amounts.length, "RewardToken: length mismatch");

        for (uint256 i = 0; i < to.length; i++) {
            require(to[i] != address(0), "RewardToken: invalid address");
            require(amounts[i] > 0, "RewardToken: amount must be > 0");

            _mint(to[i], amounts[i]);
            emit RewardMinted(to[i], amounts[i], reason);
        }
    }

    // ---- Burning from staking contract ----
    function burnFrom(address account, uint256 amount)
        public
        override
        onlyRole(STAKING_CONTRACT_ROLE)
    {
        require(account != address(0), "RewardToken: invalid address");
        require(amount > 0, "RewardToken: amount must be > 0");

        _burn(account, amount);
        emit RewardBurned(account, amount, "Staking contract burn");
    }

    // ---- Admin functions ----
    function addMinter(address minter) external onlyRole(EMIR_ROLE) {
        _grantRole(MINTER_ROLE, minter);
    }

    function removeMinter(address minter) external onlyRole(EMIR_ROLE) {
        _revokeRole(MINTER_ROLE, minter);
    }

    function addStakingContract(address stakingContract) external onlyRole(EMIR_ROLE) {
        _grantRole(STAKING_CONTRACT_ROLE, stakingContract);
    }

    function removeStakingContract(address stakingContract) external onlyRole(EMIR_ROLE) {
        _revokeRole(STAKING_CONTRACT_ROLE, stakingContract);
    }

    // ---- Overrides ----
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal override {
        super._beforeTokenTransfer(from, to, amount);
    }
}
