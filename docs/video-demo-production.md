# ReproScout final video production

The final English product demonstration is an independent project presentation
by Weibing Wang. Narration uses I/my throughout. The local delivery master is
`private/video-final/delivery/reproscout-final.mp4`: 1920 × 1080, 30 fps,
266.033 seconds. [Watch the uploaded video](https://youtu.be/FWAhCytPl-0). Signed-out playback and Unlisted visibility were verified on November 19, 2026.

The final script is in `deliverables/video-demo/narration.txt`. The storyboard
retains original planning estimates alongside final measured timings.
`deliverables/video-demo/youtube-upload.txt` provides title, description and chapters.
Private media remains Git-ignored. The earlier 288-second first cut is preserved
under `private/video-plus/`, along with earlier voice comparisons.

## Product story

The demonstration follows a prepared scientific project through import, original
code execution, candidate answers, cited evidence, source-integrity inspection,
attributed review, and portable report export. The scikit-learn diabetes example
uses unchanged original code and a compatible pinned runtime. Arbitrary repository
adaptation is not automatic. Successful execution is distinct from scientific
correctness, and file hashes do not establish semantic validity.

The exact browser acceptance run is
`20261119T052436478104Z-sklearn-diabetes-ols-102-run-A1`: five model calls,
20.4015 seconds, estimated model cost $0.00422805. It retained three answers and
four unchanged inventoried inputs. Saved reviews are attributed to an assistant.
The CI card uses the separate retained GitHub Actions record 44469346488; it does
not combine that run's timings with the browser attempt.

The authenticated pilot was captured on the development host. The public website
is a read-only evidence archive; durable public execution remains pending.
No additional scientific run was launched for the final edit. A fresh account
imported the bundle, and another real export/citation check supplied final footage.

## Voice and synchronization

The presenter selected Qwen cloud Plus and authorized the full narration using
his own supplied reference recording. The model is `qwen-audio-3.1-tts-plus`.
The existing enrolled voice is reused; no voice model weights were downloaded.
Scenes 01, 03, 06, 09 and 10 were regenerated to clarify language or solo authorship.
Others retain the previous cloud audio.

An already-cached Whisper large-v3 recognition model supplied acoustic word
timestamps. Qwen cloud ASR independently transcribed the audio. No new local model
weights were downloaded. Speech recognition checks are automated, not a claim of
human listening. Proper-name spelling, punctuation, and numeric caption notation
were normalized. The final script and subtitles have no collective we/our/us.

The final editor uses speech cues for visual changes, particularly the switch
from MSE evidence to source integrity. UI crops preserve actual values and review
identity. The review-history and CI cards are editorial views derived from real
saved JSON, not simulated live interface states. Each normalized audio segment
has an exact sample count, and the assembled master uses continuous audio.

## Rebuild and validation

`uv run python scripts/finalize_narrated_demo.py` assembles the final video from
private `alignment.json`, audio files and screenshots under `private/video-final/`.
The first-cut renderer and capture scripts remain available. Rebuilding final
media requires those private inputs; credentials and recordings are not distributed.

The private delivery contains MP4, WAV/MP3, ten scene WAVs, SRT/VTT, thumbnail,
script, storyboard, measured timeline, quality-check JSON, upload text and checksums.
Validation covers complete decoding, 1080p/30fps output, audio/video endpoint
agreement, non-overlapping captions, at most two subtitle lines, reading speed,
all 33 planned visual states, source hashes, and first-person singular narration.
The package excludes the voice reference, credentials and authentication state.

## Final scene timings

- 01 — The research problem: 0.000–21.733 seconds.
- 02 — What goes in and what comes out: 21.733–46.267 seconds.
- 03 — Import the real example: 46.267–70.533 seconds.
- 04 — Run with explicit limits: 70.533–93.433 seconds.
- 05 — Read the actual result: 93.433–120.700 seconds.
- 06 — Inspect the evidence: 120.700–157.833 seconds.
- 07 — Record a review: 157.833–180.467 seconds.
- 08 — Export and share: 180.467–206.900 seconds.
- 09 — Show what has been validated: 206.900–240.067 seconds.
- 10 — Close on the product: 240.067–266.033 seconds.
