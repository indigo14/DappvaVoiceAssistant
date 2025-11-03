**From gpt-5**
Got it—WSL-first it is. Here’s a compact **“choose-one”** playbook for **TTS in WSL2** on your **GTX 970 (Maxwell)**. I’ll show the **CUDA route** (best case), plus a **CPU fallback** that still lives entirely in WSL.

---

# WSL-first Local TTS (Windows 10 + WSL2, GTX 970)

## Reality check (1 minute)

Maxwell GPUs are **not officially supported** for CUDA in WSL2 (it *may* still work). Also, **install the NVIDIA driver only on Windows**—don’t install a Linux display driver inside WSL. ([NVIDIA Docs][1])

**Verify GPU is visible in WSL:**

```bash
# from Windows (optional, keeps WSL current)
wsl --update

# inside WSL
nvidia-smi
python3 -c "import onnxruntime as ort; print(ort.get_available_providers())"
```

If you later see `['CUDAExecutionProvider', 'CPUExecutionProvider']`, CUDA is usable from WSL. If not, use the CPU path below. (DirectML is Windows-only, not available in Linux/WSL.) ([onnxruntime.ai][2])

---

## ✅ Option A — **Piper TTS (WSL + CUDA)**  *(recommended if your Maxwell shows up)*

Piper runs on **ONNX Runtime**; with the CUDA provider it’s fast and lightweight.

```bash
# fresh venv
python3 -m venv ~/venvs/piper && source ~/venvs/piper/bin/activate
python -m pip install --upgrade pip

# install Piper + ORT CUDA
pip install piper-tts onnxruntime-gpu

# get a voice and test
piper --download-voices
piper --list-voices | head
piper --cuda -m /path/to/voice.onnx -t "Hello from WSL on the GPU." -o out.wav
python - <<'PY'
import onnxruntime as ort; print("Providers:", ort.get_available_providers())
PY
```

* Piper’s package/CLI (`pip install piper-tts`, `piper --...`) is documented in the project README. The `--cuda` flag uses ONNX Runtime’s CUDA provider. ([GitHub][3])
* If you choose to install CUDA tooling inside WSL, **only** install the **`cuda-toolkit-12-x`** metapackage (do **not** install `cuda` or `cuda-drivers`, which try to add a Linux driver). ([NVIDIA Docs][1])

---

## ✅ Option B — **Kokoro-ONNX (WSL + CUDA)**  *(tiny, high quality)*

Kokoro ships **ONNX** models; you run them with ONNX Runtime (CUDA in WSL).

```bash
python3 -m venv ~/venvs/kokoro && source ~/venvs/kokoro/bin/activate
python -m pip install --upgrade pip
pip install kokoro-onnx onnxruntime-gpu soundfile

# minimal example (per repo README/examples; download model+voices first)
# get kokoro-v1.0.onnx and voices-v1.0.bin into the CWD, then:
python - <<'PY'
from kokoro_onnx import Kokoro
k = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
wav = k.create("Hello from Kokoro running in WSL on CUDA.", voice="en_US/amy")
open("kokoro.wav","wb").write(wav)
print("ok")
PY
```

* Kokoro-ONNX is designed to run with ONNX Runtime and provides simple setup/use. ([GitHub][4])

---

## ✅ Option C — **Piper (WSL, CPU)**  *(always works, still quite fast)*

If CUDA isn’t available in WSL on your 970, stay in WSL and use CPU.

```bash
python3 -m venv ~/venvs/piper && source ~/venvs/piper/bin/activate
python -m pip install --upgrade pip
pip install piper-tts onnxruntime   # CPU package (no -gpu)
piper -m /path/to/voice.onnx -t "CPU path, still in WSL." -o out.wav
```

* Same Piper CLI, just without the CUDA provider. ([GitHub][3])

---

## Notes & troubleshooting

* **GPU in WSL on Maxwell:** NVIDIA’s guide lists **“Maxwell GPU is not supported… may still work; Pascal or later recommended.”** If `nvidia-smi` fails in WSL, assume CPU path. ([NVIDIA Docs][1])
* **DirectML:** is **Windows-only**; you can’t use it inside WSL. (If you ever need DirectML acceleration, that would be a Windows-native env.) ([GitHub][5])
* **Audio output on Windows 10:** WSLg audio is primarily a Windows 11 feature. On Windows 10, it’s simplest to **write WAVs in WSL** and **play them from Windows** (e.g., `cmd.exe /c start out.wav`). PulseAudio bridges exist but are fiddly on Win10. ([Microsoft Learn][6])

---

### Quick recommendation for your repo (WSL-centric)

* Try **Option A (Piper + CUDA)**. If `CUDAExecutionProvider` doesn’t appear, switch to **Option C (Piper CPU)** without changing any of your app code paths (only the env/flag changes).
* Keep **Kokoro-ONNX** as an alternate voice stack (Option B) if you want a different timbre/quality with similar runtime behavior.

Want me to draft a **drop-in Piper provider** (WSL) and a tiny CLI/benchmark that mirrors your XTTS harness?

[1]: https://docs.nvidia.com/cuda/wsl-user-guide/index.html "CUDA on WSL User Guide — CUDA on WSL 13.0 documentation"
[2]: https://onnxruntime.ai/docs/install/?utm_source=chatgpt.com "Install ONNX Runtime | onnxruntime"
[3]: https://github.com/OHF-Voice/piper1-gpl "GitHub - OHF-Voice/piper1-gpl: Fast and local neural text-to-speech engine"
[4]: https://github.com/thewh1teagle/kokoro-onnx "GitHub - thewh1teagle/kokoro-onnx: TTS with kokoro and onnx runtime"
[5]: https://github.com/microsoft/onnxruntime-genai/discussions/387?utm_source=chatgpt.com "DirectML requirements? · microsoft onnxruntime-genai"
[6]: https://learn.microsoft.com/en-us/windows/wsl/tutorials/gui-apps?utm_source=chatgpt.com "Run Linux GUI apps with WSL - Windows"

