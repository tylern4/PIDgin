# pagurus

Used for getting the information from a running job based on its pid using psutil.


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

