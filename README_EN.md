# Strip the "never return an empty response" customer-service voice

> AstrBot plugin · surgically removes two lines from the core system prompt that force a support-agent tone

## The problem

AstrBot core appends tool-usage instructions to the system prompt. Two of those lines are harmful in group chat:

- `never return an empty response` → forces the model to say *something* even when there's nothing to say
- `briefly explain the purpose when starting a new type of task` → forces "let me look that up for you first"

Both are appended **after** the persona, so they outrank it. Telling the persona "don't explain yourself" doesn't help — there's still a line above it saying "you must explain".

Result: in casual group chat she opens with "let me check", then summarizes the tool output, like a support agent.

## How it works

On `on_llm_request`, the plugin does a **targeted string replacement** on the system prompt:

1. Exact-match and strip the two lines above (punctuation and trailing spaces included; configurable)
2. Append a group-chat-friendly instruction: *don't announce what you're doing before/after tool calls, don't summarize tool output — put the conclusion straight into the conversation; silence is fine.*

Only the harmful lines are removed. The rest of the tool instructions stay — they genuinely help correct tool usage.

## Install

### Option 1: Plugin marketplace (recommended)

Search "群聊语气矫正" in the AstrBot WebUI plugin marketplace.

### Option 2: Download from Releases

Grab the zip from [Releases](../../releases), then WebUI → Plugins → Upload.

### Option 3: Clone manually

```bash
cd AstrBot/data/plugins
git clone https://github.com/RandyLuaW/astrbot_plugin_chat_voice.git
```

No extra dependencies.

## Configuration

| Key | Type | Default | Description |
|---|---|---|---|
| `enable` | bool | `true` | Master switch; when off the system prompt is untouched |
| `strip_phrases` | list | see below | Exact phrases to strip (punctuation and spaces matter) |
| `append_prompt` | text | see below | Instruction appended after stripping; empty = append nothing |
| `debug` | bool | `false` | Log per-turn details (how many strips, prompt length delta) |

Default `strip_phrases`:

```
never return an empty response; 
briefly explain the purpose when starting a new type of task, but not before every tool call; 
```

Default `append_prompt` (Chinese; replace with your own language):

```
工具调用前后不要向群友说明你在做什么，也不要汇总返回结果；查完直接把结论说进对话里。无话可说时可以什么都不说。
```

## Tuning

- **Stopped working after an AstrBot upgrade**: core reworded the lines. Turn on `debug`, inspect the actual prompt, add the new wording to `strip_phrases`.
- **She's too quiet now**: drop the "silence is fine" half of `append_prompt`.
- **Don't touch the prompt at all**: set `enable: false`.

## Notes

- Matching is **exact string** by design: if core changes wording the plugin silently stops working rather than fuzzy-matching something it shouldn't.
- Only the system prompt is modified — persona and history are untouched.
- Requires the `on_llm_request` hook, AstrBot `>= 4.17.0`.

## License

MIT
