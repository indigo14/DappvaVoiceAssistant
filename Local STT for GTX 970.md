**From gpt**
Got it. Short version: your GTX 970 (Maxwell, CC 5.2, 4 GB VRAM) can still run good local STT—just not with CTranslate2’s “ideal” (Tensor-Core) path. Here are the best options that **do** work on your card, plus the caveats.

# What works well on a GTX 970

**1) whisper.cpp (ggml) — CUDA *or* Vulkan acceleration (recommended)**

* Runs Whisper locally without PyTorch/CUDA baggage; supports multiple backends: CUDA (cuBLAS) and cross-vendor **Vulkan** (handy if CUDA toolchains get fussy). ([GitHub][1])
* Maxwell GPUs are supported; many users build with `GGML_CUDA=1` *or* `GGML_VULKAN=1`. Vulkan can be nearly as fast as CUDA and works broadly. ([GitHub][1])
* Use **tiny/base/small** (or quantized Q5/Q6) given your 4 GB VRAM; medium and large can exceed memory. (General VRAM guidance: ~1 GB tiny/base, ~2 GB small, ~5 GB medium, ~10 GB large.) ([Zread][2])

**2) Original OpenAI Whisper (PyTorch) — GPU in FP32 (works, but mind versions)**

* PyTorch Whisper can run on Maxwell; set FP32 (not FP16) since older GTX cards are weak at FP16. Community benches noted FP32 faster than FP16 on older GPUs. ([GitHub][3])
* **Version caveat:** Newer PyTorch CUDA wheels are dropping Maxwell/Pascal in late 2025 (CUDA 12.8/12.9 series). If you go this route, pin to a PyTorch release that still includes SM 5.x in its CUDA builds (≤ 2.7). ([PyTorch Developer Mailing List][4])
* Same VRAM limits as above (tiny/base/small fit best on 4 GB). ([Zread][2])

**3) faster-whisper (CTranslate2) — *Actually still compatible***

* Your earlier blocker (“needs Pascal+”) is a common misconception. **CTranslate2 prebuilt binaries support any NVIDIA GPU with compute capability ≥ 3.5** (Maxwell is 5.2), provided you have a CUDA-12-series driver and cuDNN 8. It *recommends* Tensor Cores (≥ 7.0) for best speed, but they’re not required. ([opennmt.net][5])
* Translation: it should run on a GTX 970; it just won’t be as fast as on Turing/Ampere. (Quantized 8-bit models can help.) ([GitHub][6])

**4) ONNX Runtime + DirectML (Whisper-ONNX) — GPU without CUDA**

* If you want to avoid CUDA entirely on Windows 10, DirectML can accelerate ONNX models on **any** DirectX-12 GPU (which includes the GTX 970). Microsoft showcases Whisper on ONNX Runtime; just note DirectML Whisper pipelines have had performance/feature gaps (KV-cache, dynamic axes) reported by users. ([Medium][7])

**5) Vosk (Kaldi) — CPU-first fallback**

* Easy offline STT with small models and low requirements; accuracy is behind Whisper but it’s rock-solid and lightweight if you want “it just works” on CPU. ([GitHub][8])

---

## Windows 10 + WSL2 notes (GPU)

* **GPU in WSL2 is supported** on current Windows 10 builds with recent NVIDIA drivers, but it’s simpler (and often faster) to run Whisper/whisper.cpp **natively on Windows** on older cards. If you *do* use WSL2, follow NVIDIA/Microsoft’s CUDA-on-WSL guides and keep drivers current. ([NVIDIA Docs][9])

## Practical picks for your rig (4 GB VRAM)

* **Fastest/easiest today:** **whisper.cpp** with CUDA or Vulkan; run **base** or **small** models (or quantized). ([GitHub][1])
* **If you want PyTorch features (diarization add-ons, etc.):** original Whisper on PyTorch, pinned to a pre-2.8 CUDA build that still supports SM 5.x, using FP32. ([PyTorch Developer Mailing List][4])
* **If you prefer the CTranslate2 ecosystem:** try **faster-whisper** with CUDA 12 + cuDNN 8; expect lower throughput than Tensor-Core GPUs but it should run. ([opennmt.net][10])
* **CUDA-free path:** ONNX Runtime **DirectML** (Whisper-ONNX). Good to keep in the toolbox if drivers get messy. ([Medium][7])

If you want, I can turn this into a one-pager with exact “choose-one” install steps for each path (Windows native vs WSL2), tuned for your GTX 970 and Windows 10.

[1]: https://github.com/ggml-org/whisper.cpp?utm_source=chatgpt.com "ggml-org/whisper.cpp"
[2]: https://zread.ai/openai/whisper/17-performance-optimization?utm_source=chatgpt.com "Performance Optimization | openai/whisper"
[3]: https://github.com/openai/whisper/discussions/391?utm_source=chatgpt.com "Some speed & GDDR measurements for choosing a GPU ..."
[4]: https://dev-discuss.pytorch.org/t/cuda-toolkit-version-and-architecture-support-update-maxwell-and-pascal-architecture-support-removed-in-cuda-12-8-and-12-9-builds/3128?utm_source=chatgpt.com "CUDA toolkit version and architecture support update ..."
[5]: https://opennmt.net/CTranslate2/hardware_support.html "Hardware support — CTranslate2 4.6.0 documentation"
[6]: https://github.com/SYSTRAN/faster-whisper?utm_source=chatgpt.com "Faster Whisper transcription with CTranslate2"
[7]: https://medium.com/microsoftazure/build-and-deploy-fast-and-portable-speech-recognition-applications-with-onnx-runtime-and-whisper-5bf0969dd56b?utm_source=chatgpt.com "Build and deploy fast and portable speech recognition ..."
[8]: https://github.com/alphacep/vosk-api?utm_source=chatgpt.com "alphacep/vosk-api: Offline speech recognition ..."
[9]: https://docs.nvidia.com/cuda/wsl-user-guide/index.html?utm_source=chatgpt.com "CUDA on WSL User Guide"
[10]: https://opennmt.net/CTranslate2/installation.html "Installation — CTranslate2 4.6.0 documentation"


