"""Per-repo mining config: how to tell source from test, and which module a path belongs to.

One entry per upstream repo cloned into ../repos/<name>. Kept declarative on purpose:
the co-change miner is repo-agnostic, everything repo-specific lives here.

`module_of` returns a coarse subsystem label used to cluster commits. Clusters are the
unit we later hand-audit for graph motifs, so the label should track *engineering
subsystem* (transport / config-precedence / plugin-scope), not directory depth.
"""

from __future__ import annotations

import posixpath
import re
from dataclasses import dataclass, field
from typing import Callable


@dataclass(frozen=True)
class RepoSpec:
    name: str
    lang: str
    # A path is a test iff any test_pat matches; source iff any src_pat matches and not a test.
    src_pats: tuple[str, ...]
    test_pats: tuple[str, ...]
    # Paths matching these are ignored entirely (docs, CI, vendored deps, fixtures).
    ignore_pats: tuple[str, ...] = ()
    # Subsystem hints applied in order: first regex to match the path wins.
    module_rules: tuple[tuple[str, str], ...] = ()
    notes: str = ""


def _match_any(path: str, pats: tuple[str, ...]) -> bool:
    return any(re.search(p, path) for p in pats)


# Shared noise: docs, CI config, changelogs, lockfiles, generated assets.
COMMON_IGNORE = (
    r"^docs?/",
    r"^\.github/",
    r"^website/",
    r"(^|/)CHANGELOG",
    r"(^|/)CONTRIBUTING",
    r"(^|/)README",
    r"(^|/)LICENSE",
    r"\.(md|rst|txt|lock|sum|png|jpg|svg|ico)$",
)


