#!/usr/bin/env python3
from web3 import Web3
from deploy import deploy
from bidder import Bidder
from seller import Seller
from constants.web3 import provider_url, http_timeout
import time

web3 = Web3(Web3.HTTPProvider(provider_url,
                              request_kwargs={'timeout': http_timeout}))

if web3.isConnected() == False:
    print("web3 connection failed.", flush=True)
    exit(1)
else:
    print("web3 connected!", flush=True)

accounts = web3.eth.accounts
bidder_count = 3

seller = Seller(accounts[0],
                price=[p for p in range(1, bidder_count*2 + 1)],
                time_limit=[15, 1000000, 1000000, 1000000, 1000000, 1000000],
                balance_limit=10)

auction_contract = deploy(web3, seller)

bidders = [Bidder(i, accounts[i + 1], web3, auction_contract)
           for i in range(bidder_count)]

print()

print('Phase 1 bidder init:', flush=True)
for bidder in bidders:
    bidder.phase_1_bidder_init()

print('Wait for phase 1 ends:', flush=True)
t = bidders[0].phase_1_time_left()
print('wait {:.2f} sec'.format(t), flush=True)
time.sleep(t + 3)

success = auction_contract.functions.phase1Success().call()
if success == False:
    print('Phase 1 failed\n', flush=True)
    exit(1)
else:
    print('Phase 1 success\n', flush=True)

print('Phase 2 bidder submit bid:', flush=True)
for bidder in bidders:
    bidder.phase_2_bidder_submit_bid(
        bidder.index % len(bidder.auction_info.price))
    # bid_debug = bidder.phase_2_bidder_join(len(price) - 1)

success = auction_contract.functions.phase2Success().call()
if success == False:
    print('Phase 2 failed\n', flush=True)
    exit(1)
else:
    print('Phase 2 success\n', flush=True)

print('Phase 3.1 bidder verification sum 1:', flush=True)
for bidder in bidders:
    bidder.phase_3_bidder_verification_sum_1()

print('Phase 3.2.1 bidder verification 01 omega:', flush=True)
bidders[0].phase_3_bidder_verification_01_omega()

print('Phase 3.2.2 bidder verification 01 dec:', flush=True)
for bidder in bidders:
    bidder.phase_3_bidder_verification_01_dec()

success = auction_contract.functions.phase3Success().call()
if success == False:
    print('Phase 3 failed\n', flush=True)
    exit(1)
else:
    print('Phase 3 success\n', flush=True)

print('Phase 4.1 second highest bid decision omega:', flush=True)
bidders[0].phase_4_second_highest_bid_decision_omega()

print('Phase 4.2 second highest bid decision dec:', flush=True)
while True:
    success = auction_contract.functions.phase4Success().call()
    binarySearchL = auction_contract.functions.binarySearchL().call()
    binarySearchR = auction_contract.functions.binarySearchR().call()
    secondHighestPriceJ = auction_contract.functions.secondHighestPriceJ().call()
    print('({}, {}, {})'.format(binarySearchL,
                                secondHighestPriceJ, binarySearchR), flush=True)
    if success or binarySearchL == len(bidders[0].auction_info.price) - 1:
        print('Multiple bidder chose maximum bidding price.', flush=True)
        break
    for bidder in bidders:
        bidder.phase_4_second_highest_bid_decision_dec()

success = auction_contract.functions.phase4Success().call()
if success == False:
    print('Phase 4 failed\n', flush=True)
    exit(1)
else:
    secondHighestPriceJ = auction_contract.functions.secondHighestPriceJ().call()
    print('secondHighestPriceJ = {}'.format(
        secondHighestPriceJ), flush=True)
    print('Phase 4 success\n', flush=True)

print('Phase 5 winner decision:', flush=True)
for bidder in bidders:
    bidder.phase_5_winner_decision()

success = auction_contract.functions.phase5Success().call()
if success == False:
    print('Phase 5 failed\n', flush=True)
    exit(1)
else:
    winnerI = auction_contract.functions.winnerI().call()
    print('winnerI = {}'.format(winnerI), flush=True)
    print('Phase 5 success\n', flush=True)


highest_bid_j = -1
second_highest_bid_j = -1
bidder_bids = [bidder.bid_price_j for bidder in bidders]
bidder_bids.sort()
for bidder_bid in bidder_bids:
    if bidder_bid > highest_bid_j:
        second_highest_bid_j = highest_bid_j
        highest_bid_j = bidder_bid

for bidder in bidders:
    if bidder.bid_price_j == highest_bid_j:
        print('[B{:2}]'.format(bidder.index), end='', flush=True)
    else:
        print(' B{:2} '.format(bidder.index), end='', flush=True)
print()

for bidder in bidders:
    if bidder.bid_price_j == second_highest_bid_j:
        print('[{:3}]'.format(bidder.bid_price_j), end='', flush=True)
    else:
        print(' {:3} '.format(bidder.bid_price_j), end='', flush=True)
print()

print('price = {}'.format(bidders[0].auction_info.price), flush=True)

# for auctioneer in auctioneers:
#     print('A{} balance = {}'.format(auctioneer.index,
#                                     web3.eth.getBalance(auctioneer.addr)))
# for bidder in bidders:
#     print('B{} balance = {}'.format(bidder.index,
#                                     web3.eth.getBalance(bidder.addr)))
balances = auction_contract.functions.getBalance().call()
print('balances = {}'.format(balances), flush=True)

print('Phase 6 payment:', flush=True)
bidders[winnerI].phase_6_payment()

success = auction_contract.functions.phase6Success().call()
if success == False:
    print('Phase 6 failed\n', flush=True)
    exit(1)
else:
    print('Phase 6 success\n', flush=True)

for bidder in bidders:
    print('B{} used {:,} gas'.format(bidder.index, bidder.gasUsed), flush=True)

# balances = auction_contract.functions.getBalance().call()
# print('balances = {}'.format(balances))
