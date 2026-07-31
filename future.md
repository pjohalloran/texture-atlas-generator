# Future Directions

Ideas for extending texture-atlas-generator toward more general game-engine use.
Not a roadmap or commitment — a brainstorm to prioritize from later.

## Packing Algorithms

- **Skyline algorithm** — the de facto industry standard alongside maxrects for 2D
  bin packing (used by most commercial packers). Tracks a "skyline" height profile
  instead of a free-rect list. Generally faster than maxrects with competitive
  density. Worth adding as a third `-a` choice, following the existing
  `TexturePacker` abstract-base pattern.
- **Guillotine algorithm** — simpler than maxrects; splits free space with
  straight full-width/full-height cuts instead of maxrects' overlapping free-rect
  bookkeeping. Faster, modestly worse density. Good candidate for a "fast" mode
  on large batches.
- **Shelf/row packing** — very fast, ideal for uniform-height content like font
  glyphs at a single point size. `ImageFontGenerator` could default to this
  instead of reusing the general-purpose maxrects/ratcliff packers, since glyph
  packing is naturally row-shaped.
- **Multi-bin (multi-page) packing** — currently a real gap. Everything for one
  `textures/<name>/` directory must fit into a *single* atlas, retried up to the
  16384px `DEFAULT_MAX_BIN_SIZE` cap. Real engines commonly want N atlas pages
  instead of one oversized texture (GPU max texture size varies by platform/
  hardware tier — many mobile/older GPUs cap well below 16384). Probably the
  single highest-value "make this engine-ready" feature here: once a bin size
  cap is hit, start a new page instead of raising `PackerError`.
- **Input pre-sorting** — sort textures by area/longest-edge before packing.
  Ratcliff already does a weak per-iteration version of this; a proper
  pre-sort pass ahead of *either* algorithm is a small, cheap change that
  generally improves density.
- **Post-pack optimization pass** — try several heuristics (or several random
  input orderings) and keep the best result by occupancy. Since
  `TexturePackerMaxRects.get_occupancy()` already exists, this is mostly
  plumbing: run N variants, compare occupancy, keep the winner.

## Texture Processing (currently entirely missing)

- **Trim/crop transparent padding** — detect each source image's actual
  non-transparent bounding box before handing its dimensions to the packer,
  and store the trim offset (original size + offset within it) in the
  manifest so the engine can restore correct sprite positioning. Commonly
  saves 20-40% of atlas space; a top-requested feature in tools like
  TexturePacker. This is the second-highest-value item after multi-page.
- **Extrusion/bleeding padding** — duplicate edge pixels outward by N px so
  bilinear filtering/mipmapping at UV seams doesn't sample into the
  neighboring sprite. Without this, packed atlases show visible seam
  artifacts at runtime whenever the engine filters or mipmaps — a real
  correctness gap for production use today (the existing 1px `borderSize` is
  just spacing between rects, not seam-safe extrusion).
- **Alpha premultiplication** — common engine expectation, straightforward
  Pillow-level toggle (`-alpha-premultiplied` flag).
- **Mipmap chain generation** alongside the atlas image.
- **Compressed GPU texture output** (DXT/BC, ETC2, ASTC) via an external
  compressor (e.g. shelling out to `texconv`/`astcenc`/`basisu`). Bigger lift
  than the above — external tool dependency, platform-specific binaries — but
  a big win for VRAM/bandwidth on real hardware.

## Output Formats

### Binary

- **FlatBuffers** — the standout choice for a game engine specifically.
  Schema-driven (`.fbs` file defines the manifest layout), and reads are
  zero-copy: mmap the file, cast pointers, no deserialization step. Exactly
  what a hot-path asset loader wants, and it's what many shipped titles
  already use for this kind of data. Highest implementation cost of the
  binary options (schema authoring, codegen step) but the best runtime
  characteristics by far.
- **MessagePack** — same logical shape as the existing JSON output, just
  binary-encoded. Much lower effort than FlatBuffers (near drop-in from the
  current `JsonParser`), decent size/parse-speed win for the cost. Good
  "cheap binary" option to ship first.
- **Small custom binary format** — fixed-size header + fixed-size per-texture
  records, doable in an afternoon. Reinvents something FlatBuffers already
  solves better, but has zero new dependencies — worth it only if adding a
  FlatBuffers toolchain dependency is undesirable.
- **Protocol Buffers** — reasonable middle ground, but FlatBuffers fits
  asset-pipeline use better specifically because of the no-unpack-step
  property; protobuf still requires a decode pass.

### Text

- **Existing importer-format compatibility** — matching the JSON/plist shapes
  already used by cocos2d, Spine, or TexturePacker itself buys instant
  support in any engine/tool that already has an importer for those formats,
  without writing new engine-side parsing code at all. Cheapest way to reach
  the widest set of engines.
- **YAML** — for a hand-editable manifest variant; low value for runtime use,
  higher value if manifests are ever meant to be diffed/edited by hand.

## Game-Engine-Specific Exporters

Dedicated output presets, each a thin new `Parser` subclass given the
existing abstraction (`get_file_ext()` + `parse()`):

- **Unity** — SpriteAtlas-compatible data + `.meta` sidecar generation.
- **Godot** — `AtlasTexture` resource (`.tres`) generation.
- **Unreal** — Paper2D flipbook/sprite sheet data.
- **Web/JS engines** — CSS spritesheet output (background-position rules),
  Phaser's JSON atlas format.

Cheap to add incrementally per-engine as real demand shows up — no
architecture change needed, just new `Parser` subclasses registered in
`get_parser()`.

## Pipeline / Developer Experience

- **Incremental rebuilds** — hash source images (mtime + content hash), skip
  re-packing atlases whose inputs haven't changed since the last run. Matters
  a lot once a project has hundreds of sprites across many atlas directories.
- **Watch mode** — auto-rebuild affected atlases on file change during active
  development.
- **Declarative config file** (TOML/YAML) — alternative to the current
  CLI-flags-only interface, so per-project build settings can be checked into
  source control instead of re-typed on every invocation. Could coexist with
  the CLI (flags override config file values).
- **Parallel atlas generation** — `iterate_data_directory()` currently
  processes subdirectories sequentially; multi-core packing across
  independent atlas directories is an easy win once there's real batch scale.
- **Plugin discovery for packers/parsers** — now that the project is a real
  installable package (`pyproject.toml`), `TexturePacker`/`Parser` subclasses
  could be discovered via `entry_points`, letting a downstream game project
  register a custom output format or packing algorithm without forking this
  repo.
- **Content-hash filenames** — optional cache-busting suffix on output atlas
  filenames, useful for web-deployed games.

## Suggested Ordering (highest leverage first)

1. Multi-page/multi-bin packing (removes the hard single-atlas-size ceiling)
2. Trim + extrude (biggest visual-quality and space-efficiency win)
3. MessagePack output (cheap binary win, near drop-in from JsonParser)
4. Skyline algorithm (rounds out algorithm choice with an industry-standard option)
5. Incremental rebuilds (biggest DX win once projects get large)
6. Engine-specific exporters (as real demand appears)
7. FlatBuffers, compressed GPU textures (highest value but highest cost — save
   for when there's a concrete consuming engine to validate against)
