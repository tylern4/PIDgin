# pagurus

Used for getting the information from a running job based on its pid using psutil.

### Options

```
usage: pagurus [-h] [-t TAG] [-o OUTFILE] [-p PATH] [-d] [-r RATE] [-u USER] [-noh] [-mv]

optional arguments:
  -h, --help            show this help message and exit
  -o OUTFILE, --outfile OUTFILE
                        File name for csv.
  -p PATH, --path PATH  Path to put csv file.
  -d, --debug           Run with debugging info.
  -r RATE, --rate RATE  Polling rate for process.
  -u USER, --user USER  Username to get stats for.
  -noh, --no-header     Turn off writting the header.
  -mv, --move           Moves file from 'running' to 'complete'
```


### Running pagurus as a wrapper for a single user
```bash
# Start running wrapper in the background for username
pagurus -u username -mv -p /path/to/output/dir -o test.csv
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
