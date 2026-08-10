// SPDX-License-Identifier: CC BY-SA 4.0
pragma solidity ^0.8.0;

/**
 * @title DAO Governance – Yusuf-Grondona System
 * @author Marc Daghar
 * @notice Contrat de gouvernance DAO pour le système monétaire Yusuf-Grondona
 * @dev Utilise OpenZeppelin Governor + Timelock
 *
 * Le DAO permet aux détenteurs de jetons YGDAO de :
 * - Proposer des changements de politique monétaire
 * - Voter sur les propositions
 * - Exécuter les décisions adoptées
 *
 * Licence: CC BY-SA 4.0
 */

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Votes.sol";
import "@openzeppelin/contracts/governance/Governor.sol";
import "@openzeppelin/contracts/governance/extensions/GovernorVotes.sol";
import "@openzeppelin/contracts/governance/extensions/GovernorVotesQuorumFraction.sol";
import "@openzeppelin/contracts/governance/extensions/GovernorTimelockControl.sol";
import "@openzeppelin/contracts/governance/extensions/GovernorCountingSimple.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";

// ============================================================================
// JETON DE GOUVERNANCE (YGDAO)
// ============================================================================

/**
 * @title YGDAO Token
 * @notice Jeton de gouvernance du système Yusuf-Grondona
 * @dev ERC20 avec votes et permit
 */
contract YGDAO is ERC20, ERC20Permit, ERC20Votes {
    uint256 public constant INITIAL_SUPPLY = 1_000_000 * 10**18; // 1 million de tokens

    constructor()
        ERC20("Yusuf-Grondona DAO", "YGDAO")
        ERC20Permit("Yusuf-Grondona DAO")
    {
        _mint(msg.sender, INITIAL_SUPPLY);
    }

    // Les fonctions ci-dessous sont requises par ERC20Votes
    function _afterTokenTransfer(address from, address to, uint256 amount)
        internal
        override(ERC20, ERC20Votes)
    {
        super._afterTokenTransfer(from, to, amount);
    }

    function _mint(address to, uint256 amount)
        internal
        override(ERC20, ERC20Votes)
    {
        super._mint(to, amount);
    }

    function _burn(address account, uint256 amount)
        internal
        override(ERC20, ERC20Votes)
    {
        super._burn(account, amount);
    }
}

// ============================================================================
// TIMELOCK CONTROLLER
// ============================================================================

import "@openzeppelin/contracts/governance/TimelockController.sol";

// ============================================================================
// GOUVERNEUR
// ============================================================================

/**
 * @title YGGovernor
 * @notice Gouverneur du système Yusuf-Grondona
 * @dev Hérite de Governor avec votes et timelock
 */
contract YGGovernor is
    Governor,
    GovernorVotes,
    GovernorVotesQuorumFraction,
    GovernorTimelockControl,
    GovernorCountingSimple
{
    uint256 public constant VOTING_DELAY = 1; // 1 bloc
    uint256 public constant VOTING_PERIOD = 5; // 5 blocs
    uint256 public constant PROPOSAL_THRESHOLD = 1000 * 10**18; // 1000 YGDAO

    constructor(IVotes _token, TimelockController _timelock)
        Governor("YGGovernor")
        GovernorVotes(_token)
        GovernorVotesQuorumFraction(4) // 4% de quorum
        GovernorTimelockControl(_timelock)
    {}

    function votingDelay() public pure override returns (uint256) {
        return VOTING_DELAY;
    }

    function votingPeriod() public pure override returns (uint256) {
        return VOTING_PERIOD;
    }

    function proposalThreshold() public pure override returns (uint256) {
        return PROPOSAL_THRESHOLD;
    }

    function quorum(uint256 blockNumber)
        public
        view
        override(GovernorVotesQuorumFraction)
        returns (uint256)
    {
        return super.quorum(blockNumber);
    }

    // Fonctions requises par GovernorTimelockControl
    function state(uint256 proposalId)
        public
        view
        override(Governor, GovernorTimelockControl)
        returns (ProposalState)
    {
        return super.state(proposalId);
    }

    function propose(
        address[] memory targets,
        uint256[] memory values,
        bytes[] memory calldatas,
        string memory description
    ) public override(Governor, IGovernor) returns (uint256) {
        return super.propose(targets, values, calldatas, description);
    }

    function _execute(
        uint256 proposalId,
        address[] memory targets,
        uint256[] memory values,
        bytes[] memory calldatas,
        bytes32 descriptionHash
    ) internal override(Governor, GovernorTimelockControl) {
        super._execute(proposalId, targets, values, calldatas, descriptionHash);
    }

    function _cancel(
        address[] memory targets,
        uint256[] memory values,
        bytes[] memory calldatas,
        bytes32 descriptionHash
    ) internal override(Governor, GovernorTimelockControl) returns (uint256) {
        return super._cancel(targets, values, calldatas, descriptionHash);
    }

    function _executor()
        internal
        view
        override(Governor, GovernorTimelockControl)
        returns (address)
    {
        return super._executor();
    }
}