REPOS: dict[str, RepoSpec] = {
    # ---------------------------------------------------------------- httpx (A+)
    # Target motifs: sync/async parity (Fork), transport/proxy/redirect/auth (Join),
    # env-var + proxy precedence (Hard Negative).
    "httpx": RepoSpec(
        name="httpx",
        lang="python",
        src_pats=(r"^httpx/.*\.py$",),
        test_pats=(r"^tests/.*\.py$",),
        ignore_pats=COMMON_IGNORE + (r"^tests/.*fixtures?/",),
        module_rules=(
            (r"^httpx/_client\.py$", "client-api"),
            (r"^httpx/_api\.py$", "toplevel-api"),
            (r"^httpx/_transports/", "transport"),
            (r"^httpx/_auth\.py$", "auth"),
            (r"^httpx/_config\.py$", "config-ssl"),
            (r"^httpx/_urls?\.py$|^httpx/_urlparse\.py$", "url"),
            (r"^httpx/_content\.py$|^httpx/_multipart\.py$", "content"),
            (r"^httpx/_models\.py$", "models"),
            (r"^httpx/_exceptions\.py$", "exceptions"),
            (r"^httpx/_utils\.py$", "utils"),
            (r"^tests/client/", "client-api"),
            (r"^tests/test_auth", "auth"),
            (r"^tests/models/", "models"),
        ),
        notes="sync/async parity is the flagship Fork motif; _client.py holds both Client and AsyncClient.",
    ),
    # ---------------------------------------------------------------- viper (A+)
    # Target motifs: Scope / Hard Negative / Stale-Update via config precedence,
    # alias, key normalization, reload.
    "viper": RepoSpec(
        name="viper",
        lang="go",
        src_pats=(r"\.go$",),
        test_pats=(r"_test\.go$",),
        ignore_pats=COMMON_IGNORE + (r"^internal/testutil/",),
        module_rules=(
            (r"^viper\.go$|^viper_test\.go$", "core-precedence"),
            (r"^util\.go$", "key-normalization"),
            (r"^flags\.go$", "flag-binding"),
            (r"^remote/|^internal/encoding/", "encoding-remote"),
            (r"^experimental", "experimental-finder"),
            (r"^watch", "reload-watch"),
        ),
        notes="Precedence order (explicit > flag > env > config > default) is the single richest invariant.",
    ),
    # ---------------------------------------------------------------- fastify (A+)
    # Target motifs: Scope (plugin encapsulation), Join (hook x decorator x schema).
    "fastify": RepoSpec(
        name="fastify",
        lang="javascript",
        src_pats=(r"^lib/.*\.js$", r"^fastify\.js$", r"^types/.*\.d\.ts$"),
        test_pats=(r"^test/.*\.(js|ts)$",),
        ignore_pats=COMMON_IGNORE + (r"^test/.*fixtures?/", r"^examples?/", r"^build/"),
        module_rules=(
            (r"^lib/pluginOverride\.js$|^lib/pluginUtils\.js$", "plugin-scope"),
            (r"^lib/hooks\.js$", "hook-lifecycle"),
            (r"^lib/decorate\.js$", "decorator"),
            (r"^lib/(schemas|validation)\.js$", "schema"),
            (r"^lib/reply\.js$", "reply"),
            (r"^lib/request\.js$", "request"),
            (r"^lib/route\.js$", "route"),
            (r"^lib/contentTypeParser\.js$", "content-type"),
            (r"^lib/error", "errors"),
            (r"^types/", "type-parity"),
            (r"^test/types/", "type-parity"),
            (r"^fastify\.js$", "core-bootstrap"),
        ),
        notes="Encapsulation boundary (parent/child/sibling plugin visibility) is an executable Scope oracle.",
    ),
    # ---------------------------------------------------------------- clap (A)
    # Target motifs: Fork/Join (builder vs derive parity), Update (deprecation).
    "clap": RepoSpec(
        name="clap",
        lang="rust",
        src_pats=(r"^clap_builder/src/.*\.rs$", r"^clap_derive/src/.*\.rs$", r"^src/.*\.rs$",
                  r"^clap_complete/src/.*\.rs$", r"^clap_lex/src/.*\.rs$"),
        test_pats=(r"^tests/.*\.rs$", r"^clap_complete/tests/.*\.rs$"),
        ignore_pats=COMMON_IGNORE + (r"^tests/.*snapshots?/", r"\.stderr$", r"\.stdout$",
                                     r"^benches?/", r"^examples?/"),
        module_rules=(
            (r"^clap_derive/", "derive-api"),
            (r"^clap_builder/src/builder/", "builder-api"),
            (r"^clap_builder/src/parser/", "parser"),
            (r"^clap_builder/src/error/", "error-surface"),
            (r"^clap_builder/src/output/", "help-output"),
            (r"^clap_complete/", "completion"),
            (r"^clap_lex/", "lexer"),
            (r"^tests/derive", "derive-api"),
            (r"^tests/builder", "builder-api"),
        ),
        notes="builder/derive parity = clean Fork; deprecated->removed API = natural Update chain.",
    ),
    # ---------------------------------------------------------------- ripgrep (A-)
    # Phase-0 infra validation: ignore/glob precedence, CLI behavior.
    "ripgrep": RepoSpec(
        name="ripgrep",
        lang="rust",
        src_pats=(r"^crates/.*/src/.*\.rs$",),
        test_pats=(r"^tests/.*\.rs$", r"^crates/.*/tests/.*\.rs$"),
        ignore_pats=COMMON_IGNORE + (r"^benchsuite/", r"^pkg/", r"^ci/"),
        module_rules=(
            (r"^crates/ignore/", "ignore-precedence"),
            (r"^crates/globset/", "glob"),
            (r"^crates/core/flags/", "cli-flags"),
            (r"^crates/printer/", "output-printer"),
            (r"^crates/searcher/", "searcher"),
            (r"^crates/matcher/|^crates/regex/", "matcher"),
            (r"^crates/grep/", "grep-facade"),
        ),
        notes="gitignore precedence is a real layered-rule invariant; cheap Rust test cycle.",
    ),
}


def classify(spec: RepoSpec, path: str) -> str:
    """Return 'test' | 'src' | 'ignore' for a repo-relative path."""
    path = path.replace("\\", "/")
    if _match_any(path, spec.ignore_pats):
        return "ignore"
    if _match_any(path, spec.test_pats):
        return "test"
    if _match_any(path, spec.src_pats):
        return "src"
    return "ignore"


def module_of(spec: RepoSpec, path: str) -> str:
    """Coarse subsystem label for clustering. Falls back to top two path segments."""
    path = path.replace("\\", "/")
    for pat, label in spec.module_rules:
        if re.search(pat, path):
            return label
    parts = posixpath.dirname(path).split("/")
    return "/".join(parts[:2]) if parts and parts[0] else "root"