**From Claude OPus**
I understand your situation - you're running into a hardware limitation where the GTX 970's Maxwell architecture doesn't support the instruction sets that ctranslate2 needs for faster-whisper. Let me research current speech-to-text solutions that will work with your GPU setup.Good news! Your GTX 970 actually has several excellent speech-to-text options available. Let me walk you through the solutions that will work with your Maxwell architecture GPU, starting with the most straightforward options.

## The Original OpenAI Whisper Works with Your GTX 970

The original OpenAI Whisper implementation explicitly supports GTX 970 and newer GPUs for hardware acceleration. This is different from faster-whisper, which requires the newer Pascal architecture. The standard Whisper uses PyTorch with CUDA support, and while it won't be as fast as faster-whisper on newer GPUs, it will still provide significant speedup over CPU-only processing.

To install the original Whisper on your Windows 10 WSL2 setup, you'll need to:

1. Install Python (3.8-3.11 recommended)
2. Install the CUDA-accelerated version of PyTorch by first uninstalling any vanilla torch installation, then installing with: `pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu116` (adjust the CUDA version to match your system)
3. Install Whisper: `pip install git+https://github.com/openai/whisper.git`
4. Install ffmpeg for audio processing

The setup process is straightforward, and you'll be able to use all Whisper model sizes, though the larger models will naturally process more slowly on your hardware.

## Whisper.cpp - An Excellent CPU-Optimized Alternative

Whisper.cpp is a C++ port of OpenAI's Whisper that runs entirely on the CPU and has virtually no dependencies. This implementation is particularly interesting for your setup because it doesn't require any GPU capabilities at all, yet still provides impressive performance through optimized CPU code.

The advantages of whisper.cpp include:
- No GPU requirements whatsoever
- Supports advanced CPU features like ARM NEON and x86 AVX for acceleration
- Minimal dependencies and easy installation
- Can be compiled directly or used through Python bindings
- Supports the same GGML model formats that are widely available

To use whisper.cpp in WSL2, you would clone the repository, compile it with make, and then download the GGML format models. The entire process is much simpler than setting up CUDA dependencies, and you might be surprised by the performance on modern CPUs.

## WhisperDesktop - Windows-Native DirectCompute Solution

For a Windows-native solution that will utilize your GTX 970, Const-me's WhisperDesktop uses DirectCompute (compute shaders in Direct3D 11) rather than CUDA, making it vendor-agnostic and compatible with any DirectX 11 capable GPU. This includes your GTX 970.

WhisperDesktop doesn't use tensor cores or special AI hardware, instead relying on standard GPU compute shaders, which means it works on older GPUs that newer implementations have left behind. The developer reports it being faster than the original PyTorch implementation on their GTX 1080Ti, so you should see good performance on your GTX 970.

The installation is remarkably simple:
1. Download WhisperDesktop.zip from the GitHub releases
2. Extract and run WhisperDesktop.exe
3. Download a GGML model (medium recommended)
4. Start transcribing

## Performance Expectations and Model Selection

With your GTX 970, you'll want to balance accuracy against processing speed. The different Whisper models require varying amounts of VRAM: tiny and base need about 1GB each, small needs 2GB, medium requires 5GB, and large needs 10GB. Your GTX 970 has 4GB of VRAM, so you'll comfortably run the small model and might manage the medium model depending on other system factors.

An important point about model selection: larger models use more GPU resources and process faster, but they're not necessarily more accurate for all use cases. The base and small models often provide excellent accuracy for English transcription while being much faster on limited hardware.

## Practical Recommendations

Given your specific hardware and Windows 10 WSL2 setup, I'd suggest this approach:

1. **Start with WhisperDesktop** for the simplest setup experience. It's a native Windows application that will definitely work with your GTX 970, requires no complex installation, and provides a GUI interface.

2. **If you need command-line integration or automation**, try the original OpenAI Whisper in WSL2 with CUDA support. Your GTX 970 is explicitly supported, and while it won't match the speed of newer GPUs, it will still significantly outperform CPU-only processing.

3. **For maximum compatibility and portability**, consider whisper.cpp. While it doesn't use your GPU, modern CPU optimizations can provide surprisingly good performance, and you won't have to worry about any GPU compatibility issues.

The key insight here is that the GTX 970's limitation specifically affects faster-whisper and other implementations that require newer CUDA compute capabilities. The original Whisper and alternative implementations like WhisperDesktop were designed with broader hardware compatibility in mind, making them perfect for your setup. You're not locked out of local speech-to-text at all - you just need to use the right implementation for your hardware generation.

