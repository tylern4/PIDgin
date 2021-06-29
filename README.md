# PIDgin

Used for getting the information from a running job based on its PID using psutil.

PIDgin waits for a pid to be stored in a file called watch.pid and then reads it and starts extracting information and saving to a csv file. It can also attach to an already running processes by supplying the `--pid` option.

### As a wrapper script
```bash
pagurus.py test_program arg1 --arg2=4
```

### Example Usage slurm

```bash
python pagurus.py &
WAITPID=$!
sleep 10
test_program arg1 --arg2=4 &
echo $! > watch.pid
wait $WAITPID
```

### Attaching to a running program

```bash
test_program arg1 --arg2=4 &
python pagurus.py -i $!
```

