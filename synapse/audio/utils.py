import numpy as np

def resample_audio(data: np.ndarray, target_len: int) -> np.ndarray:
    """
    Resamples a 1D audio numpy array to exactly target_len using linear interpolation.
    This guarantees that models like Silero VAD receive exactly the frame size they expect (e.g. 512),
    preventing STFT window failures that cause 0.1% confidence.
    """
    if len(data) == target_len:
        return data
        
    x = np.arange(len(data))
    x_new = np.linspace(0, len(data) - 1, target_len)
    
    resampled = np.interp(x_new, x, data).astype(np.float32)
    return resampled
