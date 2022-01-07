#!/usr/bin/env python

from requests import get, post
from funcy import flatten
import math
import base64
import pandas as pd
import json
from typing import List, Dict

def tx_search (rpc, query, page='1', per_page='100') -> List[Dict]:
    '''
    See: htps://docs.tendermint.com/master/app-dev/indexing-transactions.html

    e.g.,

       curl --header "Content-Type: application/json" --request POST --data '{"method": "tx_search", "params": ["3D1000", "true", "1", "30", "asc"], "id": 0}' cro-croeseid.alchemyapi.io/your-api-key/tendermint

    params:

    - query - string, required query.
    - prove - boolean, include proofs of the transactions inclusion in the block. Default value = false
    - page - integer, page number (1-based). Default value = 1
    - per_page - integer, number of entries per page (max: 100). Default value = 30.
    - order_by - string, Order in which transactions are sorted ("asc" or "desc"), by height & index. If empty, default sorting will be still applied. Default value = asc
    '''
    q =  {
        "method": "tx_search",
        "params": [
            # query
            query,
            # prove
            False,
            # page
            page,
            # per_page
            per_page,
            # order_by
            'asc',
        ],
        "id": 0,
    }
    resp = post(rpc, json=q)
    return resp.json()


def historical_txs (rpc, query) -> List[Dict]:
    txs = []
    per_page = 100
    # print('querying page 1')
    res = tx_search(rpc, query, per_page=str(per_page))
    total = int(res['result']['total_count'])
    txs.append(res['result']['txs'])
    n_pages = math.ceil(total/per_page)
    pages_left = n_pages
    for i in range(pages_left):
        # print('querying page',2+i)
        res = tx_search(rpc, query, page=str(1+i), per_page=str(per_page))
        txs.append(res['result']['txs'])
    return list(flatten(txs))


def events (tx: Dict) -> List[Dict]:
    tx_events = []
    log = json.loads(tx['tx_result']['log'])
    for item in log:
        tx_events.append(item['events'])
    return list(flatten(tx_events))


def find_attr_value (attrs: List[Dict], attr_key: str):
    return [a for a in attrs if a['key']==attr_key][0]['value']


def udenom_to_int (udenom: str) -> int:
    try:
        return int(udenom.split('u')[0])
    except:
        return 0


def extract_staking_activity (events: List[Dict], event_type):
    denoms = []
    for event in events:
        if event['type'] == event_type:
            attrs = event['attributes']
            v = find_attr_value(attrs, 'amount')
            v = udenom_to_int(v)
            denoms.append(v)
    return denoms


def extract_inflow_staking_rewards (events) -> List[int]:
    return extract_staking_activity(events, 'withdraw_rewards')


def extract_inflow_staking_commission (events) -> List[int]:
    return extract_staking_activity(events, 'withdraw_commission')


def extract_outflow_staking_delegations (events) -> List[int]:
    return extract_staking_activity(events, 'delegate')


def extract_transfer (events: List[Dict], event_type: str, attr_key: str, attr_value: str) -> List[int]:
    '''
    TODO - pretty similar to `extract_reward_income`. make DRY?
    '''
    denoms = []
    for event in events:
        if event['type'] == event_type:
            attrs = event['attributes']
            x = find_attr_value(attrs, attr_key)
            if x == attr_value:
                v = find_attr_value(attrs, 'amount')
                v = udenom_to_int(v)
                denoms.append(v)
    return denoms


def extract_inflow_transfer(events: List[Dict], my_address: str) -> List[int]:
    return extract_transfer(events, 'transfer', 'recipient', my_address)


def extract_outflow_transfer (events: List[Dict], my_address: str):
    return extract_transfer(events, 'transfer', 'sender', my_address)


# TODO - these spends appear to be redundant with transfers, but we should verify this.
#        documentation on these event types would be helpful.

# def extract_inflow_spends (events: List[Dict], my_address: str) -> List[int]:
#     return extract_transfer(events, 'coin_received', 'receiver', my_address)


# def extract_outflow_spends (events: List[Dict], my_address: str):
#     return extract_transfer(events, 'coin_spent', 'spender', my_address)


def inflows_outflows (txs: List[Dict], my_address:str) -> float:
    '''
    Get the inflows (tokens coming in) and outflows (tokens going out) across
    '''
    inflows = []
    outflows = []
    for tx in txs:
        es = events(tx)
        inflow = extract_inflow_staking_rewards(es) + extract_inflow_staking_commission(es) + extract_inflow_transfer(es, my_address) #+ extract_inflow_spends(es, my_address)
        outflow =  extract_outflow_staking_delegations(es)  + extract_outflow_transfer(es, my_address) #+ extract_outflow_spends(es, my_address)
        inflows.append(sum(flatten(inflow)))
        outflows.append(sum(flatten(outflow)))
    return inflows, outflows


def udenom_to_readable(udenom: int) -> float:
    return udenom/1000000


def block_height (tx) -> int:
    return int(tx['height'])


def block_time (rpc: str, height: int) -> str:
    '''
    Get the UTC time of a particular block.
    '''
    return get(f'{rpc}/block?height={height}').json()['result']['block']['header']['time']


def historical_prices (coin:str) -> List[Dict]:
    '''
    Get historical (USD) prices from Osmosis.
    '''
    return get(f'https://api-osmosis.imperator.co/tokens/v1/historical/{coin}/chart?range=365d').json()


def fmv (price):
    '''
    Our estimate of the FMV in a given trading period is is the average between the high and low price during that period.
    '''
    return (price['high'] + price['low']) / 2


# TODO - depricated - see https://github.com/elsehow/tendermint-tax/issues/2
# def get_holdings (rest_endpoint: str, address: str) -> int:
#     '''
#     Get the number of tokens currently held by `address` across delegated, unbonding, and unstaked tokens.
#     '''

#     def rest (path):
#         return get(rest_endpoint + path).json()

#     def get_amount (balance: dict) -> int:
#         return int(balance['amount'])

#     # def get_balance () -> int:
#     #     if not denom:
#     #         resp = rest(f"/cosmos/bank/v1beta1/balances/{address}")
#     #         return get_amount(resp['balances'][0])
#     #     else:
#     #         resp = rest(f"/cosmos/bank/v1beta1/balances/{address}/{denom}")
#     #         return get_amount(resp['balance'])

#     def get_delegations () -> List[int]:
#         resp = rest(f"/cosmos/staking/v1beta1/delegations/{address}")
#         return [get_amount(d['balance']) for d in resp['delegation_responses']]

#     def get_unbonding () -> List[int]:
#         resp = rest(f"/cosmos/staking/v1beta1/delegators/{address}/unbonding_delegations")
#         return flatten([
#             [int(e['balance'])  for e in r['entries']]
#             for r in resp['unbonding_responses']
#         ])

#     holdings = sum(get_delegations()) + sum(get_unbonding()) # + get_balance()
#     return holdings
