import magenta.music as mm
import magenta
import tensorflow
from magenta.music.protobuf import music_pb2
from midi2audio import FluidSynth


twinkle_twinkle = music_pb2.NoteSequence()

# Add the notes to the sequence.
# we can specify midi pitch, times, and speed (dynamics)
twinkle_twinkle.notes.add(pitch=60, start_time=0.0, end_time=0.5, velocity=80)
twinkle_twinkle.notes.add(pitch=60, start_time=0.5, end_time=1.0, velocity=80)
twinkle_twinkle.notes.add(pitch=67, start_time=1.0, end_time=1.5, velocity=80)
twinkle_twinkle.notes.add(pitch=67, start_time=1.5, end_time=2.0, velocity=80)
twinkle_twinkle.notes.add(pitch=69, start_time=2.0, end_time=2.5, velocity=80)
twinkle_twinkle.notes.add(pitch=69, start_time=2.5, end_time=3.0, velocity=80)
twinkle_twinkle.notes.add(pitch=67, start_time=3.0, end_time=4.0, velocity=80)
twinkle_twinkle.notes.add(pitch=65, start_time=4.0, end_time=4.5, velocity=80)
twinkle_twinkle.notes.add(pitch=65, start_time=4.5, end_time=5.0, velocity=80)
twinkle_twinkle.notes.add(pitch=64, start_time=5.0, end_time=5.5, velocity=80)
twinkle_twinkle.notes.add(pitch=64, start_time=5.5, end_time=6.0, velocity=80)
twinkle_twinkle.notes.add(pitch=62, start_time=6.0, end_time=6.5, velocity=80)
twinkle_twinkle.notes.add(pitch=62, start_time=6.5, end_time=7.0, velocity=80)
twinkle_twinkle.notes.add(pitch=60, start_time=7.0, end_time=8.0, velocity=80) 
twinkle_twinkle.total_time = 8

# 60 bpm!
twinkle_twinkle.tempos.add(qpm=60)
mm.sequence_proto_to_midi_file(twinkle_twinkle, 'twinkle.mid')
# This is a colab utility method that visualizes a NoteSequence.
fs = FluidSynth()

fs.midi_to_audio('twinkle.mid', "twinkle.mp3")

# This is a colab utility method that plays a NoteSequence.
# mm.play_sequence(twinkle_twinkle,synth=mm.fluidsynth)



# mm.play_sequence(teapot,synth=mm.synthesize)