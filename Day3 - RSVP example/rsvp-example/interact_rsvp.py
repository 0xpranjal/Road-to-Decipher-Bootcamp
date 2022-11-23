from algosdk.future import transaction
from algosdk.error import AlgodHTTPError
from algosdk.atomic_transaction_composer import (
    TransactionWithSigner,
)

from beaker import sandbox, consts
from beaker.client import ApplicationClient

from rsvp import EventRSVP

client = sandbox.get_algod_client()
accts = sandbox.get_accounts()

creator_acct = accts.pop()
guest_acct1 = accts.pop()
guest_acct2 = accts.pop()


# Create instance of the EventRSVP contract
app = EventRSVP()

# Create an Application client for event creator containing both an algod client and my app
app_client = ApplicationClient(client, app, signer=creator_acct.signer)

def rsvp_testing():

    print("### CREATE AND INITIALIZE CONTRACT ### \n")
    sp = client.suggested_params()
    # Create the applicatiion on chain, set the app id for the app client
    app_id, app_addr, txid = app_client.create(event_price=1 * consts.algo)
    print(f"Created App with id: {app_id} and address addr: {app_addr} in tx: {txid}")

    event_price = app_client.call(app.read_price)
    print(f"Event price is set to {event_price.return_value} microAlgos")

    # Fund the contract for minimum balance
    app_client.fund(100*consts.milli_algo)
    print(f"RSVP Balance: {client.account_info(app_addr).get('amount')} microAlgos \n")

    # Guest 1
    print("### GUEST 1 SCENARIO ###\n")
    
    # Set up Guest 1 application client
    app_client_guest1 = app_client.prepare(signer=guest_acct1.signer)

    # RSVP to the event by opting in
    print("Guest 1 rsvp to the event...")
    ptxn2 = TransactionWithSigner(
            txn=transaction.PaymentTxn(guest_acct1.address, sp, app_addr,1 * consts.algo),
            signer=guest_acct1.signer,
        )
    
    # Opt in to contract with event registration payment included
    app_client_guest1.opt_in(payment=ptxn2)
    acct_state = app_client_guest1.get_account_state()
    checked_in_val = acct_state["checked_in"]
    print(f"Only RSVPed so checked_in should be 0 and the state is {checked_in_val}")
    print(f"RSVP Balance: {client.account_info(app_addr).get('amount')} microAlgos \n")
    
    # Check in to the event
    print("Guest 1 checking in to the Event...")
    app_client_guest1.call(app.check_in)
    acct_state = app_client_guest1.get_account_state()
    checked_in_val = acct_state["checked_in"]
    print(f"checked_in should be 1 and the state is {checked_in_val}")
    
    # See How many RSVPed
    result = app_client.call(app.read_rsvp)
    print(f"The number of people RSVPed should be 1 and it is {result.return_value}\n")

    # Guest 2 Scenario

    print("### GUEST 2 SCENARIO ###\n")
    # Set up Guest 2 application client
    app_client_guest2 = app_client.prepare(signer=guest_acct2.signer)

    # RSVP to the event by opting in
    print("Guest 2 rsvp to the event...")
    ptxn2 = TransactionWithSigner(
            txn=transaction.PaymentTxn(guest_acct2.address, sp, app_addr,1 * consts.algo),
            signer=guest_acct2.signer,
        )
    # Opt in to contract with event registration payment included
    app_client_guest2.opt_in(payment=ptxn2)
    acct_state = app_client_guest2.get_account_state()
    checked_in_val = acct_state["checked_in"]
    print(f"Only RSVPed so checked_in should be 0 and the state is {checked_in_val}")
    print(f"RSVP Balance: {client.account_info(app_addr).get('amount')} microAlgos")
    
    # See How many RSVPed
    result = app_client.call(app.read_rsvp)
    print(f"The number of people RSVPed should be 2 and it is {result.return_value}\n")

    # Cancel RSVP to the event
    print("Guest 2 canceling registration and getting refund...")
    app_client_guest2.close_out()

    try:
        app_client_guest2.get_account_state()
    except AlgodHTTPError as e:
        print(f"Succesfully closed_out: {e}")

    # See How many RSVPed
    result = app_client.call(app.read_rsvp)
    print(f"The number of people RSVPed should be 1 and it is {result.return_value}")
    print(f"RSVP Balance: {client.account_info(app_addr).get('amount')} microAlgos \n")

    # Withdraw and Delete Scenario

    print("### WITHDRAW AND DELETE SCENARIO ###\n")

    # Withdraw funds and close event RSVP
    print("Event creator withdrawing funds...")
    app_client.call(app.withdraw_external)
    print(f"Event creator successfully withdrew remaining balance.")
    print(f"RSVP Balance: {client.account_info(app_addr).get('amount')} microAlgos \n")

    print("Event creator deleting rsvp contract...")
    app_client.delete()
    print(f"RSVP successfully deleted")

if __name__ == "__main__":
    rsvp_testing()