# 更新日志

所有重要变更记录于此。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循[语义化版本](https://semver.org/lang/zh-CN/)。

## [1.0.0] - 2026-10-20

### 新增

- 首个公开版本。
- 定点剥离核心 system prompt 里两句会逼出客服腔的指令（`never return an empty response`、`briefly explain the purpose when starting a new type of task`），只动有害的两句，其余工具说明保留。
- 剥离项与追加内容都可配置（`strip_phrases` / `append_prompt`），支持 `debug` 查看每轮剥离明细。
- 只改 system prompt，不动人格与历史。
