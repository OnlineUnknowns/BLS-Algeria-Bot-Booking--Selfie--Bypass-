NotFoundError:
        print(Fore.RED + "Input file not found. Generate records first or provide a file path." + Style.RESET_ALL)
        return
    # For demonstration, we'll attempt N random records
    sample = random.sample(lines, min(args.attempts, len(lines)))
    for ln in sample:
        parts = ln.split('|')
        code, expiry, ref, bal = parts[0], parts[1], parts[2], parts[3].lstrip('$')
        record = BLSRecord(code, expiry, ref, int(bal))
        print(Fore.MAGENTA + f"\n=== Attempting booking for {record.code} (simulated) ===" + Style.RESET_ALL)
        if REAL_INTEGRATION_ENABLED and args.use_real:
            try:
                resp = real_book_request(record, user_data={})
                print(Fore.GREEN + f"Real integration response: {resp}" + Style.RESET_ALL)
            except Exception as e:
                print(Fore.RED + f"Real integration failed or disabled: {e}" + Style.RESET_ALL)
        else:
            resp = real_book_request_simulation_placeholder(record, user_data={})
            if resp.get("status") == "success":
                print(Fore.GREEN + f"Simulated booking success: appointment id {resp.get('appointment_id')}" + Style.RESET_ALL)
                with open(VALID_OUTPUT_FILE, 'a', encoding='utf-8') as vf:
                    vf.write(f"BOOKED_SIM|{resp.get('appointment_id')}|{record}\n")
            else:
                print(Fore.YELLOW + f"Simulated booking failed: {resp.get('message')}" + Style.RESET_ALL)

# ---------------------------
# CLI argument parsing
# ---------------------------
def build_parser():
    parser = argparse.ArgumentParser(prog=APP_NAME, description="BLS Algeria Booking Simulator & Safe Integration Template")
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Generate fake BLS records (simulation).")
    gen.add_argument("--count", "-c", type=int, default=200, help="How many records to generate.")
    gen.add_argument("--start-year", type=int, default=2025, help="Start year for expiries.")
    gen.set_defaults(func=handle_generate)

    check = sub.add_parser("simulate-check", help="Simulate checking generated records with multi-threading.")
    check.add_argument("--input", "-i", type=str, default=None, help="Input file to read records from (default: generated file).")
    check.add_argument("--threads", "-t", type=int, default=8, help="Number of worker threads.")
    check.set_defaults(func=handle_simulate_check)

    book = sub.add_parser("attempt-book", help="Attempt bookings (simulation).")
    book.add_argument("--input", "-i", type=str, default=None, help="Input file to read records from.")
    book.add_argument("--attempts", "-a", type=int, default=5, help="Number of random attempts to simulate.")
    book.add_argument("--use-real", action="store_true", help="Try to use real integration (only if REAL_INTEGRATION_ENABLED=True and real_book_request is implemented).")
    book.set_defaults(func=handle_attempt_book)

    return parser

# ---------------------------
# Main entry point
# ---------------------------
def main():
    banner()
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as exc:
        logging.exception("Unhandled exception: %s", exc)
        print(Fore.RED + "An error occurred. See log file for details." + Style.RESET_ALL)

if __name__ == "__main__":
    main()
