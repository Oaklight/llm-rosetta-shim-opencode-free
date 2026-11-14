# llm-rosetta-shim-free

Keyless free LLM endpoints for [llm-rosetta](https://github.com/Oaklight/llm-rosetta),
delivered as a plugin package. Every shim here serves a free pool that needs no
account:

| Shim | Vendor | Default Base URL | Credential |
|:---|:---|:---|:---|
| `kilo_free--chat_completions` | Kilo Code | `https://api.kilo.ai/api/gateway` | none (keyless) |
| `llm7--chat_completions` | LLM7.io | `https://api.llm7.io/v1` | none (keyless) |
| `opencode_zen_free--chat_completions` | OpenCode (Zen) | `https://opencode.ai/zen/v1` | none (keyless) |
| `ovhcloud--chat_completions` | OVHcloud AI Endpoints | `https://oai.endpoints.kepler.ai.cloud.ovh.net/v1` | none (keyless) |

All four are OpenAI Chat Completions lanes.

This repository was `llm-rosetta-shim-opencode-free` and shipped only the
OpenCode Zen lane. It was renamed when the other keyless pools joined it. The
OpenCode shim's name did not change, so a config written for the old package
keeps working after its preset declaration is switched to `free`.

## Where these come from — and what they are not

These endpoints are a **collection from public sources**, not original research.
Some came from
[**awesome-free-llm-apis**](https://github.com/mnfst/awesome-free-llm-apis), a
community list of LLM APIs with permanent free tiers. Others were inspired by,
or adapted from, other open-source projects that catalogue free endpoints or
integrate with them. Credit for the discovery belongs to those projects and
their authors; this repository only turns the result into shims, and every shim
was probed directly before it was written.

Because the sources are mixed, this package is deliberately not the authority on
any of them: check the upstream's own documentation for the current roster,
limits and terms.

**This is a collection, not an endorsement.** Neither this project nor its
author is affiliated with, approved by, or partnered with any of these vendors,
and nothing here should be read as a statement about their quality.

**Use at your own risk.** In particular:

- **Nothing here guarantees zero data retention.** Free tiers are exactly the
  tiers most likely to retain prompts, log them for abuse review, or use them to
  improve a product. If ZDR, residency, a DPA or a subprocessor list matters to
  you, read that vendor's own terms and privacy policy and decide for yourself.
  A shim saying `keyless` says nothing about what the upstream does with your
  data.
- **Terms, roster and rate limits belong to the upstream** and can change or
  close without notice. A shim that worked yesterday may fail today; that is not
  a defect in this package.
- **The author holds no responsibility for any consequence** of using these
  endpoints — data loss or disclosure, cost, account suspension, or a breach of
  an upstream's terms.
- **You are responsible for compliance** with the terms you accept, with the law
  where you and your users are, and with any obligation you owe your own users.

If an upstream asks to be removed, its shim is withdrawn.

<details>
<summary>中文说明</summary>

本仓库收录的接口来自**公开渠道的汇总**，不是原创调研。其中一部分来自
[**awesome-free-llm-apis**](https://github.com/mnfst/awesome-free-llm-apis) ——
一个社区维护的「有永久免费额度的 LLM API」清单；另一部分参考或改编自其他开源项目
（收录免费端点的清单类项目、以及集成这些端点的客户端项目）。发现的功劳属于这些项目
及其作者，本仓库只把结果落成 shim，并在写入前逐条实测。

正因为来源是混合的，本包不对任何一条做权威担保：模型清单、限额与条款以上游自己的文档为准。

**这里是收集，不是背书。** 本项目及作者与这些厂商没有任何隶属、授权或合作关系，
也不对其服务质量作任何判断。

**风险自负。** 特别提醒：

- **这里不保证零数据保留（ZDR）。** 免费额度恰恰是最可能保留 prompt、为风控留痕、
  或用于改进产品的档位。若 ZDR、数据驻留、DPA 或分处理者清单对你重要，请自行阅读
  该厂商的条款与隐私政策后判断。shim 写着 `keyless`，只说明接口不要求密钥，
  不说明上游如何处理你的数据。
- **条款、模型清单与速率限制归上游所有**，可能随时变更或关闭。昨天可用的 shim
  今天可能失败，这不是本包的缺陷。
- **使用这些端点的任何后果，作者不承担责任** —— 包括数据丢失或泄露、费用、账号
  封禁，或违反上游条款。
- **合规由你负责**：你接受的条款、你与用户所在地的法律，以及你对自己用户的义务。

若上游要求下架，对应 shim 会被撤回。

</details>

## Why these live outside core

Free endpoints belong to their upstream. They change rate limits, rotate their
model roster, and can close without notice. None of the four carries a contract,
so shipping them as a standalone package lets the project withdraw or update
them without a core release. The built-in shims are for vendors whose endpoint
is a product you can depend on.

Kilo is the one vendor that ships on both sides: the paid gateway is the
built-in `kilo--chat_completions` (always sends `KILO_API_KEY`, offers the whole
catalogue), and the keyless pool is `kilo_free--chat_completions` here. Keeping
the two contracts apart is what lets the paid leaf demand a credential.

## Rate limits

- **Kilo**: 200 requests per hour per IP on the free pool.
- **LLM7**: anonymous access reaches the `turbo` models. A free token from
  `token.llm7.io` raises the rate ceiling to 1 RPS / 60 RPM / 250 requests per
  hour / 100,000 tokens per 24 h, and reaches the same models.
- **OpenCode Zen**: the lane is gated to the OpenCode client's request shape;
  see the shim's `transforms.py`.
- **OVHcloud**: 2 requests per minute per IP per model, anonymous. A Public
  Cloud project key raises it to 400 RPM per project per model and bills per
  token.

## What each shim fixes

- **Reasoning field.** LLM7 and OVHcloud put reasoning text on
  `message.reasoning` / `delta.reasoning`, while the Chat Completions converter
  reads `reasoning_content`. Both ship a rename, a no-op when no reasoning is
  present. Kilo's free lane carries no rename: its reasoning field has not been
  probed, and an unverified rename is worse than none.
- **Model roster.** Kilo's and OpenCode's catalogs list the paid models beside
  the free ones; their `model_list_transform`s keep only the free slice. LLM7's
  catalog is typed and tiered, so its transform keeps `model_type: chat` in the
  `turbo` tier. OVHcloud's listing carries no type field and is offered whole.
- **Request shape.** OpenCode's lane refuses a request that does not declare a
  tool named exactly `read`; the shim injects a placeholder declaration and
  removes any call to it from the response.

## Usage with the gateway

Declare the source, then configure a provider for it:

```jsonc
{
  "shims": { "presets": ["free"] },
  "providers": {
    "kilo-free": { "type": "kilo_free--chat_completions" },
    "llm7-free": { "type": "llm7--chat_completions" },
    "ovh-free": { "type": "ovhcloud--chat_completions" }
  }
}
```

`keyless: true` means no `api_key` is required; supplying one switches the same
shim to `Authorization: Bearer <key>`, which is how an operator with a paid
OVHcloud project or an LLM7 token uses the higher limits.

## Privacy

Every endpoint here is a third-party service, and free tiers may log prompts.
Never send secrets or personal data through them.

## License

MIT.
