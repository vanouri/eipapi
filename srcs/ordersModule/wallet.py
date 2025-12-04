import json
import os

class Wallet:
    def __init__(self, amount=0):
        if os.path.exists("cryptoBot/ordersModule/wallet.json"):
            # with open("cryptoBot/ordersModule/wallet.json", "w") as f:
            #     json.dump({"USD": int(amount)}, f)
            a = 1
        else:
            with open("cryptoBot/ordersModule/wallet.json", "w") as f:
                json.dump({"USD": int(amount)}, f)
        self.wallet = json.load(open("cryptoBot/ordersModule/wallet.json", "r"))

    def get_balance(self):
        return self.wallet["USD"]

    def add_money(self, amount):
        self.wallet["USD"] += amount
        with open("cryptoBot/ordersModule/wallet.json", "w") as f:
            json.dump(self.wallet, f)
        return True

    def remove_money(self, amount):
        if self.wallet["USD"] < amount:
            print("Not enough money")
            return False
        self.wallet["USD"] -= amount
        with open("cryptoBot/ordersModule/wallet.json", "w") as f:
            json.dump(self.wallet, f)
        return True

    def init_found(self, amount):
        self.wallet["USD"] = amount
        with open("cryptoBot/ordersModule/wallet.json", "w") as f:
            json.dump(self.wallet, f)
        return True