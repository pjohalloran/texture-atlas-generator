import logging
from typing import Callable, List, Optional, Tuple, TypeVar

from atlas.texture import Texture
from geom.geom import next_power_of_two

logger = logging.getLogger(__name__)

# Default upper bound for retry_with_growing_bin_size(). Some packers (e.g.
# ratcliff) ignore the requested bin size and are fully deterministic, so a
# PackerError from them will recur at every size; without a cap the retry
# loop would grow the size forever without ever converging.
DEFAULT_MAX_BIN_SIZE = 16384

T = TypeVar('T')


class PackerError(Exception):
    pass


def retry_with_growing_bin_size(pack_fn: Callable[[int], T], initial_size: int, max_size: int = DEFAULT_MAX_BIN_SIZE) -> T:
    """Call pack_fn(curr_size) repeatedly, doubling curr_size to the next
    power of two each time it raises PackerError, until it succeeds or
    max_size is reached (at which point the PackerError propagates).

    Returns whatever pack_fn(curr_size) returned on success.
    """
    curr_size = initial_size
    while True:
        try:
            return pack_fn(curr_size)
        except PackerError:
            if curr_size >= max_size:
                raise
            curr_size = next_power_of_two(curr_size)
            logger.info("Failed, trying next power of two: %s", curr_size)


class TexturePacker:
    """Base class for texture packing algorithms.

    Subclasses queue up textures via add_texture() and, once pack_textures()
    has run, expose each texture's placement through its Texture.x/y fields
    (or via get_texture()).
    """

    texArr: List[Texture] = None
    allow_rotations = False

    def __init__(self) -> None:
        self.texArr = []

    def add_texture(self, width: int, height: int, name: str) -> None:
        """Queue a texture of the given size for packing."""
        self.texArr.append(Texture(width, height, name))

    def get_texture(self, name: str) -> Optional[Texture]:
        """Return the packed Texture with this name, or None if not found.

        The returned Texture's width/height already reflect its placed
        orientation (i.e. already swapped if .flipped is True) - callers
        compositing pixel data should rotate it to match when .flipped.
        """
        for t in self.texArr:
            if (t.name == name):
                return t
        return None

    def get_texture_count(self) -> int:
        return len(self.texArr)

    def pack_textures(self, powerOfTwo: bool, oneBorderPixel: bool) -> Tuple[int, int, int]:
        """Place every queued texture and return (bin_width, bin_height, wasted_area).

        Raises PackerError if the queued textures can't all fit.
        """
        raise NotImplementedError('pack_textures() has not been implemented')
