import argparse


def parse_ai_service_arguments():
    """
    parses user input for music generation.
    """
    parser = argparse.ArgumentParser(description='Argument Parse for Mamba Magenta Models.')
    parser.add_argument('-t', '--temperature', type=float, default=1.0,
                        help='Temperature for softmax for music generation.')
    parser.add_argument('-l', '--length', type=float, default=1.0,
                        help='Length of sequence, between 0 and 1.')
    parser.add_argument('-a', '--artist', type=str, default='music_transformer',
                        help='Type of model')
    parser.add_argument('-g', '--genre', type=str, default='wild_card',
                        help='Specified genre')
    parser.add_argument('-n', '--numgenerations', type=int, default=1,
                        help='Num of musical piece generations')

    return parser.parse_args()
