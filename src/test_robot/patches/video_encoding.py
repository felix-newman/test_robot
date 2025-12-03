import logging
import subprocess
import time
from pathlib import Path


def fast_encode_video_frames(
    imgs_dir,
    video_path,
    fps,
    vcodec="libsvtav1",
    pix_fmt="yuv420p",
    g=2,
    crf=30,
    fast_decode=0,
    log_level=None,
    overwrite=False,
):
    start = time.perf_counter()
    imgs_dir = Path(imgs_dir)
    video_path = Path(video_path)

    if video_path.exists() and not overwrite:
        logging.warning(f"Video file already exists: {video_path}. Skipping encoding.")
        return

    video_path.parent.mkdir(parents=True, exist_ok=True)

    # Build FFmpeg command
    cmd = [
        "ffmpeg",
        "-y" if overwrite else "-n",
        "-framerate",
        str(fps),
        "-pattern_type",
        "glob",
        "-i",
        str(imgs_dir / "frame-*.png"),
    ]

    # Map codecs to NVENC equivalents if available
    # Note: NVENC uses -cq or -qp instead of -crf usually, but ffmpeg might map it.
    # However, to be safe, we should check if the user wanted a specific codec.
    # If they passed default "libsvtav1", we can try "av1_nvenc".

    if vcodec == "libsvtav1":
        vcodec = "av1_nvenc"
    elif vcodec == "h264":
        vcodec = "h264_nvenc"
    elif vcodec == "hevc":
        vcodec = "hevc_nvenc"

    cmd.extend(["-c:v", vcodec])

    # NVENC specific handling for pixel format
    # NVENC often prefers yuv420p
    cmd.extend(["-pix_fmt", pix_fmt])

    if g is not None:
        cmd.extend(["-g", str(g)])
        # NVENC fix: GOP length must be > B-frames + 1.
        # Since 'g' (GOP size) is often small in these datasets (e.g. 2), we must disable B-frames to be safe.
        if "nvenc" in vcodec and g < 5:
            cmd.extend(["-bf", "0"])

    # NVENC uses -cq (Constant Quality) or -qp instead of -crf
    # For simplicity, we map crf to cq for nvenc codecs
    if crf is not None:
        if "nvenc" in vcodec:
            cmd.extend(["-cq", str(crf)])
            # NVENC sometimes needs a preset for quality vs speed
            cmd.extend(["-preset", "p4"])  # p4 is medium preset
        else:
            cmd.extend(["-crf", str(crf)])

    if fast_decode:
        if vcodec == "libsvtav1":
            cmd.extend(["-svtav1-params", f"fast-decode={fast_decode}"])
        elif "nvenc" not in vcodec:
            cmd.extend(["-tune", "fastdecode"])

    # Reduce log verbosity unless there's an error
    cmd.extend(["-loglevel", "error"])

    cmd.append(str(video_path))

    try:
        time1 = time.perf_counter()
        subprocess.run(cmd, check=True, capture_output=True)
        time2 = time.perf_counter()
        print(f"FFmpeg encoding took {time2 - time1:.3f} seconds")
    except subprocess.CalledProcessError as e:
        raise OSError(
            f"FFmpeg encoding failed.\nCommand: {' '.join(cmd)}\nError: {e.stderr.decode()}"
        ) from e
    end = time.perf_counter()
    print(f"Video encoding took {end - start:.3f} seconds")
