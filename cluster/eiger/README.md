#Scripts for EIGER CSCS workflow

- submit_warmup.sh and submit_nnlojet.sh works similarly to teh Euler ones.
But the in the production modify the number of nodes. Jobs will be 256 x nodes.
- submit_combine.sh to run the nnlojet-combine.py script on the computing node. 
Required for massive production when you have many small files.
- submit_all_warmup.sh is an optimized way to submit multiple warmup runs to a 
single EIGER node, saving node/hours. Also, having a single job simplify to 
submit the production with the dependency option.
 
You can set the initial seed. 
- check_err.sh is the same
- setchannels.sh is the same. Currently not perfect on Eiger. 
- copy_setup.sh is an alternative way to set up the initial folder starting 
from an existing one.
- myjobs.sh print running jobs.
- timequota.sh print remaining quota for the group from terminal line
