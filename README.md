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
