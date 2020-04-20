from mamba_magenta_model import MambaMagentaModel
import os

from magenta.models.melody_rnn import melody_rnn_sequence_generator
from magenta.models.shared import sequence_generator_bundle
from magenta.music.protobuf import generator_pb2
from magenta.music.protobuf import music_pb2
from utils import parse_arguments
import magenta.music as mm
from midi2audio import FluidSynth


class MelodyRNN(MambaMagentaModel):
    def __init__(self, args):
        super(MelodyRNN, self).__init__(args)
        self.get_model()
        self.initialize()

    def get_model(self, model_string="basic"):
        if model_string not in ["basic", "mono", "lookback", "attention"]:
            raise ValueError("Wrong model string provided. Choose basic, mono, lookback, or attention.")
        else:
            # models folder already exists with this repository.
            os.chdir("models")
            if os.path.isfile(f"{model_string}_rnn.mag"):
                print("mag file already exists!")
            else:
                os.system(f"wget http://download.magenta.tensorflow.org/models/{model_string}_rnn.mag")
            self.model_name = f"{model_string}_rnn"
            os.chdir("..")

    def initialize(self):
        print("Initializing Melody RNN...")
        bundle = sequence_generator_bundle.read_bundle_file(os.path.join(os.getcwd(), "models", f"{self.model_name}.mag"))
        generator_map = melody_rnn_sequence_generator.get_generator_map()
        self.melody_rnn = generator_map[self.model_name](checkpoint=None, bundle=bundle)

        self.melody_rnn.initialize()

    def generate(self):
        input_sequence = self.sequence
        num_steps = 128  # change this for shorter or longer sequences
        temperature = 1.0
        # Set the start time to begin on the next step after the last note ends.
        last_end_time = (max(n.end_time for n in input_sequence.notes)
                  if input_sequence.notes else 0)
        qpm = input_sequence.tempos[0].qpm
        seconds_per_step = 60.0 / qpm / self.melody_rnn.steps_per_quarter

        total_seconds = num_steps * seconds_per_step

        generator_options = generator_pb2.GeneratorOptions()
        generator_options.args['temperature'].float_value = temperature

        generate_section = generator_options.generate_sections.add(
            start_time=last_end_time + seconds_per_step,
            end_time=total_seconds)

        sequence = self.melody_rnn.generate(input_sequence, generator_options)
        mm.sequence_proto_to_midi_file(sequence, 'songs/output.mid')
        fs = FluidSynth()

        fs.midi_to_audio('songs/output.mid', 'songs/output.mp3')

    def __call__(self, x):
        # generate code
        pass




class Performance(MambaMagentaModel):
    def __init__(self, args):
        super(MelodyRNN, self).__init__(args)
        self.get_model()
        self.initialize()

if __name__ == '__main__':
    args = parse_arguments()
    model = MelodyRNN(args)
    model()
