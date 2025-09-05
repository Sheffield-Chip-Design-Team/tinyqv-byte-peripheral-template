import subprocess
import random
import os
import argparse
from datetime import datetime
import concurrent.futures
from tqdm import tqdm
from coverage import get_coverage, merge_coverage, clean_cov_dir, report_coverage

def run_test(runs=1, width=5):
    # find all directories with a test Makefile inside
    folders_with_makefile = []
    for root, _, files in os.walk("."):
        if "Makefile" in files or "makefile" in files:
            folders_with_makefile.append(root)
    if '.' in folders_with_makefile:
        folders_with_makefile.remove('.')
    print(f"Test directories: {folders_with_makefile}")

    def run_make(folder, run_idx, position):
        module_name = os.path.basename(os.path.abspath(folder))
        desc = f"{module_name} run {run_idx}"
        log_header = f"\n=== {desc} ===\n"

        # Start a separate progress bar for this task
        with tqdm(total=1, desc=desc, position=position, leave=True) as pbar:
            result = subprocess.run(
                ["make"],
                cwd=folder,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            pbar.update(1)

        return log_header + result.stdout

    # Create a flat list of all tasks
    tasks = []
    for folder in folders_with_makefile:
        for run_idx in range(1, runs + 1):
            tasks.append((folder, run_idx))
    print(f"Total tasks: {len(tasks)}")
    print(f"Running {min(width, len(tasks))} batches at a time.")

    logs = [None] * len(tasks)
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(width, len(tasks))) as executor:
        future_to_idx = {}
        for idx, (folder, run_idx) in enumerate(tasks):
            position = idx % width  # position for tqdm to avoid overlapping bars
            future = executor.submit(run_make, folder, run_idx, position)
            future_to_idx[future] = idx

        for future in concurrent.futures.as_completed(future_to_idx):
            idx = future_to_idx[future]
            logs[idx] = future.result()

    # Write all logs to the master log file in order
    master_log_filename = "latest_regress.log"
    with open(master_log_filename, "a") as master_log:
        master_log.write(f"=== Regression Log ===\n")
        master_log.write(f"Timestamp: {datetime.now().isoformat()}\n")
        master_log.write(f"Test directories: {folders_with_makefile}\n")
        master_log.write(f"Repetitions per directory: {runs}\n")
        master_log.write(f"Threads used: {min(width, len(tasks))}\n")
        master_log.write(f"Total tasks: {len(tasks)}\n")
        master_log.write(f"========================\n\n")
        for log in logs:
            master_log.write(log)

def main():
    parser = argparse.ArgumentParser(description="Run make in folders with Makefile.")
    parser.add_argument("-runs", type=int, default=1, help="Number of repetitions per folder")
    parser.add_argument("-width", type=int, default=4, help="Number of threads to use")
    args = parser.parse_args()
    run_test(runs=args.runs, width=args.width)

if __name__ == "__main__":import subprocess
import os
import argparse
from datetime import datetime
import concurrent.futures
from tqdm import tqdm

