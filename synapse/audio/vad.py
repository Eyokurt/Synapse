import torch

class SileroVAD:
    """
    Voice Activity Detection using Silero VAD.
    Requires torch and torchaudio to be installed.
    """
    def __init__(self, sample_rate: int = 16000, threshold: float = 0.5):
        self.sample_rate = sample_rate
        self.threshold = threshold
        
        try:
            import torch
        except ImportError:
            raise ImportError(
                "PyTorch is required for Silero VAD. "
                "Install it with `uv add centrumlib[audio]` or `pip install torch torchaudio`"
            )

        print("Loading Silero VAD model (may take a moment the first time)...")
        # Load the model from torch hub
        self.model, utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            trust_repo=True
        )
        self.get_speech_timestamps, _, _, self.VADIterator, _ = utils
        # Use VADIterator for robust start/end endpointing if needed, 
        # but for simple chunk probability we can just use the model directly.
        self.vad_iterator = self.VADIterator(self.model, sampling_rate=self.sample_rate)

    def is_speech(self, audio_chunk: torch.Tensor) -> bool:
        """
        Calculates the probability of speech in a given raw audio chunk.
        audio_chunk should be a 1D torch.Tensor of floats.
        """
        # The model expects a batch dimension: (batch, samples)
        if audio_chunk.dim() == 1:
            audio_chunk = audio_chunk.unsqueeze(0)
            
        with torch.no_grad():
            confidence = self.model(audio_chunk, self.sample_rate).item()
            
        return confidence >= self.threshold

    def process_stream_chunk(self, audio_chunk: torch.Tensor):
        """
        Advanced iterator that tracks state and returns a dict when speech starts or ends.
        Returns:
            {'start': int} if speech started
            {'end': int} if speech ended
            None if no change in state
        """
        return self.vad_iterator(audio_chunk, return_seconds=True)
