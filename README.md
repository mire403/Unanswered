# 🧠 Unanswered – 没人回答的问题

> **Automatically find questions that were asked but never answered – 不生成答案，只帮你找到「被遗忘的问题」。**

---

## 💡 项目简介 / Product Overview

在日常协作中，我们经常遇到这种情况：

- 代码评审里有人问了一个关键问题，后面聊着聊着就跑题了 🤯  
- 会议记录一大坨，谁在什么时候问了什么、到底有没有人正面回应，完全看不出来 😵  
- 产品 / 技术设计文档下面一堆评论，哪些「问题」已经有结论，哪些其实没人回答 ❓

**Unanswered（没人回答的问题）** 的目标就是：

- **输入**：一段按时间排序的长讨论文本（Issue / PR 评论、群聊记录、会议记录、技术讨论等等）  
- **输出**：一份 **结构化列表**，告诉你：
  - 🗣 **问题内容**：问了什么？
  - 👤 **是谁问的**：哪个人提问？
  - ⏰ **什么时候问的**：大致时间或顺序位置
  - ✅ **是否被回答**：已回答 / 部分回答 / 未回答 / 不确定
  - 📎 **证据**：哪些后续消息被判定为（未）回答  

👉 **核心哲学：这不是一个「回答问题」的 AI，而是一个「发现没人回答的问题」的 AI。**

---

## 🎯 设计原则 / Design Principles

**特别重要的几个原则：**

- ❌ **绝不胡编乱造问题**（No hallucinated questions）  
- ✅ **问题必须是显式的**：
  - 带问号 `?`  
  - 或使用明显的疑问语气：why / how / what / should we / 能不能 / 要不要 / 怎么办 / 为啥 等  
- ✅ **回答必须：**
  - 明确地回应该问题的内容（语义上对得上）  
  - 出现在问题之后（时间上有先后）  
- 🚫 **话题漂移不算回答**：如果后面聊嗨了、换话题了，哪怕提到了类似的词，也不能算是回答  
- 😌 **宁可漏掉一些问题，也不要误报**：
  - **保守判定**：如果模型不够确定，就标记为「未回答 / 不确定」  

---

## 🧩 核心功能 / Core Capabilities

1. **问题检测（Question Detection）**
   - 对每条消息 / 句子进行：`问题 / 非问题` 分类  
   - 识别多种形式的提问：是 / 否、开放式、澄清、决策等  
   - 支持识别 **修辞性问题**（如「谁会去干这个啊？」），并排除  

2. **问题类型识别（Question Typing）**
   - 🧼 Clarification（澄清类）：「这个字段具体是什么意思？」  
   - 🤝 Decision（决策类）：「我们要不要在 v1 支持多租户？」  
   - 🛠 Technical（技术实现类）：「这个查询有没有办法加索引优化？」  
   - 🌈 Open-ended（开放讨论类）：「大家对这个方案有什么担心吗？」  
   - 🙃 Rhetorical（修辞性）：识别后排除  

3. **回答匹配（Answer Matching）**
   - 仅在 **问题之后** 的消息中寻找候选回答  
   - 使用语义相似度和 LLM **判定是否是「直接回答」**  
   - 使用 **高阈值** 相似度，宁可漏判也不误判  

4. **状态判定（Resolution Judgment）**
   - ✅ `answered`：有明确、直接的回答  
   - 🌓 `partially_answered`：部分答到点，但仍然有明显空白  
   - ⛔ `unanswered`：没有任何消息真正回应  
   - 🤔 `uncertain`：信息不足 / 语义太模糊，模型不敢拍板  

5. **结果报告（Report Generation）**
   - 支持 **Markdown / JSON / checklist** 等输出形式  
   - 适配后续场景：VS Code / Cursor 插件、GitHub Action、会议助手等  

---

## 🏗 架构设计 / System Architecture

整体采用 **模块化流水线（pipeline）** 设计，方便替换和扩展：