def run_test(runs=1, width=5, clean=False, cov_dir="cov"):
    # Find all directories with a test Makefile inside
    folders_with_makefile = []
    for root, _, files in os.walk("./.."):
        if "Makefile" in files or "makefile" in files:
            folders_with_makefile.append(root)
    if '.' in folders_with_makefile:
        folders_with_makefile.remove('.')
    print(f"Test directories: {folders_with_makefile}")

    # Create a flat list of all tasks
    tasks = []
    for folder in folders_with_makefile:
        for run_idx in range(1, runs + 1):
            tasks.append((folder, run_idx))
    print(f"Total tasks: {len(tasks)}")

    # Determine number of batches
    num_batches = min(width, len(tasks))
    print(f"Running {num_batches} tests concurrently.")

    logs = [None] * len(tasks)
    
    # Write all logs to the master log file in order
    master_log_filename = "latest_regress.log"
    with open(master_log_filename, "a") as master_log:
        master_log.write(f"=== Regression Log ===\n")
        master_log.write(f"Timestamp: {datetime.now().isoformat()}\n")
        master_log.write(f"Test directories: {folders_with_makefile}\n")
        master_log.write(f"Repetitions per directory: {runs}\n")
        master_log.write(f"Threads used: {num_batches}\n")
        master_log.write(f"Total tasks: {len(tasks)}\n")
        master_log.write(f"========================\n\n")
        

    def run_make(folder, run_idx, work_dir):

        # Copy environment and set RANDOM_SEED
        seed = random.randint(10**9, 10**10 - 1)
        module_name = os.path.basename(os.path.abspath(folder))
        desc = f"[{module_name} run {run_idx}] Using seed {seed}"
        log_header = f"\n=== {desc} ===\n"
        vcd_path = f"{work_dir}/tb_{seed}.vcd"

        cmd = [
        "make",
        f"RANDOM_SEED={seed}",
        f"VCD_PATH={vcd_path}"
]
        result = subprocess.run(
            cmd,
            cwd=folder,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        src_dir = "./../src"
        srcs = [f"{src_dir}/FPGA_NESReciever.v" , f"{src_dir}/peripheral.v" ]

        get_coverage(srcs=srcs, vcd=vcd_path, top_module="tqvp_nes_snes_controller", hier_path="tb.test_harness.user_peripheral", seed=seed)

          #  result.stdout += f"\n--- Coverage Output ---\n{coverage_result.stdout}\n"
        return log_header + result.stdout, desc

    # Run tasks in batches
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_batches) as executor:
        for i in range(0, len(tasks), num_batches):
            batch_tasks = tasks[i:i+num_batches]
            # Print which tasks are running in this batch
            batch_descs = [f"{os.path.basename(os.path.abspath(folder))} run {run_idx}" for folder, run_idx in batch_tasks]
            print(f"Running test batch {i//num_batches + 1}: {batch_descs}")

            futures = {
                executor.submit(run_make, folder, run_idx, cov_dir): idx
                for idx, (folder, run_idx) in enumerate(batch_tasks, start=i)
            }

            # One progress bar for this batch
            with tqdm(total=len(batch_tasks), desc=f"Batch {i//num_batches + 1}", leave=True) as pbar:
                for future in concurrent.futures.as_completed(futures):
                    idx = futures[future]
                    result_log, test_desc = future.result()
                    logs[idx] = result_log
                    # Update progress bar with the current test
                    pbar.set_postfix_str(test_desc)
                    pbar.update(1)

            print(f"Batch {i//num_batches + 1} finished!")


    # write all logs to the master regression log
    with open(master_log_filename, "a") as master_log:
         for log in logs:
            master_log.write(log)

    print("All tests finished!")
    merge_coverage(work_dir="cov", merged_cov_file="merged.cdd")

def main():
    latest_log_path = "latest_regress.log"
    if os.path.exists(latest_log_path):
        os.remove(latest_log_path)

    parser = argparse.ArgumentParser(description="Run make in folders with Makefile.")
    parser.add_argument("-runs", type=int, default=1, help="Number of repetitions per folder")
    parser.add_argument("-width", type=int, default=4, help="Number of threads to use")
    parser.add_argument("-clean", action="store_true", help="Clean before running tests")
    parser.add_argument("-verbose", action="store_true", help="Enable verbose coverage output")

    args = parser.parse_args()

    cov_dir = "cov"
    os.makedirs(cov_dir, exist_ok=True)
   
    if args.clean:
        print("Cleaning cov directory before tests starts")
        clean_cov_dir(cov_dir=cov_dir)

    run_test(runs=args.runs, width=args.width, cov_dir=cov_dir)

    report_coverage(cov_dir=cov_dir, cov_file="merged.cdd", verbose=args.verbose)

if __name__ == "__main__":
    main()