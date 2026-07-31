from atlas.atlas_data import AtlasData
from atlas.texture import Texture


def test_init_defaults():
    atlas = AtlasData(name="sprites")
    assert atlas.name == "sprites"
    assert atlas.width == 512
    assert atlas.height == 512
    assert atlas.border == 1
    assert atlas.color_mode == "RGBA"
    assert atlas.file_type == "tga"
    assert atlas.get_texture_count() == 0


def test_add_texture_indexes_by_name():
    atlas = AtlasData(name="sprites")
    tex = Texture(10, 10, name="a.png")
    atlas.add_texture(tex)
    assert atlas.get_texture_count() == 1
    assert atlas.texture_dict["a.png"] is tex


def test_instances_do_not_share_texture_dict():
    # texture_dict is declared as a class attribute in AtlasData; guard
    # against it accidentally becoming shared mutable state across instances.
    first = AtlasData(name="first")
    second = AtlasData(name="second")
    first.add_texture(Texture(1, 1, name="only-in-first"))
    assert second.get_texture_count() == 0
    assert "only-in-first" not in second.texture_dict
