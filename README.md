NIFTY Option Chain Data Fetcher (NSE API)

This project fetches NIFTY option-chain data directly from NSE's public API using requests.Session(), cleans it, removes duplicates, and exports the result to CSV.

Features:

Fetches latest NIFTY Option Chain data

Supports both PE (Put) and CE (Call) sides

Automatically handles NSE cookies + headers

Cleans & aggregates data → one strike per row

Exports:

pe.csv

ce.csv

Technologies Used:

Python

requests

pandas

How It Works:

NSE blocks bot requests, so we:

Start a session

Request homepage to collect fresh cookies

Hit the option-chain API using those cookies

Parse & clean the JSON

Save clean DataFrames to CSV


Run the script:  
python open_chain_new.py


Output:

pe.csv → highest bid for PE per strike

ce.csv → highest ask for CE per strike


AI Assistance

ChatGPT was used for:

Debugging the NSE API headers/cookies method

Improving parsing logic

Cleaning duplicate strikes
