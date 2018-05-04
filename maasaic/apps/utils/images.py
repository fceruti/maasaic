from io import BytesIO

from PIL import Image

'''
Based on a script by BigglesZX: https://gist.github.com/BigglesZX/4016539

BigglesZX was adapted as follows:
    - Updated to be compatible with Python 3.
    - The original function 'processImage' was renamed 'extract_and_resize_frames' and was adapted as follows:
        - It resizes each frames as it extracts them
        - It saves all the frames to an array
        - It returns the array of all frames
    - a function 'resize_gif' was added which calls 'extract_and_resize_frames' to extract all the GIF frames and then
      saves all frames to an output file.
    - the function main() was modified to call 'resize_gif'

Functionality of the current script:
    - Similar functionality to BigglesZX's original script
    - Extracts all frames from a GIF and returns as array of all frames
    - Resizes the GIF to a given size

JAN 2017
'''


def resize_gif(image, box, zoom, output_file=None):
    """
    Resizes the GIF to a given length:

    Args:
        path: the path to the GIF file
        save_as (optional): Path of the resized gif. If not set, the original gif will be overwritten.
        resize_to (optional): new size of the gif. Format: (int, int). If not set, the original GIF will be resized to
                              half of its size.
    """
    all_frames = extract_and_resize_frames(image, box, zoom)

    if output_file is None:
        output_file = BytesIO()

    if len(all_frames) == 1:
        print("Warning: only 1 frame found")
        all_frames[0].save(output_file, optimize=True, format='GIF')
    else:
        all_frames[0].save(output_file, optimize=True, save_all=True, append_images=all_frames[1:], duration=image.info['duration'], loop=0, format='GIF')
    return output_file


def analyse_image(image):
    """
    Pre-process pass over the image to determine the mode (full or additive).
    Necessary as assessing single frames isn't reliable. Need to know the mode
    before processing all frames.
    """
    results = {
        'size': image.size,
        'mode': 'full',
    }
    try:
        while True:
            if image.tile:
                tile = image.tile[0]
                update_region = tile[1]
                update_region_dimensions = update_region[2:]
                if update_region_dimensions != image.size:
                    results['mode'] = 'partial'
                    break
            image.seek(image.tell() + 1)
    except EOFError:
        pass
    return results


def extract_and_resize_frames(image, box, zoom):
    """
    Iterate the GIF, extracting each frame and resizing them

    Returns:
        An array of all frames
    """
    mode = analyse_image(image)['mode']

    i = 0
    palette = image.getpalette()
    last_frame = image.convert('RGBA')

    all_frames = []
    image.seek(0)
    try:
        while True:
            '''
            If the GIF uses local colour tables, each frame will have its own palette.
            If not, we need to apply the global palette to the new frame.
            '''
            if not image.getpalette():
                image.putpalette(palette)

            new_frame = Image.new('RGBA', image.size)

            '''
            Is this file a "partial"-mode GIF where frames update a region of a different size to the entire image?
            If so, we need to construct the new frame by pasting it on top of the preceding frames.
            '''
            if mode == 'partial':
                new_frame.paste(last_frame)

            new_frame.paste(image, (0, 0), image.convert('RGBA'))
            new_frame = new_frame.crop(box)
            width, height = new_frame.size
            new_frame = new_frame.resize((int(width * zoom * 2), int(height * zoom * 2)), Image.ANTIALIAS)
            all_frames.append(new_frame)

            i += 1
            last_frame = new_frame
            image.seek(image.tell() + 1)
    except EOFError:
        pass

    return all_frames
