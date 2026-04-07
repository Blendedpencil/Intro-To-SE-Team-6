import os

ALLOWED_LISTING_IMAGE_MIME_TYPES = {
    'image/png',
    'image/jpeg',
}

ALLOWED_LISTING_IMAGE_EXTENSIONS = {
    '.png',
    '.jpg',
    '.jpeg',
}

ALLOWED_GOV_ID_MIME_TYPES = {
    'image/png',
    'image/jpeg',
    'application/pdf',
}

ALLOWED_GOV_ID_EXTENSIONS = {
    '.png',
    '.jpg',
    '.jpeg',
    '.pdf',
}

ALLOWED_PDF_MIME_TYPES = {
    'application/pdf',
}

ALLOWED_PDF_EXTENSIONS = {
    '.pdf',
}


def is_valid_uploaded_file(uploaded_file, allowed_mime_types, allowed_extensions):
    if not uploaded_file:
        return False

    content_type = getattr(uploaded_file, 'content_type', '')
    extension = os.path.splitext(uploaded_file.name)[1].lower()

    return content_type in allowed_mime_types and extension in allowed_extensions