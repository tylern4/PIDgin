use byte_unit::Byte;
use psutil;
use psutil::process::os::unix::ProcessExt;
use psutil::process::{MemoryInfo, ProcessCpuTimes};
use psutil::Pid;
use std::collections::HashMap;
use std::slice::Iter;
use std::thread;
use std::time::Duration;

#[allow(dead_code)]
pub fn print_mem_avg(key: &u32, mem_vec: &Vec<MemoryInfo>) {
    let mem_iter = mem_vec.into_iter();
    let vms_avg = avgmem(mem_iter.clone(), "vms");
    let rss_avg = avgmem(mem_iter.clone(), "rss");
    let shared_avg = avgmem(mem_iter.clone(), "shared");

    println!("{}, {:#}, {:#}, {:#}", key, vms_avg, rss_avg, shared_avg);
}

#[allow(dead_code)]
pub fn write_out_done_pids(
    done_pids: &Vec<Pid>,
    mem_hash_map: &HashMap<Pid, Vec<MemoryInfo>>,
    _cpu_hash_map: &HashMap<Pid, Vec<ProcessCpuTimes>>,
    _cmd_hash_map: &HashMap<Pid, Vec<String>>,
) {
    for pid in done_pids.into_iter() {
        let mem_info = match mem_hash_map.get(&pid) {
            Some(m) => m,
            None => continue,
        };
        print_mem_avg(&pid, &mem_info);
    }
}

#[allow(dead_code)]
pub fn get_proc_maps() {
    let mut mem_hash_map: HashMap<Pid, Vec<MemoryInfo>> = HashMap::new();
    let mut cpu_hash_map: HashMap<Pid, Vec<ProcessCpuTimes>> = HashMap::new();
    let mut cmd_hash_map: HashMap<Pid, Vec<String>> = HashMap::new();
    let mut done_pids: Vec<Pid> = Vec::new();
    // let mut last_pids: HashSet<Pid> = HashSet::new();
    // let mut current_pids: HashSet<Pid> = HashSet::new();
    let one_nano_sec = Duration::from_millis(100);

    for _i in 0..100 {
        let all_procs = psutil::process::processes().unwrap();
        for proc in all_procs.into_iter() {
            let proc_info = match proc {
                Ok(p) => p,
                Err(_) => continue,
            };

            let pid = proc_info.pid();

            let uid = match proc_info.uids() {
                Ok(u) => u.real,
                Err(_) => 0,
            };

            if uid == 0 {
                continue;
            }

            let cmd1 = match proc_info.cmdline_vec() {
                Ok(x) => x,
                Err(_) => Some(vec!["unkown".to_string()]),
            };

            let cmd: Vec<String> = match cmd1 {
                Some(c) => c,
                None => vec!["unkown".to_string()],
            };

            if !cmd_hash_map.contains_key(&pid) {
                cmd_hash_map.insert(pid, cmd);
            }

            let memory: MemoryInfo = match proc_info.memory_info() {
                Ok(m) => m,
                Err(_) => {
                    // add pid to done list
                    println!("{}", pid);
                    done_pids.push(pid);
                    continue;
                }
            };
            let cpuinfo: ProcessCpuTimes = match proc_info.cpu_times() {
                Ok(c) => c,
                Err(_) => {
                    // add pid to done list
                    println!("{}", pid);
                    done_pids.push(pid);
                    continue;
                }
            };

            if mem_hash_map.contains_key(&pid) {
                let mem_vec = mem_hash_map.get_mut(&pid);
                mem_vec.unwrap().push(memory.clone());
            } else {
                mem_hash_map.insert(pid, vec![memory.clone()]);
            }

            if cpu_hash_map.contains_key(&pid) {
                let cpu_vec = cpu_hash_map.get_mut(&pid);
                cpu_vec.unwrap().push(cpuinfo.clone());
            } else {
                cpu_hash_map.insert(pid, vec![cpuinfo.clone()]);
            }
        }
        write_out_done_pids(&done_pids, &mem_hash_map, &cpu_hash_map, &cmd_hash_map);
        thread::sleep(one_nano_sec);
    }
    done_pids = mem_hash_map.clone().into_keys().collect();
    write_out_done_pids(&done_pids, &mem_hash_map, &cpu_hash_map, &cmd_hash_map);
    eprintln!("Done!");
}

#[allow(dead_code)]
pub fn avgmem(mem_iter: Iter<MemoryInfo>, mem_type: &str) -> Byte {
    let output = match mem_type {
        "vms" => {
            let vms_count: u64 = mem_iter.clone().count() as u64;
            let vms_total: u64 = mem_iter
                .clone()
                .map(|x: &MemoryInfo| x.vms())
                .fold(0, |acc, x| acc + x);
            Byte::from_u64(vms_total / vms_count)
        }
        "rss" => {
            let rss_count: u64 = mem_iter.clone().count() as u64;
            let rss_total: u64 = mem_iter
                .clone()
                .map(|x: &MemoryInfo| x.rss())
                .fold(0, |acc, x| acc + x);
            Byte::from_u64(rss_total / rss_count)
        }
        "shared" => {
            let shared_count: u64 = mem_iter.clone().count() as u64;
            let shared_total: u64 = mem_iter
                .clone()
                .map(|x: &MemoryInfo| x.shared())
                .fold(0, |acc, x| acc + x);
            Byte::from_u64(shared_total / shared_count)
        }
        _ => Byte::from_u64(0),
    };
    return output;
}
