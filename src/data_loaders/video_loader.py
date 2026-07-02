from pathlib import Path
import torch
from pydub import AudioSegment
from pyannote.audio import Pipeline
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from dotenv import load_dotenv
from transformers import WhisperProcessor

load_dotenv() 

hf_token = os.getenv(HUGGING_FACE_HUB_TOKEN)
asr_model = os.getenv("ASR_MODEL_NAME")
diarization_model = os.getenv("DIARIZATION_MODEL_NAME")

def transcribe_video_clip(video_path: str, diarize: bool = False):
    # 1. Validate inputs and formats
    if not video_path or not Path(video_path).is_file():
        print("Invalid file path provided.")
        return None
        
    ext = Path(video_path).suffix.lower().replace('.', '')
    if ext not in ['mp4']:
        print(f"Unsupported format: {ext}")
        return None

    # Determine hardware acceleration
    device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    print(f"Running inference on device: {device}")

    content = {'source': 'video', 'filename': video_path, 'content', [], 'diarized': False}

    # 2. Extract and format the audio stream using pydub
    print("Extracting audio stream from video...")
    audio = AudioSegment.from_file(video_path, format=ext)
    # Whisper requires 16000Hz mono audio data
    audio = audio.set_frame_rate(16000).set_channels(1)

    # 3. Initialize models
    print("Loading PyAnnote & Hugging Face Whisper models...")
    pipeline = Pipeline.from_pretrained(diarization_model, use_auth_token=hf_token)
    
    # Send PyAnnote pipeline to GPU if using CUDA
    if device == "cuda":
        pipeline.to(torch.device("cuda"))
        
    processor = WhisperProcessor.from_pretrained(asr_model)
    model = WhisperForConditionalGeneration.from_pretrained(asr_model).to(device)
    model.config.forced_decoder_ids = None

    # 4. Execute Diarization
    print("Analyzing speaker timelines...")
    diarization_segments = pipeline(video_path)

    transcript_output = {"transcript": []}

    if not diarize:

        data_dict = {"audio": [video_path]}
        ds = Dataset.from_dict(data_dict)
        ds = ds.cast_column("audio", Audio(sampling_rate=16000, mono=True))
        sample = ds[0]["audio"]
        processor = WhisperProcessor.from_pretrained(asr_model)
        input_features = processor(
            sample["array"],               # <--- This is the correct numerical array
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

    # 5. Process segments sequentially
    print("Processing and transcribing video segments...")
    for turn, _, speaker in diarization_segments.itertracks(yield_label=True):
        # Convert seconds to milliseconds for pydub slicing
        start_ms = int(turn.start * 1000)
        end_ms = int(turn.end * 1000)
        
        # Ignore micro-noises under half a second
        if (end_ms - start_ms) < 500:
            continue

        # Extract the audio slice for the specific speaker
        audio_slice = audio[start_ms:end_ms]
        
        # Format binary array into normalized PyTorch Float32 tensors
        raw_samples = audio_slice.get_array_of_samples()
        numpy_samples = torch.tensor(raw_samples, dtype=torch.float32) / 32768.0

        # Run Whisper inference
        input_features = processor(
            numpy_samples.numpy(), 
            sampling_rate=16000, 
            return_tensors="pt"
        ).input_features.to(device)

        with torch.no_grad():
            predicted_ids = model.generate(input_features)
            
        transcription_list = processor.batch_decode(predicted_ids, skip_special_tokens=True)
        text = transcription_list[0].strip() if transcription_list else ""

        if text:
            # Format visual time markers for easy reading
            m_start, s_start = divmod(int(turn.start), 60)
            m_end, s_end = divmod(int(turn.end), 60)
            time_stamp = f"{m_start:02d}:{s_start:02d} -> {m_end:02d}:{s_end:02d}"
            
            line = f"[{time_stamp}] {speaker}: {text}"
            transcript_output["transcript"].append(line)
        
    content['content'] = transcribe_output['transcript']

    return transcript_output

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Audio File Loader.')
    parser.add_argument('-f', '--file', required=True, help='Full path filename to load.')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output.')

    args = parser.parse_args()
    video_path = args.file

    results = transcribe_video_clip(
        video_path="presentation.mp4",
        asr_model="openai/whisper-base",
        diarization_model="pyannote/speaker-diarization-3.1"
    )

    pdf.set_trace()
