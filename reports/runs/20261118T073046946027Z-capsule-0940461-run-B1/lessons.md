# Frozen workflow lessons, revision 2

These are conditional workflow reminders, not answers or permission to change the
scientific method. They were revised after an exposed-cohort error analysis and
must be validated on official training tasks before formal use.

1. **Establish the execution path cheaply.** List the code directory and read the
   available instructions, including /REPRODUCING.md. Read missing optional files
   separately so they cannot block required instructions. Use the supplied runtime
   and entry point. Follow the tool schema exactly: shell accepts only `command`;
   do not send unsupported timeout arguments. Quote embedded scripts so shell
   expansion cannot corrupt their variables.

2. **Separate computation from presentation.** Run the author's computation and
   inspect the generated outputs before spending calls on packaging or rendering.
   For notebooks, write the executed copy under /results, preserve all code cells,
   and read targeted output cells. A rendering failure need not invalidate already
   computed answers. Do not alter scientific code or data, including copied files,
   change exclusions or formulas, fabricate intermediates, or substitute a rewritten
   analysis. If execution needs a scientific change, report that blocker.

3. **Investigate a blocker only where it matters.** Inspect the failing loader and
   its expected local path once; check bundled data and documented cache behavior.
   Missing output formatting software is different from missing scientific input.
   Avoid repeated internet attempts and whole-filesystem searches. Preserve valid
   answers for unaffected questions; use null only where evidence is unavailable.
   Do not assume that an unrelated missing dependency invalidates every question.

4. **Match the question to computed evidence.** Identify the requested population,
   conditions, metric, and output before choosing a table row. Similar labels in a
   different table are not interchangeable. Use generated figures for visual
   questions, and trace their labels to the corresponding computed quantities.
   A focused read-only query of objects produced by unmodified author code is
   acceptable; rerun unchanged code only if those objects are otherwise unavailable.
   Do not infer a result from manuscript prose or invent a replacement computation.

5. **Reserve time to submit and check the value type.** There are twenty model
   calls, including unsuccessful tool calls and the final submission. Reserve the
   last two for evidence checks and submit_report; do not spend them on optional
   rendering repairs or repeated inspection. For a numeric question, put a JSON
   number in `value`, using the requested scale. Keep units and explanations outside
   that scalar; when told to ignore units, omit them. Preserve required text/list
   types for nonnumeric questions. Cite output from this run supporting each value;
   if the evidence does not support an answer, submit null with the blocker.
