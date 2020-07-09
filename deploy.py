import pprint
from os import listdir
from os.path import isfile, join
from solcx import compile_standard
import json
from constants.web3 import gas_limit
from constants.auction import price, time_limit, balance_limit
from constants.solidity import source_path, entry_file, entry_class
from lib.tx_print import tx_print


def deploy(web3, auctioneer_addr, seller_addr):
    compiled_sol = compile()
    bytecode = compiled_sol['contracts'][entry_file][entry_class]['evm']['bytecode']['object']
    abi = json.loads(compiled_sol['contracts'][entry_file]
                     [entry_class]['metadata'])['output']['abi']
    auction_contract = web3.eth.contract(abi=abi, bytecode=bytecode)
    tx_hash = auction_contract.constructor(
        auctioneer_addr, seller_addr, price, time_limit, balance_limit).transact({'from': auctioneer_addr[0], 'gas': gas_limit})
    tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    tx_print(tx_receipt, "Contract created")
    # print("addr = {}".format(tx_receipt.contractAddress))
    auction_contract.address = tx_receipt.contractAddress
    return web3.eth.contract(
        address=tx_receipt.contractAddress, abi=abi)


def compile():
    sources = {}
    with open(join(source_path, entry_file), 'r') as f:
        sources[entry_file] = {'content': f.read()}
    for file_name in listdir(join(source_path, 'lib')):
        if isfile(join(source_path, 'lib', file_name)) and file_name.endswith('.sol'):
            with open(join(source_path, 'lib', file_name), 'r') as f:
                sources[join('lib', file_name)] = {'content': f.read()}

    return compile_standard({
        'language': 'Solidity',
        'sources': sources,
        "settings":
        {
            "outputSelection": {
                "*": {
                    "*": [
                        "metadata", "evm.bytecode", "evm.bytecode.sourceMap"
                    ]
                }
            }
        }
    })
    # }, optimize=True, optimize_runs=1000)
