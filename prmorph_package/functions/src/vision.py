import google.cloud.vision as vision
import io

def detect_text(path: str) -> str:
    """Detects text in the file."""
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(
        image=image,
        # specify english handwriting as input
        image_context={"language_hints": ["en-t-i0-handwrit"]}
    )
    texts = response.text_annotations

    fish_ID = ""
    for text in texts:
        fish_ID = fish_ID + str(text.description).replace("\n", "_")

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    return fish_ID