**From Claude Opus 4.1**
Thank you for sharing these detailed benchmark results! This is actually a perfect illustration of an important principle in AI model deployment: not all models that *can* run on certain hardware will run *well* on that hardware. Let me help you understand why XTTS-v2 struggled on your GTX 970 and why Piper TTS is indeed your best path forward.

## Understanding Why XTTS-v2 Underperformed

Your benchmark results reveal something crucial about the nature of different TTS architectures. XTTS-v2 is what we call an **autoregressive model**, which means it generates audio token by token, with each new token depending on all the previous ones. Think of it like writing a sentence one letter at a time, where you have to read the entire sentence so far before adding each new letter. This sequential nature creates a computational bottleneck that's particularly punishing on older hardware.

The Maxwell architecture of your GTX 970 lacks several optimizations that newer GPUs use to accelerate these sequential operations. When you combine this with XTTS-v2's size (nearly 2GB) and the fact that it needs to compute speaker embeddings even for default voices, you get a perfect storm of performance challenges. Your 4GB of VRAM is technically sufficient to *load* the model, but it doesn't leave much room for the intermediate computations that need to happen during generation, likely causing memory transfers that further slow things down.

## The Architectural Divide in TTS Models

There's a fundamental split in how TTS models approach speech generation, and understanding this will help you make better choices for your hardware:

**Autoregressive models** (like XTTS-v2, Tacotron2, and most high-quality voice cloning systems) generate speech sequentially. They produce remarkably natural, expressive speech with excellent prosody, but at the cost of computational intensity. Each output depends on all previous outputs, creating a chain of dependencies that can't be parallelized.

**Non-autoregressive models** (like Piper, FastSpeech2, and many ONNX-based systems) generate multiple parts of the speech in parallel. Imagine having ten people each write one word of a sentence simultaneously, then assembling them together. This parallel processing is exactly what your GPU was designed to excel at, even with its older architecture.

## Why Piper TTS Will Work Better

Piper TTS represents a completely different philosophy in TTS design, one that aligns perfectly with your hardware constraints:

The models are typically 20-50MB (compared to XTTS-v2's 2GB), which means your entire model, intermediate computations, and output buffers can fit comfortably in your 4GB VRAM with room to spare. This eliminates the memory transfer bottlenecks that were likely plaguing your XTTS-v2 performance.

More importantly, Piper uses ONNX runtime, which is specifically optimized for inference on a wide variety of hardware. ONNX includes optimizations for older GPU architectures that PyTorch might not prioritize. It's like having a car specifically tuned for your local roads rather than a Formula 1 car that needs a perfect track to perform well.

The non-autoregressive nature means your GPU can use its parallel processing capabilities effectively. Your GTX 970 has 1,664 CUDA cores - with Piper, you can actually use them in parallel rather than having most of them sit idle waiting for sequential computations to complete.

## Setting Realistic Expectations

Based on your hardware and the benchmark results, here's what you should realistically expect:

**With Piper TTS**, you should achieve latencies in the 0.2-0.5 second range for typical sentences. This meets your target and would actually be faster than your current OpenAI TTS solution. The quality will be good - clear, intelligible, and natural-sounding - though it won't have the same level of emotional expressiveness or voice cloning capabilities as XTTS-v2.

Think of it this way: XTTS-v2 on your hardware is like trying to run a 4K video game on medium settings - technically possible but frustratingly slow. Piper is like a well-optimized game from a few years ago running on high settings - smooth, responsive, and actually enjoyable to use.

## Alternative Approaches to Consider

While Piper is your best immediate solution, let me suggest a few other strategies you might explore:

**Hybrid approach**: You could use Piper for real-time responses where latency matters, but keep XTTS-v2 available for cases where quality matters more than speed (like generating audio files for later playback).

**Model distillation**: Some projects have created smaller, distilled versions of larger TTS models. Look for models labeled "small" or "tiny" in the Coqui ecosystem - these trade some quality for significant speed improvements.

**Streaming synthesis**: If your application allows, you could implement streaming TTS where you start playing audio before the entire utterance is generated. This won't reduce total generation time but can dramatically improve perceived latency.

## Moving Forward with Piper

When you implement Piper, pay attention to these optimization opportunities:

Choose models trained on phoneme inputs rather than raw text if available - these typically generate faster because the text processing step is simpler. The quality difference is usually negligible for most applications.

Piper supports different quality levels for many voices. Start with the medium quality versions - they often provide the best balance of speed and quality for real-time applications. You can always test the high-quality versions to see if they still meet your latency requirements.

Consider implementing a simple cache for commonly spoken phrases. Since Piper is deterministic (same input always produces same output), you can cache and reuse generated audio for frequently repeated text.

## The Broader Lesson

Your experience here illustrates an important principle in AI deployment: the newest, most sophisticated models aren't always the best choice for every situation. Your GTX 970 is perfectly capable hardware for TTS - you just need to match it with models designed for efficiency rather than maximum quality.

This is similar to how in the earlier days of digital photography, professional photographers would sometimes choose older, smaller sensors for certain types of work because they were faster and more responsive, even though larger sensors produced better image quality. The key is matching the tool to the task and the constraints you're working within.

I strongly recommend proceeding with the Piper implementation. It's not a compromise or a fallback - it's the right tool for your specific combination of hardware capabilities and latency requirements. You'll likely be pleasantly surprised by how responsive and capable it is on your GTX 970.