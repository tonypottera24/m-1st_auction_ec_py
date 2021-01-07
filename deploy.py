from os import listdir
from os.path import isfile, join
import solcx
import json
from constants.web3 import gas_limit
from pathlib import Path
from lib.tx_print import tx_print

source_path = Path(str(Path(__file__).resolve(
).parents[0].as_posix()).replace('_py', '_sol'))
entry_class = 'Auction'
entry_file = entry_class + '.sol'


def compile():
    # sol_files = [join(source_path, entry_file)]
    # for file_name in listdir(join(source_path, 'lib')):
    #     if isfile(join(source_path, 'lib', file_name)) and file_name.endswith('.sol'):
    #         sol_files.append(join(source_path, 'lib', file_name))
    # return solcx.compile_files(sol_files, base_path=source_path, optimize=True)
    # return solcx.compile_files(sol_files, base_path=source_path, allow_paths=[source_path, source_path.joinpath('lib')], optimize=True, no_optimize_yul=True)
    sources = {}
    with open(join(source_path, entry_file), 'r') as f:
        sources[entry_file] = {'content': f.read()}
    for file_name in listdir(join(source_path, 'lib')):
        if isfile(join(source_path, 'lib', file_name)) and file_name.endswith('.sol'):
            with open(join(source_path, 'lib', file_name), 'r') as f:
                sources[join('lib', file_name)] = {'content': f.read()}

    return solcx.compile_standard({
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
            },
            "optimizer": {
                "enabled": True,
                "details": {
                    "yul": False
                }
            }
        }
    }, solc_version='0.7.6')


def deploy(web3, seller):
    compiled_sol = compile()
    bytecode = compiled_sol['contracts'][entry_file][entry_class]['evm']['bytecode']['object']
    abi = json.loads(compiled_sol['contracts'][entry_file]
                     [entry_class]['metadata'])['output']['abi']
    auction_contract = web3.eth.contract(abi=abi, bytecode=bytecode)
    tx_hash = auction_contract.constructor(seller.m,
                                           seller.price, seller.time_limit, seller.balance_limit).transact({'from': seller.addr, 'gas': gas_limit})
    tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    tx_print(tx_receipt, "Contract created")
    # print("addr = {}".format(tx_receipt.contractAddress))
    auction_contract.address = tx_receipt.contractAddress
    return web3.eth.contract(
        address=tx_receipt.contractAddress, abi=abi)
