// SPDX-License-Identifier: CC BY-SA 4.0
pragma solidity ^0.8.0;

/**
 * @title MultiSigCRD – MultiSignature pour le CRD Grondona
 * @author Marc Daghar
 * @notice MultiSig à 3/5 pour les décisions critiques du CRD
 * @dev Les modifications des paramètres du CRD (prix plancher/plafond)
 *      nécessitent l'approbation de 3 des 5 muhtassib
 *
 * Licence: CC BY-SA 4.0
 */

contract MultiSigCRD {
    // ---- Événements ----
    event ProposalCreated(
        uint256 indexed proposalId,
        address indexed target,
        uint256 value,
        bytes calldata,
        string description
    );
    event ProposalApproved(
        uint256 indexed proposalId,
        address indexed owner
    );
    event ProposalExecuted(
        uint256 indexed proposalId,
        address indexed executor
    );
    event OwnerAdded(address indexed owner);
    event OwnerRemoved(address indexed owner);
    event RequiredChanged(uint256 newRequired);

    // ---- State ----
    address[] public owners;
    mapping(address => bool) public isOwner;
    uint256 public required;

    struct Proposal {
        uint256 id;
        address target;
        uint256 value;
        bytes calldata;
        string description;
        bool executed;
        uint256 approveCount;
        mapping(address => bool) approves;
        mapping(address => bool) executedBy;
    }

    mapping(uint256 => Proposal) public proposals;
    uint256 public proposalCount;

    // ---- Modifiers ----
    modifier onlyOwner() {
        require(isOwner[msg.sender], "MultiSigCRD: not an owner");
        _;
    }

    modifier validProposal(uint256 proposalId) {
        require(proposalId <= proposalCount, "MultiSigCRD: invalid proposal");
        _;
    }

    modifier notExecuted(uint256 proposalId) {
        require(!proposals[proposalId].executed, "MultiSigCRD: already executed");
        _;
    }

    modifier notApproved(uint256 proposalId) {
        require(!proposals[proposalId].approves[msg.sender], "MultiSigCRD: already approved");
        _;
    }

    // ---- Constructor ----
    constructor(address[] memory _owners, uint256 _required) {
        require(_owners.length > 0, "MultiSigCRD: at least one owner required");
        require(_required > 0 && _required <= _owners.length, "MultiSigCRD: invalid required");

        for (uint256 i = 0; i < _owners.length; i++) {
            address owner = _owners[i];
            require(owner != address(0), "MultiSigCRD: invalid owner");
            require(!isOwner[owner], "MultiSigCRD: duplicate owner");
            isOwner[owner] = true;
            owners.push(owner);
        }

        required = _required;
    }

    // ---- Gestion des propriétaires ----
    function addOwner(address newOwner) external onlyOwner {
        require(newOwner != address(0), "MultiSigCRD: invalid address");
        require(!isOwner[newOwner], "MultiSigCRD: already owner");

        isOwner[newOwner] = true;
        owners.push(newOwner);
        emit OwnerAdded(newOwner);
    }

    function removeOwner(address ownerToRemove) external onlyOwner {
        require(isOwner[ownerToRemove], "MultiSigCRD: not an owner");

        isOwner[ownerToRemove] = false;
        for (uint256 i = 0; i < owners.length; i++) {
            if (owners[i] == ownerToRemove) {
                owners[i] = owners[owners.length - 1];
                owners.pop();
                break;
            }
        }

        // Vérifier que le nombre de propriétaires reste suffisant
        require(owners.length >= required, "MultiSigCRD: would break required");

        emit OwnerRemoved(ownerToRemove);
    }

    function changeRequired(uint256 newRequired) external onlyOwner {
        require(newRequired > 0 && newRequired <= owners.length, "MultiSigCRD: invalid required");
        required = newRequired;
        emit RequiredChanged(newRequired);
    }

    // ---- Propositions ----
    function propose(
        address target,
        uint256 value,
        bytes calldata calldata,
        string memory description
    ) external onlyOwner returns (uint256) {
        require(target != address(0), "MultiSigCRD: invalid target");

        proposalCount++;
        Proposal storage proposal = proposals[proposalCount];
        proposal.id = proposalCount;
        proposal.target = target;
        proposal.value = value;
        proposal.calldata = calldata;
        proposal.description = description;

        emit ProposalCreated(proposalCount, target, value, calldata, description);

        return proposalCount;
    }

    function approve(uint256 proposalId)
        external
        onlyOwner
        validProposal(proposalId)
        notExecuted(proposalId)
        notApproved(proposalId)
    {
        Proposal storage proposal = proposals[proposalId];
        proposal.approves[msg.sender] = true;
        proposal.approveCount++;

        emit ProposalApproved(proposalId, msg.sender);

        // Exécution automatique si le seuil est atteint
        if (proposal.approveCount >= required) {
            _executeProposal(proposalId);
        }
    }

    function _executeProposal(uint256 proposalId) internal {
        Proposal storage proposal = proposals[proposalId];
        require(!proposal.executed, "MultiSigCRD: already executed");
        require(proposal.approveCount >= required, "MultiSigCRD: not enough approvals");

        proposal.executed = true;

        (bool success, ) = proposal.target.call{value: proposal.value}(proposal.calldata);
        require(success, "MultiSigCRD: execution failed");

        emit ProposalExecuted(proposalId, msg.sender);
    }

    function execute(uint256 proposalId)
        external
        onlyOwner
        validProposal(proposalId)
        notExecuted(proposalId)
    {
        Proposal storage proposal = proposals[proposalId];

        // Vérifier que le seuil est atteint
        require(proposal.approveCount >= required, "MultiSigCRD: not enough approvals");

        // Vérifier que l'exécuteur n'a pas déjà exécuté
        require(!proposal.executedBy[msg.sender], "MultiSigCRD: already executed by this address");

        proposal.executedBy[msg.sender] = true;
        _executeProposal(proposalId);
    }

    // ---- View functions ----
    function getOwners() external view returns (address[] memory) {
        return owners;
    }

    function getProposal(uint256 proposalId)
        external
        view
        validProposal(proposalId)
        returns (
            address target,
            uint256 value,
            bytes memory calldata,
            string memory description,
            bool executed,
            uint256 approveCount
        )
    {
        Proposal storage proposal = proposals[proposalId];
        return (
            proposal.target,
            proposal.value,
            proposal.calldata,
            proposal.description,
            proposal.executed,
            proposal.approveCount
        );
    }

    function getApprovalStatus(uint256 proposalId, address owner)
        external
        view
        validProposal(proposalId)
        returns (bool)
    {
        return proposals[proposalId].approves[owner];
    }

    // ---- Receive ----
    receive() external payable {}
}
