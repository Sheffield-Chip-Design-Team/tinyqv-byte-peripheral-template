import argparse
import subprocess
import os

def get_coverage(srcs, top_module, hier_path, cover_types="line,comb,toggle",vcd="tb.vcd", seed="", cov_dir="cov"):

    cmd = [
        "covered", "score", 
    ]
    for src in srcs:
        cmd.extend(["-v", src])
    
    cmd.extend([
        "-t", top_module,
        "-i", hier_path,
        "-vcd", vcd,
        "-o", f"{cov_dir}/cov_{seed}.cdd"
    ])
    print(f"Getting coverage for run: {seed} command:")
    print("Running command:", " ".join(cmd))
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def merge_coverage(work_dir, merged_cov_file):

    cdd_files = [f for f in os.listdir(work_dir) if f.endswith('.cdd')]
    temp_stash = f"{work_dir}/temp_stash.ccd"

    if merged_cov_file in cdd_files:
       
        src_path = os.path.join(work_dir, merged_cov_file)
        dst_path = os.path.join(work_dir, "temp_stash.ccd")

        with open(src_path, "rb") as src, open(dst_path, "wb") as dst:
            dst.write(src.read())
        cdd_files.remove(merged_cov_file)
    print("Found .cdd files:", cdd_files)

    cmd = [
        "covered", "merge",
        "-d", work_dir,
    ]

    for ccd in cdd_files:
        cmd.extend([f"{work_dir}/{ccd}"])

    if temp_stash in cdd_files:
        cmd.extend([f"{work_dir}/temp_stash.ccd"])

    cmd.extend(["-o",f"{work_dir}/{merged_cov_file}"])

    print(f"Merging coverage...")
    print("Running command:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    
    print(f"Cleaning work folder")
    clean_cov_dir(work_dir, f"{work_dir}/{merged_cov_file}")


def clean_cov_dir(cov_dir, exceptions=[]):
    print(f"Cleaning coverage directory: {cov_dir}")
    cdd_files = [f for f in os.listdir(cov_dir) if f.endswith('.cdd')]
    vcd_files = [f for f in os.listdir(cov_dir) if f.endswith('.vcd')]

    for ccd in cdd_files:
        if ccd not in exceptions:
            os.remove(f"{cov_dir}/{ccd}")

    for vcd in vcd_files:
        if vcd not in exceptions:
            os.remove(f"{cov_dir}/{vcd}")

def report_coverage(cov_dir, cov_file, verbose):
    cmd = ["covered", "report"]
    if verbose:
        cmd.extend(["-d", "v"])
    cmd.append(f"{cov_dir}/{cov_file}")

    with open("coverage.log", "w") as log_file:
        process = subprocess.run(cmd, stdout=log_file, stderr=subprocess.STDOUT)
