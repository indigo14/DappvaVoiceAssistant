**From chatGPT-5**
Great question. On a GTX 970 (Maxwell, 4 GB VRAM) + Windows 10, here are the **local TTS stacks that can use your GPU**—plus the safest picks for your setup.

# Best GPU-friendly local TTS options

## 1) Piper TTS (ONNX Runtime) — **fast, light, and easy**

* **Why it’s ideal for GTX 970:** Piper runs with **ONNX Runtime**. You can choose:

  * **CUDA** (`onnxruntime-gpu`) for NVIDIA, or
  * **DirectML** (`onnxruntime-directml`) which accelerates on *any* DirectX 12 GPU (great fallback on older cards). ([onnxruntime.ai][1])
* Piper’s codebase explicitly supports a `--cuda` path; the maintainer added GPU flags and notes that the **Python build supports CUDA**. (Repo moved to a new org, but the docs and flags remain the same.) ([GitHub][2])
* **Recommendation for you:** Install **`onnxruntime-gpu`** first. If drivers/tooling fight you, switch to **`onnxruntime-directml`** and run Piper with GPU via DirectML. ([onnxruntime.ai][1])

## 2) Kokoro TTS (ONNX) — **new, tiny (~82 M), high quality**

* Kokoro ships solid **ONNX** builds and wrappers; it runs with **ONNX Runtime** and supports GPU backends (CUDA or DirectML). Community packages expose a simple `ONNX_PROVIDER=CUDAExecutionProvider` toggle. ([GitHub][3])
* Official/communal pages highlight Kokoro’s small size and multi-voice packs; ONNX Runtime provides the actual GPU acceleration. ([Hugging Face][4])
* **Why it’s good for 4 GB VRAM:** Very lightweight compared to giant PyTorch TTS models. ([Medium][5])

## 3) Coqui TTS (XTTS-v2) — **voice cloning & multilingual (PyTorch)**

