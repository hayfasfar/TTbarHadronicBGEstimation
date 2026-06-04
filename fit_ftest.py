#!/usr/bin/env python3
import argparse
import concurrent.futures
import os
import subprocess
import sys
import threading


DEFAULT_TFS = ['0x0', '0x1', '0x2', '1x0', '1x1', '1x2', '2x1', '2x2']
DEFAULT_REGIONS = ['cen', 'fwd']

RUN2_INPUT = '/eos/home-h/hrejebsf/2Dalphabet_files/combined_run2_files/'
INPUT_2024 = '/eos/user/a/amandal/ttbarhad_root_files/2dAlphabetInputs'


def signal_name(signal):
    return signal if signal.startswith('signal') else 'signal' + signal


def parse_args():
    parser = argparse.ArgumentParser(
        description='Run ttbar.py once per transfer-function candidate for F-tests.'
    )
    parser.add_argument(
        'years',
        nargs='*',
        help='Years/eras to run. Backward-compatible positional form, e.g. 2017. Defaults depend on --preset.',
    )
    parser.add_argument(
        '--preset',
        choices=['run2', '2024'],
        default='run2',
        help='Convenience defaults. run2 preserves the old script defaults; 2024 uses the 2024 EOS input and RSGluon4000.',
    )
    parser.add_argument('--regions', nargs='+', default=DEFAULT_REGIONS, help='Region prefixes to run.')
    parser.add_argument('--tfs', nargs='+', default=DEFAULT_TFS, help='Transfer-function forms to test.')
    parser.add_argument('--input', default=None, help='Input ROOT path passed to ttbar.py.')
    parser.add_argument('--output-base', default='ftest', help='Base output directory for F-test work areas.')
    parser.add_argument('--scenario', default='RSGluon', help='Scenario passed to ttbar.py --senario.')
    parser.add_argument('--signal', default=None, help='Signal passed to ttbar.py --signal.')
    parser.add_argument('--python', default=sys.executable, help='Python executable used to run ttbar.py.')
    parser.add_argument('--jobs', type=int, default=1, help='Number of transfer-function fits to run concurrently.')
    parser.add_argument('--keep-going', action='store_true', help='Continue scanning TFs after a failed fit.')
    parser.add_argument('--dry-run', action='store_true', help='Print commands without running them.')
    return parser.parse_args()


def defaults_for(args):
    if args.preset == '2024':
        years = args.years or ['2024']
        input_path = args.input or INPUT_2024
        signal = args.signal or 'RSGluon4000'
    else:
        years = args.years or ['2016', '2017', '2018', 'Comb']
        input_path = args.input or RUN2_INPUT
        signal = args.signal or 'RSGluon2000'

    return years, input_path, signal_name(signal)


def make_command(args, category, tf, input_path, output_dir, signal):
    return [
        args.python,
        '-u',
        'ttbar.py',
        '--cat',
        category,
        '--tf',
        tf,
        '--study',
        'ftest',
        '--senario',
        args.scenario,
        '--input',
        input_path,
        '--output',
        output_dir,
        '--signal',
        signal,
    ]


def run_command(command, log_path, label, dry_run=False, print_lock=None):
    print_lock = print_lock or threading.Lock()
    command_text = ' '.join(command)

    with print_lock:
        print('[{}] {}'.format(label, command_text))

    if dry_run:
        return 0

    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, 'w') as log_file:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
        )

        for line in process.stdout:
            log_file.write(line)
            log_file.flush()
            with print_lock:
                print('[{}] {}'.format(label, line), end='')

        return process.wait()


def build_tasks(args, years, input_path, signal):
    tasks = []
    for year in years:
        for region in args.regions:
            category = '{}{}'.format(region, year)
            output_dir = os.path.join(args.output_base, str(year), region)

            for tf in args.tfs:
                log_path = os.path.join(output_dir, 'output_{}_{}.log'.format(category, tf))
                label = '{}:{}'.format(category, tf)
                command = make_command(args, category, tf, input_path, output_dir, signal)
                tasks.append((command, log_path, label))

    return tasks


def main():
    args = parse_args()
    years, input_path, signal = defaults_for(args)
    tasks = build_tasks(args, years, input_path, signal)
    print_lock = threading.Lock()

    print('Years: {}'.format(', '.join(years)))
    print('Regions: {}'.format(', '.join(args.regions)))
    print('Transfer functions: {}'.format(', '.join(args.tfs)))
    print('Signal: {}'.format(signal))
    print('Input: {}'.format(input_path))
    print('Output base: {}'.format(args.output_base))
    print('Concurrent jobs: {}'.format(args.jobs))

    if args.jobs <= 1:
        failures = []
        for command, log_path, label in tasks:
            code = run_command(command, log_path, label, args.dry_run, print_lock)
            if code != 0:
                failures.append((label, code))
                if not args.keep_going:
                    raise SystemExit('[{}] failed with exit code {}'.format(label, code))
        if failures:
            for label, code in failures:
                print('[{}] failed with exit code {}'.format(label, code))
            raise SystemExit(1)
        return

    failures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as executor:
        future_map = {
            executor.submit(run_command, command, log_path, label, args.dry_run, print_lock): label
            for command, log_path, label in tasks
        }
        for future in concurrent.futures.as_completed(future_map):
            label = future_map[future]
            code = future.result()
            if code != 0:
                failures.append((label, code))

    if failures:
        for label, code in failures:
            print('[{}] failed with exit code {}'.format(label, code))
        raise SystemExit(1)


if __name__ == '__main__':
    main()
