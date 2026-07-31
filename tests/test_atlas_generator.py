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
