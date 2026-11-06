# llm-rosetta-shim-opencode-free

OpenCode Zen's keyless free lane for
[llm-rosetta](https://github.com/Oaklight/llm-rosetta), delivered as a **plugin
package** rather than as a built-in shim.

The `opencode_zen_free--chat_completions` shim left llm-rosetta core so the
experimental lane can evolve (and be withdrawn) without a core release. Declare
it in the gateway config and use it like any other provider:

```jsonc
{
  "shims": { "presets": ["opencode_zen_free"] },
  "providers": { "zen-free": { "type": "opencode_zen_free--chat_completions" } },
  "models": { "big-pickle": { "provider": "zen-free" } }
}
```

`shims.presets` expands to this repository's archive path via llm-rosetta's
catalogue; the equivalent explicit entry is
`{"url": "https://github.com/Oaklight/llm-rosetta-shim-opencode-free",
"path": "src/llm_rosetta_shim_opencode_zen_free/providers"}`. The repository is
public, so no `token_env` is needed.

## The shim

| Shim | Format | Base URL | Credential |
|:---|:---|:---|:---|
| `opencode_zen_free--chat_completions` | `chat_completions` | `https://opencode.ai/zen/v1` | none (`Bearer public`) |

It reproduces the request shape OpenCode's own client sends — the
`opencode/<version>` User-Agent, the `x-opencode-client` / `x-opencode-project`
markers, a session id in OpenCode's identifier layout, a `read` declaration, and
forced streaming — filters the model listing to the zero-cost slice, and removes
calls to the injected `read` placeholder from the response (a turn whose every
call was removed finishes with `stop`).

## Status: the lane is gated to OpenCode's own client

Measured 2026-11-01, the upstream only answers requests from the OpenCode client
itself. A request that reproduces the client's **body and headers byte for byte**
— captured from a real `opencode` session through a local MITM proxy — is still
refused with `429 FreeUsageLimitError` when sent with curl, Node `https`, Node
`fetch`, Bun `fetch`, or browser-impersonating TLS (curl-impersonate
chrome/firefox/safari), on a host where the genuine client answers in the same
minute. The gate therefore keys on the client's transport (TLS/HTTP stack), not
on anything a shim can set.

`429 FreeUsageLimitError` is also what genuine quota exhaustion returns, so the
two cannot be told apart from the response alone; the only reliable control is
the real client from the same host.

Consequences for this package:

- Treat it as **experimental**. It is kept because the upstream may relax the
  gate, and because the request-shape work (model filter, placeholder tool,
  finish-reason rewrite) is reusable.
- A gateway built on an ordinary HTTP client will most likely receive `429` from
  the lane. Nothing in this repository's configuration changes that.

## Archive and mirror

Every release publishes one archive of the bundled shims, so a gateway can load
them from a host other than GitHub. `main` never carries it: `dist/` is build
output and is in `.gitignore`.

- `v<version>/opencode_zen_free.tar.gz` and `v<version>/opencode_zen_free.tar.gz.sha256` live on the
  orphan `dist` branch.
- The same bytes are attached to the GitHub Release, with the digest in its
  notes.

Two interchangeable, version-pinned URLs for the same bytes:

```
https://github.com/Oaklight/llm-rosetta-shim-opencode-free/releases/download/v<version>/opencode_zen_free.tar.gz
https://cdn.jsdelivr.net/gh/Oaklight/llm-rosetta-shim-opencode-free@dist/v<version>/opencode_zen_free.tar.gz
```

The archive's root is `providers/`, the layout the package ships under
`src/llm_rosetta_shim_opencode_zen_free/providers`, so a gateway source declares `path: "providers"`:

```jsonc
{
  "shims": {
    "remotes": [
      {
        "url": "https://cdn.jsdelivr.net/gh/Oaklight/llm-rosetta-shim-opencode-free@dist/v<version>/opencode_zen_free.tar.gz",
        "path": "providers",
        "archive": "tar.gz",
        "sha256": "<digest from v<version>/opencode_zen_free.tar.gz.sha256>"
      }
    ]
  }
}
```

The digest is what pins the mirror, and the same value appears in the release
notes. jsDelivr is only the default suggestion: the gateway accepts any URL that
serves the same bytes, an internal mirror included.

### Publishing a release

1. Bump `__version__` in `src/llm_rosetta_shim_opencode_zen_free/__init__.py`. The tag must match it —
   the release workflow passes the tag without its `v` as `--expect-version` and
   refuses a mismatch.
2. `python scripts/build_shim_archive.py --write` builds
   `dist/v<version>/opencode_zen_free.tar.gz` and its digest locally and verifies the
   layout. CI runs the same build without writing on every push, so a tree whose
   `providers/` layout changed fails before a tag is cut.
3. Tag and push: `git tag v<version> && git push origin v<version>`.
4. `.github/workflows/release.yml` builds from the tag, creates or updates the
   GitHub Release, uploads the archive and its digest file, and commits
   `v<version>/` to the `dist` branch.

The workflow requests `contents: write` for `GITHUB_TOKEN`, because it creates
the release and pushes `dist`. An organization that downgrades action tokens to
read-only must restore "Read and write permissions" under Settings → Actions →
General, or the release step fails.

## License

MIT
