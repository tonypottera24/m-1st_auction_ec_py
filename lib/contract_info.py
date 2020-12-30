class AuctionInfo():
    def __init__(self, auction_contract):
        self.auction_contract = auction_contract
        self.update()

    def update(self):
        self.price = self.auction_contract.functions.getPrice().call()
        self.timer = self.auction_contract.functions.getTimer().call()
