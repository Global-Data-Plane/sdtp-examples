# Simple Table Example
This directory hosts the Simple Table Example for the Simple Data Transfer Protocol.  

The server serves the SDML tables in the `tables` directory, which are:
- `electoral_college.sdml`: The electoral college totals
- `nationwide_votes.sdml`: The national popular vote for president
- `presidential_margins.sdml`: A numeric score for each state and year showing which party won the presidential election in that year and by how much.
- `presidential_vote_history.sdml`: By party, showing the cumulative percentage of the vote for each party by state and year.
- `presidential_vote.sdml`: The raw data, showing candidate name, party, state, year, votes, and percentage of the vote
- `nightingale.sdml`: Florence Nightingale's famous Crimean War dataset, which laid the foundation for modern hospitalization.
- `nightingale-summary.sdml`: An aggregated version of Ms. Nightingale's dataset.
- `senate-vote-history.sdml`: Senate elections, 1976-present
- `senate-control.sdml`: Control of the US Senate, 1976-present

To add data to this server, simply add a Simple Data Markup Language file to the tables directory and re-launch the server.

