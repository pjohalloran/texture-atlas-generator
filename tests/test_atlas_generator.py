from PIL import Image

import AtlasGenerator

DEFAULT_ARGS = {
    'packing_algorithm': 'maxrects',
    'maxrects_heuristic': 'area',
    'allow_rotations': False,
    'atlas_type': 'png',
    'output_data_type': 'xml',
    'bg_color': '0,0,0,255',
    'maxrects_bin_size': '64',
    'verbose': False,
    'padding': 1,
}


def _make_sprites_dir(tmp_path, broken=False):
    sprites_dir = tmp_path / "sprites"
    sprites_dir.mkdir()
    Image.new("RGBA", (8, 8), (255, 0, 0, 255)).save(sprites_dir / "a.png")
    if broken:
        (sprites_dir / "broken.png").write_text("not an image")
    return sprites_dir


def test_create_atlas_returns_true_when_all_images_open(tmp_path):
    sprites_dir = _make_sprites_dir(tmp_path)
    atlases_dir = tmp_path / "atlases"
    atlases_dir.mkdir()

    ok = AtlasGenerator.create_atlas('RGBA', str(sprites_dir), str(atlases_dir), 'sprites', DEFAULT_ARGS)

    assert ok is True


def test_create_atlas_returns_false_when_an_image_fails_to_open(tmp_path):
    # Regression test: main()'s exit code used to be meaningless (it never
    # reached sys.exit(), and iterate_data_directory() had no return
    # statement at all), so a build pipeline had no way to detect that some
    # images silently failed to open and were skipped.
    sprites_dir = _make_sprites_dir(tmp_path, broken=True)
    atlases_dir = tmp_path / "atlases"
    atlases_dir.mkdir()

    ok = AtlasGenerator.create_atlas('RGBA', str(sprites_dir), str(atlases_dir), 'sprites', DEFAULT_ARGS)

    assert ok is False


def test_iterate_data_directory_aggregates_failures_across_atlases(tmp_path):
    textures_dir = tmp_path / "textures"
    textures_dir.mkdir()
    _make_sprites_dir(textures_dir, broken=False)  # tmp_path/textures/sprites
    bad_dir = textures_dir / "bad"
    bad_dir.mkdir()
    (bad_dir / "broken.png").write_text("not an image")

    atlases_dir = tmp_path / "atlases"
    atlases_dir.mkdir()

    ok = AtlasGenerator.iterate_data_directory('RGBA', str(atlases_dir), str(textures_dir), DEFAULT_ARGS)

    assert ok is False


def test_iterate_data_directory_true_when_everything_opens(tmp_path):
    textures_dir = tmp_path / "textures"
    textures_dir.mkdir()
    _make_sprites_dir(textures_dir, broken=False)

    atlases_dir = tmp_path / "atlases"
    atlases_dir.mkdir()

    ok = AtlasGenerator.iterate_data_directory('RGBA', str(atlases_dir), str(textures_dir), DEFAULT_ARGS)

    assert ok is True


def test_iterate_data_directory_packs_loose_root_images_into_own_atlas(tmp_path):
    # Regression test: images placed directly in the images-dir (not inside
    # any subdirectory) used to be silently skipped entirely - no atlas, no
    # warning, no error, exit code 0. They're now packed into their own
    # atlas, named after the images-dir itself.
    textures_dir = tmp_path / "textures"
    textures_dir.mkdir()
    Image.new("RGBA", (8, 8), (255, 0, 0, 255)).save(textures_dir / "a.png")
    Image.new("RGBA", (8, 8), (0, 255, 0, 255)).save(textures_dir / "b.png")

    atlases_dir = tmp_path / "atlases"
    atlases_dir.mkdir()

    ok = AtlasGenerator.iterate_data_directory('RGBA', str(atlases_dir), str(textures_dir), DEFAULT_ARGS)

    assert ok is True
    root_atlas = atlases_dir / "textures.png"
    assert root_atlas.is_file()
    img = Image.open(root_atlas)
    assert img.size[0] > 0 and img.size[1] > 0


def test_iterate_data_directory_handles_mixed_root_images_and_subdirectories(tmp_path):
    textures_dir = tmp_path / "textures"
    textures_dir.mkdir()
    Image.new("RGBA", (8, 8), (255, 0, 0, 255)).save(textures_dir / "root1.png")
    _make_sprites_dir(textures_dir, broken=False)  # tmp_path/textures/sprites

    atlases_dir = tmp_path / "atlases"
    atlases_dir.mkdir()

    ok = AtlasGenerator.iterate_data_directory('RGBA', str(atlases_dir), str(textures_dir), DEFAULT_ARGS)

    assert ok is True
    assert (atlases_dir / "textures.png").is_file()
    assert (atlases_dir / "sprites.png").is_file()


def test_iterate_data_directory_warns_and_creates_nothing_when_empty(tmp_path, caplog):
    textures_dir = tmp_path / "textures"
    textures_dir.mkdir()

    atlases_dir = tmp_path / "atlases"
    atlases_dir.mkdir()

    with caplog.at_level("WARNING"):
        ok = AtlasGenerator.iterate_data_directory('RGBA', str(atlases_dir), str(textures_dir), DEFAULT_ARGS)

    assert ok is True
    assert list(atlases_dir.iterdir()) == []
    assert any("nothing to pack" in record.message for record in caplog.records)
