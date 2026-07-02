import pdb
import argparse
import torch
from pathlib import Path
from pydub import AudioSegment
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from pyannote.audio import Pipeline
from dotenv import load_dotenv

load_dotenv() 

diarization_model_name = os.getenv("DIARIZATION_MODEL_NAME")
asr_model_name = os.getenv("ASR_MODEL_NAME")
hf_token = os.getenv(HUGGING_FACE_HUB_TOKEN)

    return diarization

def load_file(filename: str = "", 
    diarize: bool = False, 
    verbose: bool = True
) -> dict:
    if not filename:
        print(f"Filename cannot be empty.")
    elif not Path(filename).is_file():
        print("The file does not exist.")
    else:
        content = {'source': 'audio', 'filename': filename, 'content', [], 'diarized': False}
        ext = Path(filename).suffix

        # Load mp4 txt file
        if not ext in ['mp3','mp4','wav']:
            print(f"Audio format - {} - not recognized.")
        else:
            # Transcribe filename with Auto Speech Recognition (ASR) Model
            processor = WhisperProcessor.from_pretrained(model=asr_model_name)
            model = WhisperForConditionalGeneration.from_pretrained(model=asr_model_name)
            model.config.forced_decoder_ids = None

            if diarize:
                audio = AudioSegment.from_file(filename).set_frame_rate(16000).set_channels(1)
                print("Transcribing segments...")
                for turn, _, speaker in diarization.itertracks(yield_label=True):
                    # Convert pyannote seconds (floats) to pydub milliseconds (ints)
                    start_ms = int(turn.start * 1000)
                    end_ms = int(turn.end * 1000)
                    
                    # Skip segments shorter than 0.5 seconds to avoid Whisper processing noise
                    if (end_ms - start_ms) < 500:
                        continue

                    # Slice out just this speaker's segment
                    audio_segment = audio[start_ms:end_ms]
                    
                    # Convert the raw sliced audio array to the format Whisper expects
                    # (float32 numpy array normalized between -1.0 and 1.0)
                    raw_samples = audio_segment.get_array_of_samples()
                    numpy_samples = torch.tensor(raw_samples, dtype=torch.float32) / 32768.0

                    # Feed the sample slice to the processor
                    input_features = processor(
                        numpy_samples.numpy(), 
                        sampling_rate=16000, 
                        return_tensors="pt"
                    ).input_features

                    # Generate tokens and decode
                    predicted_ids = model.generate(input_features)
                    transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]

                    # Save result with metadata
                    if transcription.strip():
                        formatted_line = f"[{turn.start:.2f}s - {turn.end:.2f}s] {speaker}: {transcription.strip()}"
                        content['content'].append(formatted_line)
                        # print(formatted_line)
                content['diarized'] = True

            else:
                ds = load_dataset(filename, "clean", split="validation")
                sample = ds[0]["audio"]
                input_features = processor(
                    filename, 
                    sampling_rate=sample["sampling_rate"], 
                    return_tensors="pt"
                    ).input_features 

                # generate token ids
                predicted_ids = model.generate(input_features)
                # decode token ids to text
                content['content'].append(
                    processor.batch_decode(
                        predicted_ids, skip_special_tokens=True
                    )
                )

        return content

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Audio File Loader.')
    parser.add_argument('-f', '--file', required=True, help='Full path filename to load.')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output.')

    args = parser.parse_args()

    # Extract content dictionary
    content = load_file(verbose = args.verbose)
    pdf.set_trace()