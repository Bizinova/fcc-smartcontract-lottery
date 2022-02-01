from brownie import (
    network,
    config,
    accounts,
    Contract,
    interface,
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken,
)

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev2"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local-two"]


def get_account(index=None, id=None):
    # method 1 - local chain: accounts[0]
    # method 2 - env variable: accounts.add("env")
    # method 3 - cmd line native: accounts.load("id")
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


# place mocking logic in get_contract():
# we want it to deploy a mock if a local env, or deploy test if tests
# create a mapping of

contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "VRF_Coordinator": VRFCoordinatorMock,
    "LINK_Token": LinkToken,
}


def get_contract(contract_name):
    """ "This function will grab the contract addresses from the brownie config
    if defined, otherwise, it will deploy a mock version of that contract, and return
    that mock contract.

        Args:
            contract_name (string)

        Returns:
            brownie.network.contract.ProjectContract: the most recently deployed
            version of this contract.

    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            # MockV3Aggregator.length which checks if a mock has prev been deployed
            deploy_mocks()
        contract = contract_type[-1]
        # MockV3Aggregator[-1], aka get most recent version of deployed contract
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        # address: shown above
        # abi: MockV3Aggregator.abi
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


DECIMALS = 8
INITIAL_VALUE = 200_000_000_000


def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(LinkToken[-1], {"from": account})
    print("Deployed!")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=10_000_000_000_000_000_000
):  # 0.1 Link
    # use the account passed thru, otherwise get_account
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("LINK_Token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    # another way to create contracts and interact, don't need deploy contract cause interfaces compiles ABI
    # link_token_contract = interface.LinkTokenInterface(link_token.address)
    # tx = link_token_contract.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Fund Contract!")
    return tx
