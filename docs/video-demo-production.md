# ReproScout video narration and storyboard

Prepare a roughly four-minute English product demonstration using actual application footage and the presenter’s own cloned voice. The story follows a researcher from prepared project import through original-code execution, evidence inspection, recorded review, and portable report export. Evidence review is the main interaction; infrastructure and historical A/B experiments are supporting context.

Production status: narration and storyboard prepared on November 19, 2026. The presenter has supplied a 21.568-second voice sample and its transcript. The official Qwen online demo returned a scene-one cloned audio sample successfully; presenter listening approval, new screen capture, subtitle alignment, and final video assembly are pending. Existing videos in `deliverables/` are earlier versions and are not the video described here.

## Production files

- [Complete English narration](../deliverables/video-demo/narration.txt): 497 words, in scene order. Only this text goes into speech generation; do not read scene numbers, production notes, URLs, or timecodes.
- [Voice reference recording script](../deliverables/video-demo/voice-reference.txt): a short recording sample for the presenter, separate from the full narration.
- [Machine-readable storyboard](../deliverables/video-demo/storyboard.json): scene text, planned timing, screen action, overlays, and capture notes.

The scene plan totals 240 seconds. At 135–150 spoken words per minute, the narration alone should take approximately 3.3–3.7 minutes. These are editing estimates; leave natural pauses around evidence and the closing card. Generate a sample first and adjust pacing after listening. Create final captions from the approved synthesized audio rather than treating these scene boundaries as subtitle timestamps.

## Editorial direction

Use 1920 × 1080, 16:9, approximately 30 fps. Keep the English interface and English subtitles. Record with consistent browser zoom, hide unrelated tabs and notifications, and move the cursor deliberately. Use short fades and gentle crops to direct attention to the current evidence line. A talking avatar, decorative stock footage, and background music are unnecessary for the first version.

Capture the authenticated pilot at `http://127.0.0.1:8780/`. Distinguish it from the public read-only website at `https://wuhubing.github.io/reproscout/`. Use a clean demonstration account for a new import, since the existing acceptance account already contains the example. Do not expose login codes or API credentials. Keep voice samples and access credentials outside the public repository, under its ignored `private/` directory if stored locally.

The central demonstration uses the unchanged scikit-learn diabetes regression example, not a research-paper-wide reproduction. Its compatible pinned runtime is not claimed to be an image published by the scikit-learn authors. Preparing a project is a prerequisite; arbitrary repository adaptation is not automatic.

## Scene overview

| Scene | Planned time | Focus |
| --- | --- | --- |
| 01 | 0:00–0:24 | The research problem |
| 02 | 0:24–0:50 | What goes in and what comes out |
| 03 | 0:50–1:15 | Import the real example |
| 04 | 1:15–1:38 | Run with explicit limits |
| 05 | 1:38–2:03 | Read the actual result |
| 06 | 2:03–2:34 | Inspect the evidence |
| 07 | 2:34–2:58 | Record a review |
| 08 | 2:58–3:20 | Export and share |
| 09 | 3:20–3:42 | Show what has been validated |
| 10 | 3:42–4:00 | Close on the product |

## Detailed script and shot plan

### Scene 01 The research problem

Planned time: 0:00–0:24.

**Narration**

Hello, I’m Weibing Wang. This is ReproScout, a scientific reproduction review tool developed for MIT one point one two five. When a research program finishes, we still need to ask: did it run the original computation, and does its output actually support the answer?

**Screen action**

Open on the ReproScout title, then show the real workspace overview. Add the project name, author, and course in a restrained title card.

**Overlay**

ReproScout | Scientific reproduction review

**Capture note**

Use the authenticated pilot at localhost:8780. Crop or clearly label the development-host address; do not replace it with a fictional public URL.

### Scene 02 What goes in and what comes out

Planned time: 0:24–0:50.

**Narration**

ReproScout connects those questions in one workflow. The input is a prepared project containing original code, data or documented data sources, research questions, and a pinned software environment. The output is a retained execution record, answers linked to evidence, and a portable report that another researcher can inspect.

**Screen action**

Show a simple three-part graphic: Prepared project → Original-code execution → Evidence and reviewed report. Transition into the Projects view.

**Overlay**

Original code + data + questions + environment → Evidence + review + report

**Capture note**

The diabetes data comes from the pinned scikit-learn installation. Do not claim that every project includes a separate uploaded dataset.

### Scene 03 Import the real example

Planned time: 0:50–1:15.

**Narration**

Here, I’m using an unchanged diabetes regression example from scikit-learn. In the signed-in workspace, I upload its prepared project bundle. ReproScout checks the archive and the input file hashes before registering it. The server must already have an approved runtime; importing a repository does not automatically solve its dependencies.

**Screen action**

Show the signed-in Projects screen, open Import project, select the supplied example ZIP, and show successful registration in a fresh demonstration account.

