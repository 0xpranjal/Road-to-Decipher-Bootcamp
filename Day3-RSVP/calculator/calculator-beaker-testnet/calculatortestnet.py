from pyteal import abi

from beaker.client.application_client import ApplicationClient
from beaker.application import Application
from beaker.decorators import external
from beaker import sandbox

from algosdk import mnemonic
from algosdk import account
from algosdk.atomic_transaction_composer import AccountTransactionSigner


class Calculator(Application):
    @external
    def add(self, a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64):
        """Add a and b, return the result"""
        return output.set(a.get() + b.get())

    @external
    def mul(self, a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64):
        """Multiply a and b, return the result"""
        return output.set(a.get() * b.get())

    @external
    def sub(self, a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64):
        """Subtract b from a, return the result"""
        return output.set(a.get() - b.get())

    @external
    def div(self, a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64):
        """Divide a by b, return the result"""
        return output.set(a.get() / b.get())


def demo():
    token = "2f3203f21e738a1de6110eba6984f9d03e5a95d7a577b34616854064cf2c0e7b"
    address = "https://academy-algod.dev.aws.algodev.network/"
    # demonstration purposes only, never use mnemonics in code
    mnemonic_1 = "price clap dilemma swim genius fame lucky crack torch hunt maid palace ladder unlock symptom rubber scale load acoustic drop oval cabbage review abstract embark"

    client = sandbox.get_algod_client(address, token)
    print_address(mnemonic_1)
    # acct = sandbox.get_accounts().pop()

    # Create an Application client containing both an algod client and app
    app_client = ApplicationClient(client=client, app=Calculator(
        version=6), signer=AccountTransactionSigner(mnemonic.to_private_key(mnemonic_1)))

    # Create the application on chain, set the app id for the app client
    app_id, app_addr, txid = app_client.create()
    print(
        f"Created App with id: {app_id} and address addr: {app_addr} in tx: {txid}")

    result = app_client.call(Calculator.add, a=2, b=2)
    print(f"add result: {result.return_value}")

    result = app_client.call(Calculator.mul, a=2, b=2)
    print(f"mul result: {result.return_value}")

    result = app_client.call(Calculator.sub, a=6, b=2)
    print(f"sub result: {result.return_value}")

    result = app_client.call(Calculator.div, a=16, b=4)
    print(f"div result: {result.return_value}")


def print_address(mn):
    pk_account_a = mnemonic.to_private_key(mn)
    address = account.address_from_private_key(pk_account_a)
    print("Creator Account Address :", address)


if __name__ == "__main__":
    import json

    calc = Calculator()
    print(calc.approval_program)
    print(calc.clear_program)
    print(json.dumps(calc.contract.dictify()))

    demo()