* Coqui TTS/XTTS-v2 runs best on **PyTorch + CUDA**; GPU is strongly recommended for inference. ([docs.coqui.ai][6])
* **Caveat for Maxwell:** Newer PyTorch CUDA wheels are focused on recent architectures. If a current wheel doesn’t include **sm_5x** kernels, install an older **Torch + CUDA 11.x** build that *does* (or build from source). You can confirm support by checking the printed “supported CUDA capabilities” list at runtime; some builds still list **sm_50**/**sm_52**. ([PyTorch Forums][7])
* If CUDA is too finicky on Maxwell, Coqui may still run **CPU-only**, or you can try **torch-directml** (works on DX12 GPUs, but operator coverage varies). ([Microsoft Learn][8])

## 4) Mimic3 (legacy) — **ONNX + GPU works, but unmaintained**

* Mimic3 can use **`onnxruntime-gpu`** and `--cuda` for acceleration, but the project has been **archived**; Piper is its successor. Useful if you already have a voice you like. ([mycroft-ai.gitbook.io][9])

## 5) Bark / other research models (PyTorch)

* Bark supports GPU (PyTorch 2.0+, CUDA 11.7/12), but it’s heavy and **slow on older GPUs**—not my first pick for a 970. ([GitHub][10])

---

## Quick picks for your machine

* **Easiest & fast today:** **Piper + ONNX Runtime** (try **CUDA** first; if pain ⇒ **DirectML**). ([onnxruntime.ai][1])
* **Small, high-quality voices:** **Kokoro (ONNX)** with CUDA or DirectML. ([GitHub][3])
* **Need cloning/multilingual:** **Coqui XTTS-v2** on **PyTorch**, but pin a Torch build that reports **sm_5x** support (or build from source). ([docs.coqui.ai][11])

---

## Windows vs WSL2 on a Maxwell card

* **Prefer Windows native** for GPU. NVIDIA’s docs state **Maxwell GPUs aren’t officially supported in WSL 2** (it *may* work, but it’s not reliable). ONNX DirectML isn’t available inside Linux; it’s a Windows tech. ([NVIDIA Docs][12])

If you want, I can turn this into a one-pager with *exact* install commands for Piper-CUDA, Piper-DirectML, and Kokoro-ONNX on your Windows 10 box.

[1]: https://onnxruntime.ai/docs/install/?utm_source=chatgpt.com "Install ONNX Runtime | onnxruntime"
[2]: https://github.com/rhasspy/wyoming-piper/pull/5?utm_source=chatgpt.com "Enable GPU support #5 - rhasspy/wyoming-piper"
[3]: https://github.com/thewh1teagle/kokoro-onnx?utm_source=chatgpt.com "TTS with kokoro and onnx runtime"
[4]: https://huggingface.co/onnx-community/Kokoro-82M-ONNX?utm_source=chatgpt.com "onnx-community/Kokoro-82M-ONNX"
[5]: https://medium.com/data-science-in-your-pocket/kokoro-82m-the-best-tts-model-in-just-82-million-parameters-512b4ba4f94c?utm_source=chatgpt.com "Kokoro-82M: The best TTS model in just 82 Million ..."
[6]: https://docs.coqui.ai/?utm_source=chatgpt.com "TTS 0.22.0 documentation"
[7]: https://discuss.pytorch.org/t/nvidia-geforce-rtx-5070-ti-with-cuda-capability-sm-120/221509?utm_source=chatgpt.com "NVIDIA GeForce RTX 5070 Ti with CUDA capability sm_120"
[8]: https://learn.microsoft.com/en-us/windows/ai/directml/pytorch-windows?utm_source=chatgpt.com "Enable PyTorch with DirectML on Windows"
[9]: https://mycroft-ai.gitbook.io/docs/mycroft-technologies/mimic-tts/mimic-3?utm_source=chatgpt.com "Mimic 3 | Mycroft AI - GitBook"
[10]: https://github.com/suno-ai/bark?utm_source=chatgpt.com "suno-ai/bark: 🔊 Text-Prompted Generative Audio Model"
[11]: https://docs.coqui.ai/en/latest/models/xtts.html?utm_source=chatgpt.com "TTS 0.22.0 documentation"
[12]: https://docs.nvidia.com/cuda/wsl-user-guide/index.html?utm_source=chatgpt.com "CUDA on WSL User Guide"








**From Claude Opus 4.1**
Let me research text-to-speech options that will work with your GTX 970 GPU. Since you're dealing with the same Maxwell architecture limitations, we'll need to find TTS solutions that don't require the latest CUDA features.Great question! Let me walk you through the TTS landscape for your GTX 970. The good news is that you have several excellent options, and your 4GB VRAM is actually sufficient for many modern TTS models. Let me explain how the TTS ecosystem works with older GPUs and what your best options are.

## Understanding TTS GPU Requirements

Before diving into specific solutions, it's helpful to understand why TTS is generally more forgiving than speech-to-text regarding GPU requirements. TTS models tend to be smaller than their STT counterparts and don't require the same architectural features that faster-whisper demands. For TTS, even entry-level GPUs with 4GB of memory can handle models that generate 30-second audio clips, with batch processing being viable on lower-end GPUs when latency isn't critical.

Your GTX 970 sits comfortably in the range where you can run quality TTS models effectively, though you'll want to be strategic about model selection based on your specific needs.

## Coqui TTS and XTTS - Your Primary Option

The most mature and versatile option for your setup is Coqui TTS (formerly Mozilla TTS), particularly the XTTS models. This ecosystem has been designed with broad hardware compatibility in mind.

### Why XTTS Works Well on Your Hardware

XTTS-v2, which is about 2GB in size, can run on GPUs with 4GB or more VRAM. Your GTX 970's 4GB VRAM places you right at the threshold where you can run these models effectively. The system is built on PyTorch with CUDA support, and there's explicit support for CUDA 11.8 for older cards like yours.

When you install Coqui TTS, you'll use the standard PyTorch CUDA installation, just like with Whisper. The key difference is that you need to explicitly enable GPU support by passing `gpu=True` when initializing the model: `tts = TTS("model_name", gpu=True)`.

### Setting Up Coqui TTS

The installation process mirrors what you'd do for Whisper:

1. Install PyTorch with CUDA support for your system (likely CUDA 11.6 or 11.8)
2. Install Coqui TTS: `pip install coqui-tts`
3. When running models, explicitly enable GPU: For example, `tts = TTS("tts_models/multilingual/multi-dataset/xtts_v1", gpu=False)` for CPU or `gpu=True` for GPU usage

One particularly useful feature for your hardware situation is that Coqui TTS can run on CPU as a fallback option, which means you're never completely blocked if a particular model proves too demanding for your GPU.

### Model Recommendations for 4GB VRAM

With your 4GB VRAM constraint, you'll want to focus on models that fit comfortably within your memory limits:

1. **XTTS-v2**: This is the sweet spot for your hardware. It offers multilingual support, voice cloning capabilities, and reasonable performance within your VRAM budget.

2. **Smaller Tacotron2 models**: These older but reliable models work well on limited hardware and provide good quality English synthesis.

3. **VITS models**: These are efficient and produce high-quality output while being relatively lightweight.

## Memory Management Strategies

If you encounter memory issues with larger models, there's an interesting development from NVIDIA that could help. Recent NVIDIA drivers include a "CUDA Sysmem Fallback Policy" feature that allows the GPU to use system RAM as overflow when VRAM runs out, enabling users with 8GB cards to effectively use up to 17GB of combined memory. While this feature was mentioned for newer cards, it's worth checking if your driver version supports it.

To check if this is available:
- Update to the latest NVIDIA drivers for your GTX 970
- Look for "CUDA Sysmem Fallback Policy" in the NVIDIA Control Panel under "Manage 3D settings"
- If available, this could significantly expand what models you can run

## Docker Deployment Options

For a more managed approach, Coqui provides Docker images that support both CUDA 11.8 (for older cards) and CPU-only operation. This can simplify your setup considerably:

```bash
# For GPU (CUDA 11.8, perfect for your GTX 970):
docker run --gpus=all -e COQUI_TOS_AGREED=1 --rm -p 8000:80 ghcr.io/coqui-ai/xtts-streaming-server:latest

# For CPU fallback if needed:
docker run -e COQUI_TOS_AGREED=1 --rm -p 8000:80 ghcr.io/coqui-ai/xtts-streaming-server:latest-cpu
```

## Performance Expectations

With your GTX 970, you should expect:

1. **Voice Cloning**: XTTS can clone voices with just 3-10 seconds of reference audio. This will work on your GPU, though processing might take a few seconds longer than on newer hardware.

2. **Real-time Factor**: While newer GPUs might achieve 1:15 or better (generating 15 seconds of audio per second of processing), you might see something closer to 1:3 to 1:5, which is still very usable for most applications.

3. **Language Support**: The multilingual capabilities of XTTS work regardless of your GPU generation - you'll get the same quality output, just with slightly longer generation times.

## Alternative Approaches

If you find that certain models are too demanding, consider these strategies:

1. **Streaming Generation**: Instead of generating entire speeches at once, generate smaller segments. This reduces memory requirements and can improve perceived responsiveness.

2. **Lower Precision**: Some models support running in FP16 (half precision) mode, which reduces memory usage while maintaining acceptable quality.

3. **CPU Fallback**: For models that don't fit in your VRAM, CPU generation is always an option. While slower, modern CPUs with AVX instructions can still provide reasonable performance for TTS.

## The Bottom Line

Your GTX 970 is absolutely viable for local TTS, particularly with the Coqui TTS ecosystem. The key is choosing models that fit within your 4GB VRAM budget - primarily XTTS-v2 and smaller models. Unlike the situation with faster-whisper, you're not locked out by architectural requirements. The TTS landscape has maintained better backward compatibility, likely because TTS has been around longer and the community has prioritized accessibility.

Start with XTTS-v2 through Coqui TTS, as it offers the best balance of features, quality, and compatibility with your hardware. If you need more performance, the Docker deployment options make it easy to experiment with different configurations. Remember, even if GPU acceleration isn't optimal, the CPU fallback means you'll always have a working solution - it's just a matter of optimizing for your specific use case and performance requirements.

