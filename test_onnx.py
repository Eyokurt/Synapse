import onnxruntime
import numpy as np
import httpx
import os

model_path = "silero_vad.onnx"
if not os.path.exists(model_path):
    print("Downloading ONNX model...")
    url = "https://github.com/snakers4/silero-vad/raw/master/src/silero_vad/data/silero_vad.onnx"
    response = httpx.get(url, follow_redirects=True)
    with open(model_path, "wb") as f:
        f.write(response.content)

sess = onnxruntime.InferenceSession(model_path)
inputs = [i.name for i in sess.get_inputs()]
print("Required inputs:", inputs)

input_data = np.zeros((1, 512), dtype=np.float32)
sr_data = np.array([16000], dtype=np.int64)
state_data = np.zeros((2, 1, 128), dtype=np.float32)

out = sess.run(None, {"input": input_data, "sr": sr_data, "state": state_data})
print("Outputs:", [o.shape for o in out])
print("Probability:", out[0][0][0])