```text
[raw text] 
   ↓ ingest.py        （解析原始文本，标准化为 Utterance）
   ↓ segment.py       （句子 / 对话轮次切分）
   ↓ question_detector.py  （LLM 逐条判定是否为问题 + 问题类型）
   ↓ question_type.py      （进一步细分类型 / 过滤修辞性问题）
   ↓ answer_matcher.py     （基于语义相似 + LLM 进行回答匹配）
   ↓ resolver.py           （汇总某个问题的回答情况，给出状态）
   ↓ outputs/formatter.py  （导出为 Markdown / JSON / checklist）
```

> 核心思想：**LLM 只做「判官」（classification / verification），而不是「作者」（generation）。**

---

## 📂 目录结构 / Project Structure

```text
unanswered/
  core/
    ingest.py           # 解析 & 规范化讨论文本（Raw → Utterance）
    segment.py          # 句子 / 轮次切分（可扩展为更细粒度）
    question_detector.py# 检测问题（LLM 判定）
    question_type.py    # 问题类型 & 修辞性过滤
    answer_matcher.py   # 回答候选匹配 & 相似度计算
    resolver.py         # 最终 answered/partially/unanswered 判断
  llm/
    client.py           # LLM 客户端抽象（只做 JSON 判定）
    prompts.py          # 问题检测 & 回答验证 Prompt 模板
  schemas/
    question.py         # 核心数据结构：Utterance / Question / Resolution
  outputs/
    formatter.py        # Markdown / JSON / checklist 输出
  main.py               # 端到端运行入口示例
  README.md
```

---

## 🧱 核心数据结构 / Schemas（简要示例）

项目使用 `dataclasses` 来定义核心结构（位于 `schemas/question.py`）：

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class QuestionType(str, Enum):
    CLARIFICATION = "clarification"
    DECISION = "decision"
    TECHNICAL = "technical"
    OPEN_ENDED = "open_ended"
    RHETORICAL = "rhetorical"


class ResolutionStatus(str, Enum):
    ANSWERED = "answered"
    PARTIALLY_ANSWERED = "partially_answered"
    UNANSWERED = "unanswered"
    UNCERTAIN = "uncertain"


@dataclass
class Utterance:
    id: int
    speaker: Optional[str]
    timestamp: Optional[str]
    text: str
