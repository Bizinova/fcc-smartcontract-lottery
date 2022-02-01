from scripts.helpful_scripts import get_account, get_contract, fund_with_link
from brownie import Lottery, config, network
import time


def deploy_lottery():
    account = get_account()
    # have diff parameters based on local chain or not
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("VRF_Coordinator").address,
        get_contract("LINK_Token").address,
        config["networks"][network.show_active()]["Fee"],
        config["networks"][network.show_active()]["Key_Hash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print("Deployed lottery!")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery({"from": account})
    starting_tx.wait(3)
    print("The Lottery has started")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 1000000
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(3)
    print("you entered the lottery")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # fund the contract with LINK
    # then end the lottery
    tx = fund_with_link(lottery.address)
    tx.wait(3)
    ending_transaction = lottery.endLottery({"from": account})
    ending_transaction.wait(3)
    time.sleep(90)
    print(f"{lottery.recentWinner()} is the new winner!")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
