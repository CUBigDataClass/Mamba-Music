from mamba_magenta_model import MambaMagentaModel
import os

from magenta.models.melody_rnn import melody_rnn_sequence_generator
from magenta.models.shared import sequence_generator_bundle
from magenta.music.protobuf import generator_pb2
from magenta.music.protobuf import music_pb2
from utils import parse_arguments


class MelodyRNN(MambaMagentaModel):
    def __init__(self, args):
        super(MelodyRNN, self).__init__(args)

    def get_model(self, model_string="basic"):
        if model_string not in ["basic", "mono", "lookback", "attention"]:
            raise ValueError("Wrong model string provided. Choose basic, mono, lookback, or attention.")
        else:
            os.chdir("models")
            if os.path.isfile(f"{model_string}_rnn.mag"):
                print("mag file already exists!")
            else:
                os.system(f"wget http://download.magenta.tensorflow.org/models/{model_string}_rnn.mag")
            self.model_name = f"{model_string}_rnn"
    def __call__(self):
        print("Initializing Melody RNN...")
        bundle = sequence_generator_bundle.read_bundle_file(os.path.join("models", f"{self.model_name}.mag"))
        generator_map = melody_rnn_sequence_generator.get_generator_map()
        melody_rnn = generator_map[self.model_name](checkpoint=None, bundle=bundle)

        melody_rnn.initialize()

if __name__ == '__main__':
    args = parse_arguments()
    m = MelodyRNN(args)