```

### 设计要点解析 🔍

- `Utterance` 把「一条消息」标准化，不管来自 GitHub、Slack 还是会议转写；  
- `QuestionCandidate` 代表「被检测为问题的那句话」，携带提问者和时间信息；  
- `QuestionCluster` 用于合并高度相似 / 重复的问题；  
- `QuestionResolution` 是最终你要看的结构：**问题内容 + 问的人 + 时间 + 状态 + 证据**。  

这种设计方便后续：

- 做跨平台适配（只要统一成 `Utterance` 即可）  
- 针对某个阶段做 A/B 实验（比如替换不同的 question detector / matcher）  

---

## 🤖 LLM Prompt 设计 / Prompt Design

> **关键原则：LLM 只负责「判定」，不负责「创作」。不允许它「总结讨论」。**

### 1️⃣ 问题检测 Prompt（Question Detection）

系统提示（节选，位于 `llm/prompts.py`）：

```python
QUESTION_DETECTION_SYSTEM_PROMPT = """
You are an expert analyst that finds explicit questions inside technical and product discussions.

CRITICAL RULES:
- Do NOT invent or hallucinate questions.
- Only mark something as a question if:
  - It has a clear question mark "?" OR
  - It uses interrogative intent (why, how, what, when, where, who, should, can, could, would, is, are, do, does, did, may, might) AND is clearly seeking information or a decision.
- Ignore rhetorical questions that are clearly not expecting an answer.
- Be conservative: if uncertain, classify as NOT_QUESTION.

You receive ONE utterance (single message) at a time, not the whole thread.
You must classify the utterance as QUESTION or NOT_QUESTION and provide minimal reasoning flags.

OUTPUT FORMAT (JSON, no extra text):
{
  "is_question": true | false,
  "is_rhetorical": true | false,
  "question_type": "clarification" | "decision" | "technical" | "open_ended" | "rhetorical" | null,
  "reason_flags": [
    "contains_question_mark" | "starts_with_wh_word" | "yes_no_question" |
    "ambiguous" | "rhetorical_cue" | "no_interrogative_signal"
  ]
}
""".strip()
```

用户提示模板：

```python
QUESTION_DETECTION_USER_TEMPLATE = """
Utterance:
\"\"\"{text}\"\"\"

Classify this utterance according to the instructions.
Return ONLY the JSON object.
""".strip()
```

**解析：**

- 只给 LLM 一条 `utterance`，避免它「看前后文」后脑补问题；  
- 强调「不允许胡编问题」和「保守策略」；  
- 输出固定 JSON 字段，便于代码做严格解析 & 校验；  
- `reason_flags` 记录判定线索，方便后续调试、可视化。  

### 2️⃣ 回答验证 Prompt（Answer Verification）

系统提示（节选）：

```python
ANSWER_VERIFICATION_SYSTEM_PROMPT = """
You are an expert judge that checks whether a set of later messages actually answer a specific question.

You MUST follow these rules:
- You do NOT generate any new answers.
- You only judge if the existing messages answer the question.
- An answer must directly address the question.
- The answer must appear AFTER the question in time.
- Topic drift, partial side-comments, or unrelated discussion do NOT count as answers.
- Be conservative: if you are not sure, say the question is UNANSWERED or PARTIALLY_ANSWERED.

OUTPUT FORMAT (JSON, no extra text):
{
  "status": "answered" | "partially_answered" | "unanswered" | "uncertain",
  "answer_utterance_ids": [list of integer ids that provide direct answers],
  "reason_flags": [
    "direct_answer_found" | "partial_answer_found" | "no_relevant_message" |
    "only_topic_drift" | "conflicting_answers" | "insufficient_information"
  ]
}
""".strip()
```

用户提示模板：

```python
ANSWER_VERIFICATION_USER_TEMPLATE = """
Question:
\"\"\"{question_text}\"\"\"

Candidate later utterances (chronological order):
{utterance_block}

Each utterance is formatted as:
[id=<id>] <speaker_or_unknown>: <text>

Judge whether these utterances answer the question according to the rules.
Return ONLY the JSON object.
""".strip()
```

**解析：**

- 明确约束：**不能生成新答案**，只能「判定已存在的文本是否构成回答」；  
- 明确「时间方向」：只看 **问题之后** 的消息；  
- Explicitly 要求 `status` 只能是四种之一，并带上 `answer_utterance_ids` 证据；  
- 同样用 `reason_flags` 便于后续分析：是完全没找到、还是只有话题漂移？  

---

## 🧮 LLM Client 设计 / LLM Client

`llm/client.py` 提供一个极简抽象层，只做两件事：

1. 调用底层 LLM API（待你接入 OpenAI / Anthropic / Moonshot / 自研等）；  
2. 强制要求返回 **合法 JSON**，否则抛异常（防止静默 hallucination）。  

```python
from dataclasses import dataclass
import json
from typing import Any, Dict


@dataclass
class LLMConfig:
    model: str = "gpt-4.1-mini"


