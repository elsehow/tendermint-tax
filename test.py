#!/usr/bin/env python
#
import json

from lib import util

JUNO_ADDR = 'juno175q6smvgnuec5e62rs4chnu5cs8d98q2xgf4rx'

def load_txs ():
    with open('mock-txs.json', 'r') as f:
        return json.load(f)


def test_events ():
    tx = load_txs()[0]
    assert( util.events(tx)==[{'type': 'coin_received',
                               'attributes': [{'key': 'receiver',
                                               'value': 'juno175q6smvgnuec5e62rs4chnu5cs8d98q2xgf4rx'},
                                              {'key': 'amount', 'value': '26099278ujuno'}]},
                              {'type': 'coin_spent',
                               'attributes': [{'key': 'spender',
                                               'value': 'juno1jv65s3grqf6v6jl3dp4t6c9t9rk99cd83d88wr'},
                                              {'key': 'amount', 'value': '26099278ujuno'}]},
                              {'type': 'message',
                               'attributes': [{'key': 'action',
                                               'value': '/cosmos.distribution.v1beta1.MsgWithdrawDelegatorReward'},
                                              {'key': 'sender', 'value': 'juno1jv65s3grqf6v6jl3dp4t6c9t9rk99cd83d88wr'},
                                              {'key': 'module', 'value': 'distribution'},
                                              {'key': 'sender', 'value': 'juno175q6smvgnuec5e62rs4chnu5cs8d98q2xgf4rx'}]},
                              {'type': 'transfer',
                               'attributes': [{'key': 'recipient',
                                               'value': 'juno175q6smvgnuec5e62rs4chnu5cs8d98q2xgf4rx'},
                                              {'key': 'sender', 'value': 'juno1jv65s3grqf6v6jl3dp4t6c9t9rk99cd83d88wr'},
                                              {'key': 'amount', 'value': '26099278ujuno'}]},
                              {'type': 'withdraw_rewards',
                               'attributes': [{'key': 'amount', 'value': '26099278ujuno'},
                                              {'key': 'validator',
                                               'value': 'junovaloper175q6smvgnuec5e62rs4chnu5cs8d98q2e4l6cl'}]}]
           )

def test_extract_inflow_outflow ():
    tx = load_txs()[0]
    assert(util.extract_inflow_staking_rewards(util.events(tx)) == [26099278])

    tx = load_txs()[-2]
    assert(util.extract_inflow_staking_commission(util.events(tx)) == [20444435])

    tx = load_txs()[3]
    assert(util.extract_outflow_staking_delegations(util.events(tx))  == [5000000])

    tx = load_txs()[0]
    assert(util.extract_inflow_transfer(util.events(tx), JUNO_ADDR) == [26099278])

    tx = load_txs()[0]
    assert(util.extract_outflow_transfer(util.events(tx), JUNO_ADDR) == [])

    # tx = load_txs()[0]
    # assert(util.extract_inflow_spends(util.events(tx), JUNO_ADDR) == [26099278])

    # tx = load_txs()[0]
    # assert(util.extract_outflow_spends(util.events(tx), JUNO_ADDR) == [])

    inf, outf = util.inflows_outflows(load_txs(), JUNO_ADDR)
    assert(sum(inf) == 13760829206)
    assert(sum(outf) == 11688642282)


def test_udenom_to_readable ():
    assert(util.udenom_to_readable(998059) == 0.998059)


def test_block_height ():
    tx = load_txs()[0]
    assert(util.block_height(tx) == 32970)


def test_fmv ():
    price = {
        'high': 10,
        'low': 9
    }
    assert(util.fmv(price) == 9.5)
