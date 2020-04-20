import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description='Argument Parse for Mamba Magenta Models.')
    parser.add_argument('-m', '--model', type=str, default='melody-rnn',
                        help='Available networks. Choose from:')
    parser.add_argument('-n', '--notes', type=str, default='60 61 62 63',
                        help='Please provide a list of midi notes.')
    parser.add_argument('-lc', '--load_config', type=bool, default=False,
                        help='Whether the config is desired to be used.')
    parser.add_argument('-cfd', '--config_dir', type=str, default='config',
                        help='Config directory')
    parser.add_argument('-cff', '--config_file', type=str, default='sequence.yaml',
                        help='Config file for a note sequence.')

    return parser.parse_args()