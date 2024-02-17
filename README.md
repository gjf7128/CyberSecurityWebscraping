# fuzzer deliverable 0:

## Fuzzer part 2:  
Not even going to bother checking if the ci runs because it never does  
I managed to get everything other than --sensitive programmed  
  
This should work with any URL, but since dvwa is our main test env, i recommend using --custom-auth=dvwa  
so that the security is lowered and you'll get to see results.  I was using the following to test:  
python main.py test http://127.0.0.1/dvwa/vulnerabilities/brute/ --custom-auth=dvwa --vectors=vectors.txt --sanitized-chars=sanitized.txt --slow=100 --response=yes


## Getting started
http://localhost is not working when running the CI script.  I tried

## Running without CI Option 1:
run python main.py in the terminal and when the CLI menu prompts, enter 'discover http://127.0.0.1 --custom-auth=dvwa'

## Running without CI Option 2 (using args):
in the terminal run: 'python main.py --deliverable0 http://127.0.0.1'  

## Part 1 running with arguments:
python main.py discover http://localhost/fuzzer-tests --common-words=mywords.txt --extension=extensions.txt  
I once again could not get the CI pipeline to pass even after refining my argparse
