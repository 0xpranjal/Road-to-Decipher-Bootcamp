from typing import Final

from pyteal import *
from beaker import (
    Application,
    ApplicationStateValue,
    AccountStateValue,
    create,
    opt_in,
    external,
    internal,
    delete,
    bare_external,
    Authorize
)

class EventRSVP(Application):

    price: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.uint64,
        default=Int(1000000),
        descr="The price of the event. Default price is 1 Algo"
    )

    rsvp: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.uint64,
        default=Int(0),
        descr="Number of people who RSVPed to the event"
    )

    checked_in: Final[AccountStateValue] = AccountStateValue(
        stack_type=TealType.uint64,
        default=Int(0),
        descr="0 = not checked in, 1 = checked in"
    )

    ############
    # Constants#
    ############

    # Contract address minimum balance
    MIN_BAL = Int(100000)

    # Algorand minimum txn fee
    FEE = Int(1000)

    @create
    def create(self, event_price: abi.Uint64):
        """Deploys the contract and initialze the app states"""
        return Seq(
            self.initialize_application_state(),
            self.price.set(event_price.get()),
        )

    @opt_in
    def do_rsvp(self, payment: abi.PaymentTransaction):
        """Let txn sender rsvp to the event by opting into the contract"""
        return Seq(
            Assert(
                Global.group_size() == Int(2),
                payment.get().receiver() == self.address,
                payment.get().amount() == self.price,
            ),
            self.initialize_account_state(),
            self.rsvp.increment(),
        )

    @external(authorize=Authorize.opted_in(Global.current_application_id()))
    def check_in(self):
        """If the Sender RSVPed, check-in the Sender"""
        return self.checked_in.set(Int(1))

    @internal
    def withdraw_funds(self):
        """Helper method that withdraws funds in the RSVP contract"""
        rsvp_bal = Balance(self.address)
        return Seq(
            Assert(
                rsvp_bal > (self.MIN_BAL + self.FEE),
            ),
            InnerTxnBuilder.Execute({
                TxnField.type_enum: TxnType.Payment,
                TxnField.receiver: Txn.sender(),
                TxnField.amount: rsvp_bal - (self.MIN_BAL + self.FEE),
            }),
        )
    
    @external(authorize=Authorize.only(Global.creator_address()))
    def withdraw_external(self):
        """Let event creator to withdraw all funds in the contract"""
        return self.withdraw_funds()

    @delete(authorize=Authorize.only(Global.creator_address()))
    def delete(self):
        """Let event creator delete the contract. Withdraws remaining funds"""
        return If(Balance(self.address) > (self.MIN_BAL + self.FEE), self.withdraw_funds())
    
    @bare_external(close_out=CallConfig.CALL, clear_state=CallConfig.CALL)
    def refund(self):
        """Refunds event payment to guests"""
        return Seq(
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.Payment,
                TxnField.receiver: Txn.sender(),
                TxnField.amount: self.price - self.FEE,
            }),
            InnerTxnBuilder.Submit(),
            self.rsvp.decrement()
        )

    ################
    # Read Methods #
    ################
    
    @external(read_only=True, authorize=Authorize.only(Global.creator_address()))
    def read_rsvp(self, *, output: abi.Uint64):
        """Read amount of RSVP to the event. Only callable by Creator."""
        return output.set(self.rsvp)
    
    @external(read_only=True)
    def read_price(self, *, output: abi.Uint64):
        """Read amount of RSVP to the event. Only callable by Creator."""
        return output.set(self.price)


if __name__ == "__main__":
    import os
    import json

    path = os.path.dirname(os.path.abspath(__file__))

    rsvp_app = EventRSVP()

    # Dump out the contract as json that can be read in by any of the SDKs
    with open(os.path.join(path, "contract.json"), "w") as f:
        f.write(json.dumps(rsvp_app.application_spec(), indent=2))

    # Write out the approval and clear programs
    with open(os.path.join(path, "approval.teal"), "w") as f:
        f.write(rsvp_app.approval_program)

    with open(os.path.join(path, "clear.teal"), "w") as f:
        f.write(rsvp_app.clear_program)
