#Scripts for EIGER CSCS workflow

- submit_warmup.sh and submit_nnlojet.sh works similarly to teh Euler ones.
But the in the production modify the number of nodes. Jobs will be 256 x nodes. 
You can set the initial seed. 
- check_err.sh is the same
- setchannels.sh is the same. Currently not perfect on Eiger. 
- myjobs.sh print running jobs.
- timequota.sh print remaining quota for the group from terminal line