class LLMClient:
    def __init__(self, config: LLMConfig | None = None):
        self.config = config or LLMConfig()

    def _call_raw(self, system_prompt: str, user_prompt: str) -> str:
        # TODO: 在这里接 OpenAI / Anthropic / 其他 LLM
        raise NotImplementedError

    def classify_question(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        raw = self._call_raw(system_prompt, user_prompt)
        return json.loads(raw)

    def verify_answer(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        raw = self._call_raw(system_prompt, user_prompt)
        return json.loads(raw)
```

**解析：**

- 上层逻辑完全不知道用的是哪家模型 → 方便切换 / A/B 测试；  
- 强制 JSON 解析 → prompt 明确要求只返回 JSON，降低「啰嗦自然语言」的风险；  
- 可以进一步加 **重试 / schema 校验 / 观测日志** 等。  

---

## 🚀 使用方式 / Usage (示例)

> ⚠️ 说明：以下是典型用法示例，具体以你的 `main.py` 实现为准。建议提供一个简单 CLI：读取文本文件 → 输出 Markdown / JSON。

### 1️⃣ 安装依赖

```bash
pip install -r requirements.txt
```

（你可以根据实际需要加入：`openai`, `tiktoken`, `numpy`, `scikit-learn`, `sentence-transformers` 等。）

### 2️⃣ 准备一个讨论文本文件

例如 `examples/discussion.txt`：

```text
Alice: Should we add rate limiting to this endpoint?
Bob: I think the current traffic is still low.
Charlie: We also need to consider abuse scenarios.
Bob: Anyway, let's ship it first and see.

Alice: Another question: who owns the incident response runbook?
Bob: ...
```

### 3️⃣ 运行（示意性 main.py）

```python
# main.py (简化示例)
from unanswered.core.ingest import parse_lines
from unanswered.core.segment import segment_utterances
# from unanswered.core.question_detector import detect_questions   # 由你实现
# from unanswered.core.answer_matcher import match_answers         # 由你实现
# from unanswered.core.resolver import resolve_questions           # 由你实现
# from unanswered.outputs.formatter import format_markdown         # 由你实现


def run_on_file(path: str):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    utterances = parse_lines(lines)
    utterances = segment_utterances(utterances)

    # questions = detect_questions(utterances)
    # matched = match_answers(questions, utterances)
    # resolutions = resolve_questions(matched)
    # print(format_markdown(resolutions, utterances))

    print(f"Loaded {len(utterances)} utterances. Further pipeline steps TBD.")


if __name__ == "__main__":
    import sys

    run_on_file(sys.argv[1])
```

运行：

```bash
python -m unanswered.main examples/discussion.txt
```

---

## 📊 输出示例 / Example Output（Markdown 形式）

```markdown
## ❓ Unanswered Questions

1. [UNANSWERED] Should we add rate limiting to this endpoint?
   - Asker: Alice
   - Asked at: (unknown)
   - Type: decision
   - Evidence:
     - Later messages discuss traffic and abuse scenarios, but no one explicitly decides yes/no.

2. [UNANSWERED] Who owns the incident response runbook?
   - Asker: Alice
   - Asked at: (unknown)
   - Type: clarification
   - Evidence:
     - No later message mentions "runbook" or ownership.
```

同样可以导出 JSON，便于前端集成 / GitHub Action / VS Code 插件消费。

---

## 🔌 未来扩展 / Future Extensions

- 🧩 **IDE / Editor 插件**
  - VS Code / Cursor：在 PR 或设计文档侧边栏展示「没人回答的问题」清单  
  - 支持「点击跳转到原文位置」  

- 🐙 **GitHub Action**
  - 对 PR / Issue 评论流跑一遍 pipeline  
  - 在 Checks / Comment 中列出「未回答问题」提醒 reviewer / 作者  

- 🗣 **会议助手**
  - 对会议转录文本进行分析  
  - 会后生成「没人被回答的问题」列表，推动后续 follow-up  

- 📈 **团队洞察**
  - 哪些项目 / 模块里「没人回答的问题」最多？  
  - 哪些人提问后经常没人回复？（需要提醒改善协作氛围）  

---

## 🧭 设计总结 / Design Summary

- **Not another Q&A bot**：它不代替人回答问题，只负责指出「谁的问题被大家遗忘了」。  
- **Conservative & explainable**：宁可漏，不能乱报；每个判定都尽量给出 `reason_flags` 和证据。  
- **Modular & extensible**：各阶段解耦，方便替换模型、切换 embedding、接不同平台。  
- **Verification-oriented LLM**：LLM 只做「是否是问题」「是否被回答」等判定，不参与内容生成。  

如果你想把这个项目打造成一个真正可用的 **「协作盲点雷达」**，这个 README 可以作为设计与实现的起点 🚀  