**Overlay**

Prepared ZIP | Input hashes verified | Approved runtime

**Capture note**

Do not show the access code. The existing account already contains this project; duplicate import will fail. Use a new demonstration account or explicitly label retained import footage.

### Scene 04 Run with explicit limits

Planned time: 1:15–1:38.

**Narration**

Next, I choose the questions and set the execution limits. The controller runs the author’s code in an isolated Docker environment with networking disabled inside the scientific container. The interface keeps the run visible while it works, including partial results or failures when a task cannot finish.

**Screen action**

Open New run. Show the three questions and the model-cost cap. Start only when capturing a new authorized demonstration attempt; otherwise use retained run footage and a labeled transition.

**Overlay**

Original-code execution | Offline scientific container | Explicit budget

**Capture note**

If waiting is shortened, display “Waiting shortened.” Never animate a fake success state or splice a different run’s cost into this run.

### Scene 05 Read the actual result

Planned time: 1:38–2:03.

**Narration**

The recorded browser acceptance run finished in about twenty seconds, using five model calls and an estimated model cost of less than one cent. It produced a regression coefficient, a test mean squared error, and an R-squared value. Those numbers are candidate answers. Completing execution does not, by itself, establish scientific correctness.

**Screen action**

Open the retained authenticated acceptance run. Show Completed, approximately 20 seconds, 5 model calls, and the estimated model charge. Briefly reveal the three question tabs.

**Overlay**

Execution completed ≠ conclusion independently verified

**Capture note**

Use run 20261119T052436478104Z-sklearn-diabetes-ols-102-run-A1 for these figures. Exact estimated model charge: $0.00422805. Excludes hosting and image costs.

### Scene 06 Inspect the evidence

Planned time: 2:03–2:34.

**Narration**

This is the central interaction. For the mean squared error question, I open the cited execution output. The highlighted line explicitly reports mean squared error: two thousand five hundred forty-eight point zero seven. I can check the metric name, the value, and the context, rather than trusting a generated sentence. The source integrity view separately shows whether the inventoried original files changed.

**Screen action**

Select Q2. Hold on stdout line 3 and candidate 2548.07. Slowly highlight the metric label and exact citation. Switch to Source integrity and show four unchanged inventoried files.

**Overlay**

Candidate → citation → original execution output

**Capture note**

Keep text readable. Do not claim hashes prove semantic correctness or verify all dependencies. The retained source audit covers four prepared inputs.

### Scene 07 Record a review

Planned time: 2:34–2:58.

**Narration**

A review records a decision, an explanation, and the evidence used to support it. Reviews also preserve the reviewer’s identity and whether the reviewer is a human or an assistant. In this recorded walkthrough, the three saved decisions are assistant reviews, not independent human validation. Earlier review versions remain available.

**Screen action**

Return to Results & review. Show a saved rationale, “assistant review by researcher,” and review history. For a new review capture, choose AI assistant and retain the new version.

**Overlay**

Decision + rationale + evidence + reviewer identity

**Capture note**

Do not change the existing assistant attribution to Human for the video. Saved decisions are evidence about the walkthrough, not a completed independent usability study.

### Scene 08 Export and share

Planned time: 2:58–3:20.

**Narration**

Finally, I export the report and open it outside the application. The package preserves the answers, evidence, and review records together. Following a citation takes me to the relevant output lines. A collaborator can examine how a conclusion was reached, instead of receiving only a final number or a screenshot.

**Screen action**

Click Export report, show the downloaded ZIP, then open the extracted report.html in a separate browser window. Click a citation and hold on the highlighted line.

**Overlay**

Portable report | Retained evidence | Traceable decisions

**Capture note**

Use the actual exported report. Keep download paths free of unrelated personal information. Record the offline citation jump, not just the ZIP icon.

### Scene 09 Show what has been validated

Planned time: 3:20–3:42.

**Narration**

We have also run this fixed example successfully on a GitHub-hosted runner, using the actual Docker environment and reproduction controller. That is an integration test, not a replacement for an online execution service. The public website currently presents retained evidence; the authenticated execution pilot has been verified on the development host.

**Screen action**

Show the successful Docker reproduction acceptance workflow, then a short status card with two columns: Public evidence website and Authenticated execution pilot.

**Overlay**

GitHub CI passed | Public archive live | Public execution deployment pending

**Capture note**

GitHub run 44469346488 is a separate attempt: 96-second full job, 17.51-second controller time. Do not merge those timings with the 20.4-second browser run.

### Scene 10 Close on the product

Planned time: 3:42–4:00.

**Narration**

ReproScout’s goal is to make scientific reproduction easier to examine: preserve the original computation, expose the evidence, and record the reviewer’s judgment. The next milestone is deploying the authenticated workflow on a suitable host and evaluating it with independent researchers. Thank you for watching.

