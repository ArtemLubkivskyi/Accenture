# Flappy Bird: one model, with and without an agent

The Block 6 demo, small enough to try yourself. The same model writes the same game twice: first from a single request, then inside OpenCode, a coding agent that writes the file, checks it, and takes corrections.

The model is Qwen3.5 4B, the capstone model. Two files here go into the folder you work in: `AGENTS.md` (the instruction file the agent reads) and `opencode.json` (where OpenCode finds the model, through Ollama or through llama.cpp).

You need Python 3 and a browser, plus Ollama or llama.cpp. For step 2 also OpenCode (https://opencode.ai) and Node.js, which the agent uses to check its script.

The prompt, used in both steps:

```
Create a playable Flappy Bird clone in one file, index.html, in this folder: plain HTML canvas and JavaScript, no libraries. Space or click flaps, show the score, game over on collision, click to restart.
```

## 0. Start the model server

With Ollama (the capstone setup). The desktop app on Windows and macOS starts the server for you. On Linux, or if the `curl` below says the connection was refused, start it in its own terminal:

```bash
ollama serve
```

In a second terminal, check that it answers and that the model is there:

```bash
curl http://localhost:11434/api/version
ollama pull qwen3.5:4b-q4_K_M
```

Or with llama.cpp, if you have a build of `llama-server`. This downloads the same model from Hugging Face on first start and serves it on port 8080, with thinking off and a context big enough for step 2:

```bash
llama-server -hf unsloth/Qwen3.5-4B-GGUF:Q4_K_M -c 32768 --reasoning off --port 8080
```

## 1. The model alone

One request, no agent. The Python part pulls the HTML out of the reply and saves it.

```bash
mkdir flappy && cd flappy
P='Create a playable Flappy Bird clone in one file, index.html, in this folder: plain HTML canvas and JavaScript, no libraries. Space or click flaps, show the score, game over on collision, click to restart.'
curl -s http://localhost:11434/v1/chat/completions -H "content-type: application/json" \
  -d "$(python3 -c 'import json,sys; print(json.dumps({"model":"qwen3.5:4b-q4_K_M","reasoning_effort":"none","messages":[{"role":"user","content":sys.argv[1]+" Output only the HTML file in one code block."}]}))' "$P")" \
  | python3 -c 'import json,re,sys; t=json.load(sys.stdin)["choices"][0]["message"]["content"]; m=re.search(r"```(?:html)?\n(.*?)```",t,re.S); open("alone.html","w").write(m.group(1) if m else t)'
```

With llama.cpp, send the same request to `http://localhost:8080/v1/chat/completions`; the model name in the request does not matter there.

Open `alone.html` in the browser and play for a while: pipes can take a few seconds to arrive. Run it a few times. Some games work; some show a blank canvas, a script error, or pipes that never appear because they move far too slowly. On a GPU a run takes under a minute; on a laptop CPU expect several minutes.

## 2. The same model inside OpenCode

An agent needs a long context, because its own instructions and tool descriptions take thousands of tokens before your prompt. With Ollama, make a 32k-context variant of the model once (the llama.cpp command above already sets 32k):

```bash
printf 'FROM qwen3.5:4b-q4_K_M\nPARAMETER num_ctx 32768\n' > Modelfile
ollama create qwen3.5-4b-32k -f Modelfile
```

Copy `AGENTS.md` and `opencode.json` from this folder into `flappy/`, make it a git repository (OpenCode's `/undo` needs git), and start OpenCode:

```bash
git init && git add -A && git commit -m "start"
opencode
```

It starts with the Ollama model. With llama.cpp, pick "Qwen3.5 4B, llama-server" with `/models`. Paste the prompt. Open `index.html`, play, and commit what works. Then ask for a change and read the diff before you trust it:

```
Make it harder over time: every 5 points the pipes move 10% faster.
```

```bash
git diff
```

Two things went wrong in our runs, and both passed the agent's own syntax check: a speed-up that ran on every frame instead of once per 5 points, and a pipe speed written in pixels per frame but applied per second, so the pipes crawled in from off-screen. Tell the agent exactly what is wrong; that usually fixes it in one or two turns. If it doesn't after two corrections, `/undo` and ask again from a clean state.

Be realistic about a laptop. On a GPU each OpenCode turn took 10 to 35 seconds; on a CPU an agent turn has to read thousands of tokens of instructions first and can take minutes. A 4B model also loses track as an agent more often than larger ones: it may skip parts of the game or retry the same command. Step 1 is the part to try on a 16 GB laptop; step 2 is worth it with a GPU or a Mac with 32 GB or more.

Useful OpenCode commands: `/thinking` shows the model's reasoning as it works (for models that think), `/models` switches model, `/undo` and `/redo` undo or restore the last turn and its file changes, `/new` starts a fresh session, `tab` switches between the `build` agent and the `plan` agent, which reads and plans without editing. OpenCode edits files and runs commands without asking by default; see https://opencode.ai/docs/permissions to change that.
