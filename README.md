# pagurus

Used for getting the information from a running job based on its pid using psutil.

### Running pagurus as a wrapper for a single user
```bash
# Start running wrapper in the background for username
pagurus -u username -d -mv -p /path/to/output -o test.csv
# Get the previous running PID of pagurus
export PID=$!
# Sleep for a few seconds to let everything start running
sleep 10 


# Run your desired program as normal
./a.out

# Kill the pagurus process
kill $PID

# Sleep for a few seconds to let results finish writing
sleep 10
```


<!-- ### Plotting results
```bash
hermit -i test_data-time.csv
``` -->