mod pagurus;

use chrono::Local;

use psutil::process::os::unix::ProcessExt;
use psutil::process::{MemoryInfo, ProcessCpuTimes};
use psutil::Pid;
use signal_hook::low_level::exit;
use signal_hook::{consts::SIGINT, iterator::Signals};
use std::thread;
use std::time::Duration;

use serde_json::json;

#[allow(dead_code)]
fn write_json(pid: Pid, cmd: Vec<String>, memory: MemoryInfo, cpuinfo: ProcessCpuTimes) {
    let obj = json!({
        "@datetime": Local::now().timestamp_nanos_opt(),
        "pid": pid,
        "user_ns": cpuinfo.user().as_nanos(),
        "system_ns": cpuinfo.system().as_nanos(),
        "busy_ns": cpuinfo.busy().as_nanos(),
        "rss": memory.rss(),
        "vms": memory.vms(),
        "shared": memory.shared(),
        "cmd": cmd.first(),
        "full_cmd": cmd,
    });
    println!("{}", obj);
}

fn write_csv(pid: Pid, cmd: Vec<String>, memory: MemoryInfo, cpuinfo: ProcessCpuTimes) {
    println!(
        "{}|{}|{}|{}|{}|{}|{}|{}|{:?}|{:?}",
        Local::now(),
        pid,
        cpuinfo.user().as_nanos(),
        cpuinfo.system().as_nanos(),
        cpuinfo.busy().as_nanos(),
        memory.rss(),
        memory.vms(),
        memory.shared(),
        cmd.first().unwrap(),
        cmd
    );
}

fn print_current_procs() {
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

        if uid != 1001 {
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

        let memory: MemoryInfo = match proc_info.memory_info() {
            Ok(m) => m,
            Err(_) => {
                continue;
            }
        };
        let cpuinfo: ProcessCpuTimes = match proc_info.cpu_times() {
            Ok(c) => c,
            Err(_) => {
                continue;
            }
        };
        write_csv(pid, cmd, memory, cpuinfo);
    }
}

fn main() {
    let _cpus = psutil::cpu::cpu_count_physical();

    let mut signals = Signals::new(&[SIGINT]).expect("Signal Error");
    // println!("@datetime|pid|user_ns|system_ns|busy_ns|rss|vms|shared|cmd|cmd_full");
    // thread::spawn(move || loop {
    //     print_current_procs();
    //     thread::sleep(Duration::from_millis(100));
    // });

    thread::spawn(move || {
        pagurus::get_proc_maps();
    });

    for sig in signals.forever() {
        match sig {
            2 => {
                eprintln!("Killed with ^C");
                exit(0)
            }
            _ => exit(0),
        }
    }
}
