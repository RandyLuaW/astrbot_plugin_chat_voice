# 去掉「禁止空回复 / 必须播报工具」的客服腔

> AstrBot 插件 · 定点剥离核心 system prompt 里会逼出客服腔的两句话

## 它解决什么问题

AstrBot 核心会往 system prompt 里追加一段工具调用说明，其中有两句在群聊里是有害的：

- `never return an empty response`（禁止空回复）→ 逼出「没话找话」
- `briefly explain the purpose when starting a new type of task`（说明工具用途）→ 逼出「我先帮你查一下」

这两句追加在人格之后，权重比人格更高。光靠人格提示压不住——人格写「别解释」，它上面还有一条「必须解释」。

结果就是：群里明明是闲聊，她也先来一句「我先看看」，查完再汇总一遍结果，像个客服。

## 做法

`on_llm_request` 里对 system prompt 做**定点字符串替换**：

1. 精确匹配并剥离上面两句（含标点与空格，配置项可改）
2. 追加一段群聊版要求：*工具调用前后不要向群友说明你在做什么，也不要汇总返回结果；查完直接把结论说进对话里。无话可说时可以什么都不说。*

只动有害的两句，其余工具说明保留——那些确实有助于正确调用工具。

## 安装

### 方式一：插件市场（推荐）

WebUI 插件市场搜索「群聊语气矫正」。

### 方式二：Releases 下载

从 [Releases](../../releases) 下载 zip，WebUI → 插件 → 上传安装。

### 方式三：手动克隆

```bash
cd AstrBot/data/plugins
git clone https://github.com/RandyLuaW/astrbot_plugin_chat_voice.git
```

无额外依赖。

## 配置项

| 键 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `enable` | bool | `true` | 总开关，关闭后不动 system prompt |
| `strip_phrases` | list | 见下 | 要剥离的原文片段，精确匹配（含标点与空格） |
| `append_prompt` | text | 见下 | 剥离后追加的群聊版要求，留空则不追加 |
| `debug` | bool | `false` | 输出每轮剥离明细（剥了几处、prompt 长度变化） |

默认 `strip_phrases`：

```
never return an empty response; 
briefly explain the purpose when starting a new type of task, but not before every tool call; 
```

默认 `append_prompt`：

```
工具调用前后不要向群友说明你在做什么，也不要汇总返回结果；查完直接把结论说进对话里。无话可说时可以什么都不说。
```

## 调参建议

- **升级 AstrBot 后不生效了**：核心改了措辞，把 `debug` 打开看实际 prompt，把新措辞加进 `strip_phrases`
- **她变得太沉默**：`append_prompt` 里「无话可说时可以什么都不说」可以删掉半句
- **想完全不动 prompt**：`enable: false`

## 注意事项

- 剥离是**字符串精确匹配**，核心文案一变就会失效——这是刻意的：宁可失效也不要模糊匹配误伤其他内容
- 只影响 system prompt，不改人格、不改历史
- 依赖 `on_llm_request` 钩子，AstrBot `>= 4.17.0`

## License

MIT
