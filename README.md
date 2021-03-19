# P2P_LAMDEN

## Lamden contract for a peer to peer betting protocol

Allows any user to create a yes/no bet and any other user to take the bet, had a built in stake validator model to handle dishonest parties. Contracts and test suite were completed a few months ago, but don't have time to build out the whole dapp. I wrote the tests before I knew what pytest fixtures were so atm you have to run everyone individually, if u add an isolate function it should be cool.
p2p_contract.py is the test compatible version of the contract.
p2p_contract_func.py is the mainnet/testnet compatible version of the contract.

Here was a wireframe mockup i did to help explain how it works.

[Mockup of frontend dApp](https://siasky.net/XAGcmS43qrCRKyRgIuAfm6-E8rvYHHHHoQy2sLQwSrLZtQ)

I started making changes to deal with masternode api rate limits, i'm pretty sure I concluded that, but I may have forgotten if I finished that part or not, in any case, if I didn't conclude it, there will be very minor things to change (look for commmented code).

Feel free to use however you want, you can credit me if you want, otherwise, no biggie.

Have fun!