**Screen action**

Return to a clean evidence view, then fade into a closing card with the public website and repository. Hold the final card for at least three seconds.

**Overlay**

reproscout | wuhubing.github.io/reproscout | github.com/Wuhubing/reproscout

**Capture note**

Add “Narration generated with the presenter’s authorized AI voice clone” only after cloned narration is actually used. No synthetic voice has been generated yet.

## Evidence references

| Claim | Evidence to use |
| --- | --- |
| Browser workflow, approximately 20.4 seconds, five calls, estimated $0.00422805 | [Online acceptance record](../reports/online-acceptance-v10.json) |
| Values, citations, four original inputs unchanged, assistant review history | [Reviewed browser-run report](../reports/online-runs/20261119T052436478104Z-sklearn-diabetes-ols-102-run-A1/report.html) |
| GitHub-hosted Docker and controller run succeeded | [GitHub workflow](https://github.com/Wuhubing/reproscout/actions/runs/44469346488) and [acceptance record](../reports/actions-acceptance/44469346488/acceptance.json) |
| Public archive and deployment distinction | [Online pilot status](online-pilot-v10.md) and [Actions feasibility](github-actions-feasibility.md) |

The browser-run acceptance JSON captures `reviewed: 0` in its initial run snapshot, before the review stage. Its top-level `reviews_saved: 3` and the exported report’s review history establish the subsequent saved decisions. Use the final reviewed report for that scene.

Do not claim that assistant reviews are human reviews, source hashes prove semantic correctness, the current website offers public execution, or the historical lessons studies prove a consistent improvement. Do not call the GitHub acceptance run a new A/B experiment. Preserve old videos and failed-run records.

## Qwen voice preparation

Use the official [Qwen3-TTS online demo](https://huggingface.co/spaces/Qwen/Qwen3-TTS) first. The [official project](https://github.com/QwenLM/Qwen3-TTS) provides voice cloning using reference audio and its matching transcript. An online demo or cloud API runs inference remotely; the presenter does not need to download model weights. A local installation would require model downloads and is not part of this plan. Demo availability and quotas are not a production guarantee.

Record the reference script in a quiet room using a natural English presentation voice. Aim for around 20 seconds; use one speaker, consistent microphone distance and volume, and no music or voice effects. Supply the exact words actually spoken as the transcript if they differ from the reference text. Save a WAV, M4A, or MP3 recording. The [Alibaba Cloud voice-cloning guide](https://help.aliyun.com/en/model-studio/voice-cloning-user-guide) recommends 10–20 seconds for its listed cloud models, with a maximum of 60 seconds; the open-source demo may expose different model-specific controls.

After the presenter supplies the sample:

1. Check that it is intelligible and free of distracting clipping, echo, or long silence.
2. Select voice cloning rather than voice design or a stock voice. Provide the sample and its actual transcript.
3. Generate only scene 1 as a listening test. Confirm voice similarity, English intelligibility, and the pronunciation of ReproScout before generating the rest.
4. Generate the ten scenes separately, preserving the same voice and settings. Download each approved segment.
5. Check difficult words and numbers: scikit-learn, Docker, R-squared, two thousand five hundred forty-eight point zero seven, and MIT one point one two five. If necessary, use pronunciation-friendly text for synthesis while retaining proper spelling in subtitles.
6. Assemble audio and real footage, adjust scene lengths, and then align subtitles. Do not publish recording samples or voice credentials with the source repository.

The presenter supplied a voice sample and authorized its use for Qwen cloning. A scene-one listening test completed through the official online demo with the 1.7B voice-cloning model, English output, and the supplied reference transcript. The reference was converted to mono 24 kHz WAV with a 9 dB gain; the original recording was preserved. The generated sample has not yet been approved by the presenter. The reference recording and generated audio stay under ignored private storage. No model weights have been downloaded and no voice-service subscription has been purchased. If the demo is unavailable or cannot export usable audio, evaluate the cloud API with the presenter’s service access before incurring charges; do not silently switch to local model downloads.

## Completion checklist

- The spoken script matches the selected footage and the final deployment status.
- Import, execution, evidence inspection, review, and offline report navigation are all visible.
- Any shortened waiting period and any retained-run replay are labeled.
- Cost labels say estimated model cost, and browser-run metrics are not mixed with CI metrics.
- Assistant review attribution remains visible.
- Voice similarity and pronunciation have been approved by the presenter after a short sample.
- Captions are aligned to the approved audio; scene estimates are not passed off as final timing.
- No access codes, keys, private tabs, or original voice samples appear in the deliverable.
- The final card identifies AI-cloned narration only if that narration is actually used.
- Export a final MP4, an SRT or VTT caption file, and a thumbnail after audio and footage approval. No final video or captions are claimed at this stage.
