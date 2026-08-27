# Before and after

Ten rewrites, each showing the prohibition and the action that replaces it. Every
pair is self-contained, so any one of them reads correctly on its own.

---

## 1. Output format

The example Anthropic's own prompting guide leads with.

**Before**

```text
Do not use markdown in your response.
```

**After**

```text
Your response should be composed of smoothly flowing prose paragraphs.
```

The ban names a format to suppress. The rewrite names the format to produce, so
there is something to aim at rather than something to remember to avoid.

---

## 2. File handling in an agent rules file

**Before**

```text
NEVER create new files. Do not write documentation unless asked.
Don't add comments to code you didn't write.
```

**After**

```text
Edit existing files in place. Write documentation when the user requests it.
Comment only the code you author in this change.
```

Three prohibitions become three scoped permissions. The agent now knows what its
allowed move is at each decision point.

---

## 3. Response length

**Before**

```text
Don't be verbose. Keep it short.
```

**After**

```text
Answer in 4 sentences or fewer.
```

"Short" has no target a model can check itself against. A sentence count does.
This is the single highest-value rewrite in the set, and the one most prompts
need.

---

## 4. Opening lines

**Before**

```text
No pleasantries. Do not restate my question. Never start with "Sure" or
"Certainly".
```

**After**

```text
Open with the answer itself.
```

Four words replace three prohibitions, because naming the wanted opening rules
out every unwanted one at once.

---

## 5. Tool use before answering

**Before**

```text
Do not guess. Never make up file paths or function names.
```

**After**

```text
Read the file before describing it. Quote paths and function names from what
you read.
```

The rewrite names the procedure that makes guessing unnecessary, rather than
naming the failure and hoping it is recognised in the moment.

---

## 6. Scope control

**Before**

```text
Do not refactor unrelated code. Do not add error handling for cases I did not
mention. Avoid adding dependencies.
```

**After**

```text
Change only the lines the task requires. Handle the error cases named in the
task. Build with the dependencies already in the manifest.
```

---

## 7. Structured output

**Before**

```text
Do not include any text outside the JSON object. Do not wrap it in a code
fence.
```

**After**

```text
Reply with a single bare JSON object as the entire response.
```

"As the entire response" carries both prohibitions, because a fence and a
preamble are each something outside the object.

---

## 8. Tone in a changelog

**Before**

```text
Do not use marketing language. Avoid words like "seamless", "robust",
"leverage", or "delve".
```

**After**

```text
Describe what changed and what it means for the user, in plain everyday words.
In place of seamless, robust, leverage, and delve, pick their ordinary synonyms.
```

Naming the banned words is unavoidable here. Rule 7 still applies to the rest:
"marketing language" becomes a positive description of the wanted register.

---

## 9. Closing lines

**Before**

```text
Do not end with "let me know if you have any questions" or offers of further
help.
```

**After**

```text
End on the final substantive sentence.
```

---

## 10. A safety line that stays as it is

**Before**

```text
Never generate working exploit code for a vulnerability in third-party software.
```

**After**

```text
Never generate working exploit code for a vulnerability in third-party software.
```

Unchanged, and flagged for the human. This is rule 8. Recasting it as "generate
only defensive security code" trades a hard boundary for a soft preference, and
that is a downgrade. When a line's status is uncertain, yesand keeps it and says
so.

---

## Applying these

Hand the block to an agent with yesand installed:

> Rewrite the instructions in `CLAUDE.md` into positive form.

The reply carries the rewritten block plus a `was → now` line for each change,
so every edit is reviewable before it lands.
