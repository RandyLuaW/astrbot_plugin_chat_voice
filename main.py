"""群聊语气矫正：剥掉 AstrBot 核心硬编码的「工具提示」，换成群聊版。

问题
----
只要请求里带工具，AstrBot 就会往 system prompt 追加一段固定文案
（`astrbot/core/astr_main_agent_resources.py:25` 的 TOOL_CALL_PROMPT）：

    When using tools: never return an empty response; briefly explain the purpose
    when starting a new type of task, but not before every tool call; follow the
    tool schema exactly and do not invent parameters; keep the conversation style consistent.

对群聊 bot 来说前两句是伤害：
- `never return an empty response` —— 禁止空回复。群里有时候不说话才是最像人的反应，
  这条逼它必须说点什么，制造"没话找话"。
- `briefly explain the purpose` —— 鼓励播报意图，产生"我先帮你查一下"的客服腔。

本插件在 `on_llm_request` 阶段把这些句子从 system_prompt 里摘掉（该钩子在内核
构建完请求之后派发，`pipeline/process_stage/method/agent_sub_stages/internal.py:307`，
所以能改到），再追加一句群聊版的行为要求。

设计原则
--------
- 只做**定点字符串剥离**，不做整段替换：内核文案改字也不会把插件搞崩。
- 剥离项可配置，默认只动那两句有害的；`keep the conversation style consistent`
  这类无害的保留。
- 带 debug 开关，能看到本轮到底剥掉了什么。

与人格的关系
------------
人格（v21）里已经写了"不播报、不汇总、允许沉默"。本插件解决的是**顺序问题**：
内核那段是追加在人格之后的，靠后的指令权重更高，所以光靠人格压不住。
"""

from __future__ import annotations

import re

from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.provider import ProviderRequest
from astrbot.api.star import Context, Star

PLUGIN_NAME = "astrbot_plugin_chat_voice"

DEFAULT_STRIP = [
    "never return an empty response; ",
    "never return an empty response;",
    "briefly explain the purpose when starting a new type of task, but not before every tool call; ",
    "briefly explain the purpose when starting a new type of task, but not before every tool call;",
]

DEFAULT_APPEND = "查完直接说结论，不播报不汇总。没话就不说。"

DEFAULT_CONFIG = {
    "enable": True,
    "strip_phrases": DEFAULT_STRIP,
    "append_prompt": DEFAULT_APPEND,
    "debug": False,
}


class ChatVoicePlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig | None = None) -> None:
        super().__init__(context)
        self.cfg = dict(DEFAULT_CONFIG)
        if config:
            for k, v in dict(config).items():
                if k in DEFAULT_CONFIG:
                    self.cfg[k] = v

    def _enabled(self) -> bool:
        v = self.cfg.get("enable", True)
        if isinstance(v, str):
            return v.strip().lower() in ("1", "true", "yes", "on", "是")
        return bool(v)

    @staticmethod
    def _flag(v) -> bool:
        if isinstance(v, str):
            return v.strip().lower() in ("1", "true", "yes", "on", "是")
        return bool(v)

    @filter.on_llm_request()
    async def clean_tool_prompt(
        self, event: AstrMessageEvent, req: ProviderRequest
    ) -> None:
        """把内核硬编码的工具提示换成群聊版。"""
        if not self._enabled():
            return
        sp = getattr(req, "system_prompt", None)
        if not isinstance(sp, str) or not sp:
            return

        phrases = self.cfg.get("strip_phrases") or []
        if isinstance(phrases, str):
            phrases = [p for p in phrases.split("\n") if p.strip()]

        removed: list[str] = []
        new_sp = sp
        for p in phrases:
            if not p or not isinstance(p, str):
                continue
            if p in new_sp:
                new_sp = new_sp.replace(p, "")
                removed.append(p.strip()[:48])

        if removed:
            # 剥离后可能留下空行，收敛一下
            new_sp = re.sub(r"[ \t]+\n", "\n", new_sp)
            new_sp = re.sub(r"\n{3,}", "\n\n", new_sp).strip() + "\n"

        append = str(self.cfg.get("append_prompt") or "").strip()
        if append and append not in new_sp:
            new_sp = new_sp.rstrip() + "\n" + append + "\n"

        if new_sp != sp:
            req.system_prompt = new_sp

        if self._flag(self.cfg.get("debug")):
            logger.info(
                f"[{PLUGIN_NAME}] 剥离 {len(removed)} 处工具提示"
                f"{'：' + ' | '.join(removed) if removed else ''}"
                f"｜追加群聊版={bool(append)}｜prompt {len(sp)}→{len(new_sp)} 字符"
            )
