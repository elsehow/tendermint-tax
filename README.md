# tendermint-tax

A tool to help calculate the tax liability of staking rewards on Tendermint chains.

Specifically, this tool calculates the fair market value (FMV) of staking
rewards at time of receipt - that is, the time that you claimed the reward. It
does the same for other inflows and outflows of tokens, like sending tokens to a
friend.

# WARNING

### This software might not work

THIS IS A WORK IN PROGRESS. This is experimental software. No one else has looked at it yet. Use at your own risk.

### And even if it does work...

This a tool I use to help my CPA.
This is not tax advice. I am not a CPA.
Use at your own risk.
You have been warned.

# Install

``` sh
# clone this repo
git clone git@github.com:elsehow/tendermint-tax
cd tendermint-tax
# create a python virtual machine
python3 -m venv venv
source venv/bin/activate
# install the dependences
pip3 install -r requirements.txt
```

# Use

This command will get the FMV at time of reciept for
the address `juno175q6smvgnuec5e62rs4chnu5cs8d98q2xgf4rx`
for financial year Jan 1, 2021 - Dec 31, 2021, saving the resulting file as `juno.csv`:

```
# make sure virtual machine is active
source venv/bin/activate
# run tendermint-tax
python3 tendermint-tax.py --rpc  https://rpc-juno.itastakers.com --address juno175q6smvgnuec5e62rs4chnu5cs8d98q2xgf4rx --ticker JUNO --fystart "2021-01-01" --fyend "2021-12-31" --outfile "juno.csv" -v
```

See detailed help on all arguments with `python3 tendermint-tax.py --help`.

# Did this tool help you?

Did this tool save you time or money? Delegate with me!

Stake with me:

- Juno -  [elsehow](https://www.mintscan.io/juno/validators/junovaloper175q6smvgnuec5e62rs4chnu5cs8d98q2e4l6cl) `junovaloper175q6smvgnuec5e62rs4chnu5cs8d98q2e4l6cl`
- Stargaze - [elsehow](https://www.mintscan.io/stargaze/validators/starsvaloper1hvw778wslvyxh6mmv3sy96mwnaw80elmrswc6h) `starsvaloper1hvw778wslvyxh6mmv3sy96mwnaw80elmrswc6h`
- Oasis - [Daylight Network](https://www.oasisscan.com/validators/detail/oasis1qra3rvq7y055waxmnx8rc0nad3frr8na2s9l8l3f) `oasis1qra3rvq7y055waxmnx8rc0nad3frr8na2s9l8l3f`

*Did you know? You don't have to unstake to move your delegation. You can redelegate immediately without unbonding.*

Or pay what you think is fair:

- Cosmos - `cosmos175q6smvgnuec5e62rs4chnu5cs8d98q2s62wy6`
- Osmosis - `osmo175q6smvgnuec5e62rs4chnu5cs8d98q2cpe7jg`
- Akash -  `akash175q6smvgnuec5e62rs4chnu5cs8d98q2ap8faq`
- Regen - `regen175q6smvgnuec5e62rs4chnu5cs8d98q20cpjj7`

# License

BSD-3
