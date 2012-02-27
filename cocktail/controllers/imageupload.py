#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import ImageFile
from cocktail.schema.exceptions import ValidationError

def get_image_size(path):
    """Find the size in pixels of the given image file, loading as little of
    the image into memory as possible.
    
    :param path: The path to the image file to obtain the size for.
    :type path: str

    :return: A tuple holding the width and height of the indicated image, in
        pixels.
    :rtype: (int, int)

    :raise IOError: Raised if the indicated file can't be opened or parsed as
        an image file of a known type.
    """
    image_parser = ImageFile.Parser()
    image_file = open(path, "rb")

    while True:
        data = image_file.read(1024)
        image_parser.feed(data)
        if image_parser.image:
            return image_parser.image.size

    raise IOError("Can't determine the image size for file '%s'" % path)

def constrain_image_upload(member,
    max_width = None,
    max_height = None,
    allow_rotation = False
):
    """Validate certain properties of uploaded images.

    :param member: The upload member to constrain.
    :type member: `FileUpload`

    :param max_width: The maximum accepted width of images uploaded into this
        member, in pixels. Images with a higher width will yield an error of
        type `ImageTooBigError` during validation.
        
        Passing None to this parameter will disable this validation.

    :type max_width: int

    :param max_height: The maximum accepted height of images uploaded into this
        member, in pixels. Images with a higher height will yield an error of
        type `ImageTooBigError` during validation.
        
        Passing None to this parameter will disable this validation.

    :type max_height: int
    """
    if max_width or max_height:
        @member.add_validation
        def image_size_validation(member, upload, ctx):
            if upload:
                upload_path = member.get_file_destination(upload)
                if upload_path:
                    try:
                        image_size = get_image_size(upload_path)
                    except:
                        pass
                    else:
                        if not (
                            size_fits(image_size, (max_width, max_height)) \
                            or (
                                allow_rotation
                                and size_fits(image_size, (max_height, max_width))
                            )
                        ):
                            yield ImageTooBigError(
                                member,
                                upload,
                                ctx,
                                max_width,
                                max_height,
                                allow_rotation
                            )

def size_fits(size, max_size):
    width, height = size
    max_width, max_height = max_size
    return (not max_width or width <= max_width) \
       and (not max_height or height <= max_height)


class ImageTooBigError(ValidationError):
    """A validation error yielded when uploading an image file that exceeds the
    maximum width or height set by `constrain_image_upload`.
    """

    def __init__(self,
        member,
        value,
        context,
        max_width,
        max_height,
        allow_rotation
    ):
        ValidationError.__init__(self, member, value, context)
        self.max_width = max_width
        self.max_height = max_height
        self.allow_rotation = allow_rotation

