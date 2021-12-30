#!/usr/bin/env python

from lib import util
import pandas as pd
import logging
import argparse

parser = argparse.ArgumentParser(description='Compute the historical fair market value for staking rewards on Tendermint chains.')

parser.add_argument('--rpc', type=str,
                    help='An RPC endpoint for your network (e.g., https://rpc-juno.itastakers.com)')

parser.add_argument('--address', type=str,
                    help='Your wallet address (e.g., juno175q6smvgnuec5e62rs4chnu5cs8d98q2xgf4rx)')

parser.add_argument('--ticker', type=str,
                    help='Osmosis ticker for token (e.g., "JUNO")')

parser.add_argument('--fystart', type=str,
                    help='Start of financial year (e.g., "2021-01-01")')

parser.add_argument('--fyend', type=str,
                    help='End of the financial year (e.g., "2021-12-31")')

parser.add_argument('--outfile', type=str,
                    default=f'out.csv',
                    help='File to write CSV data to. (default "out.csv")')

parser.add_argument('--verbose', '-v', action='count', default=1,
                    help='Log verbosely. One -v is INFO. Try -vv, -vvv, etc.')

args = parser.parse_args()

# Configure logs
# more v's == more verbosity
args.verbose = 40 - (10*args.verbose) if args.verbose > 0 else 0
logging.basicConfig(level=args.verbose, format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

#
# Query RPC for transactions involving the address in question
#
query = f"transfer.recipient='{args.address}'"
logging.info(f'Querying RPC for {query}')
txs = util.historical_txs(args.rpc, query)

#
# Compute inflows and outlfows
#
logging.info(f'Computing inflows and outflows for {args.address}')
inflows, outflows = util.inflows_outflows(txs, args.address)
logging.info(f'Querying RPC for the UTC time of each relevant block height')
block_times = [util.block_time(args.rpc, util.block_height(tx)) for tx in txs]

#
# Find historical pricing data
#
logging.info(f'Querying historical pricing data on {args.ticker}')
prices = util.historical_prices(args.ticker)

#
# Compute historical FMV
#
logging.info(f'Computing historical fair market value (FMV) for {args.ticker}')
historical_fmvs = [(price['time'], util.fmv(price)) for price in  prices]

#
# Align blocks with historical pricing data
#
logging.info(f'Aligning blocks with historical pricing data')
# first, make a df of historical FMVs
fmvs_df = pd.DataFrame(historical_fmvs, columns=['time', 'price'])
fmvs_df['time'] =   pd.to_datetime(fmvs_df['time'],unit='s')
fmvs_df = fmvs_df.set_index('time')
fmvs_df.index =  fmvs_df.index.tz_localize('UTC')
fmvs_df = fmvs_df.sort_values('time')
# then, make a DF of inflows and outflows
inflow_outflow_df = pd.DataFrame({
    'time': block_times,
    'inflow': inflows,
    'outflow': outflows,
})
inflow_outflow_df['time'] = pd.to_datetime(inflow_outflow_df['time'])
inflow_outflow_df = inflow_outflow_df.set_index('time').sort_values('time')
# finally, algin the two data frames
merged_df = pd.merge_asof(inflow_outflow_df, fmvs_df, on='time', direction='nearest')

logging.info(f'For the FY, computing FMV at time of receipt')
merged_df['net'] = merged_df['inflow'] - merged_df['outflow']
# Sanity check that the net in tokens is equal between our raw calculation and the merged dataframe.
# If this is off, we should throw an error and not continue!
assert(merged_df['net'].sum() == sum(inflows) - sum(outflows))
# If that's all well, compute the FMV of the net proceeds at time of receipt.
merged_df['net_usd'] = util.udenom_to_readable(merged_df['net'] * merged_df['price'])
# Filter by financial year
merged_df_fy =  merged_df[(merged_df['time']>=args.fystart) &
                          (merged_df['time']<=args.fyend) ].drop_duplicates() # TODO - why are there duplicate rows?

logging.info(f"Computed net liability as ${merged_df_fy['net_usd'].sum()}")

logging.info(f'Writing CSV to {args.outfile}')
merged_df_fy.to_csv(args.outfile)
