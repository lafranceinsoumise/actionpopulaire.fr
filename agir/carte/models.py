import requests
from django.conf import settings
from django.contrib.gis.db import models
from django.core import exceptions, files
from django.core.validators import (
    FileExtensionValidator,
    MinValueValidator,
    MaxValueValidator,
)
from django.utils.translation import ugettext_lazy as _

from dynamic_filenames import FilePattern
from io import BytesIO
from PIL import Image
from stdimage.models import StdImageField

__all__ = [
    "StaticMapImage",
]

static_map_image_path = FilePattern(
    filename_pattern="{app_label}/{model_name}/{uuid:base32}{ext}"
)
DEFAULT_MAP_WIDTH = 992
DEFAULT_MAP_HEIGHT = 300
DEFAULT_MAP_ZOOM = 11
DEFAULT_MAP_SCALE = 1


def download_static_map_image_from_jawg(
    center=None,
    zoom=DEFAULT_MAP_ZOOM,
    scale=DEFAULT_MAP_SCALE,
    width=DEFAULT_MAP_WIDTH,
    height=DEFAULT_MAP_HEIGHT,
):
    if not center:
        raise exceptions.ValidationError("Missing required property 'center'")
    # https://www.jawg.io/docs/apidocs/maps/static-maps/
    data = {
        "center": {"latitude": center[1], "longitude": center[0],},
        "zoom": zoom,
        "scale": scale,
        "size": {"width": width, "height": height,},
        "layer": "jawg-streets",
        "format": "png",
    }
    url = f"https://api.jawg.io/static?access-token={settings.JAWG_API_ACCES_TOKEN}"
    response = requests.post(url, json=data)
    if response.status_code != requests.codes.ok:
        raise exceptions.ValidationError(response.content)
    image = Image.open(BytesIO(response.content))
    image.verify()

    return files.File(BytesIO(response.content), name="static_map.png")


class StaticMapImageManager(models.Manager):
    def create_from_jawg(self, *args, **kwargs):
        image = download_static_map_image_from_jawg(**kwargs)
        static_map_image = super(StaticMapImageManager, self).create(
            *args, **kwargs, image=image,
        )
        return static_map_image

    def create(self, *args, **kwargs):
        if kwargs.get("image", None) is None:
            return self.create_from_jawg(*args, **kwargs)
        return super(StaticMapImageManager, self).create(*args, **kwargs)


class StaticMapImage(models.Model):
    DEFAULT_WIDTH = DEFAULT_MAP_WIDTH
    DEFAULT_HEIGHT = DEFAULT_MAP_HEIGHT
    DEFAULT_ZOOM = DEFAULT_MAP_ZOOM
    DEFAULT_SCALE = DEFAULT_MAP_SCALE

    objects = StaticMapImageManager()

    center = models.PointField(
        _("coordonnées"), geography=True, null=False, blank=False, spatial_index=True
    )
    zoom = models.IntegerField(
        _("niveau de zoom"),
        blank=False,
        null=False,
        default=DEFAULT_ZOOM,
        validators=[MinValueValidator(0), MaxValueValidator(20),],
    )
    scale = models.IntegerField(
        _("résolution de l'image"),
        blank=False,
        null=False,
        default=DEFAULT_SCALE,
        validators=[MinValueValidator(1), MaxValueValidator(2),],
    )
    image = StdImageField(
        _("image"),
        upload_to=static_map_image_path,
        variations={"default": (DEFAULT_WIDTH, DEFAULT_HEIGHT, True)},
        blank=False,
        null=False,
        delete_orphans=True,
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "png"]),],
    )

    class Meta:
        indexes = [models.Index(fields=["center"])]
        constraints = [
            models.UniqueConstraint(
                fields=["center", "zoom", "scale",], name="unique_for_position_options",
            ),
        ]

    def __str__(self):
        if self.image and hasattr(self.image, "url"):
            return self.image.url
        return ""

    def __repr__(self):
        if self.image and hasattr(self.image, "url"):
            return self.image.url
        return ""
