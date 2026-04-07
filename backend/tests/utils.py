from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

#Bunch of Helpers for creating test data and making common test actions easier (e.g. login/logout)

def login_user(client, user, password="test"):
    """
    Logs in a user using Django test client
    """
    return client.login(username=user.username, password=password)


def logout_user(client):
    """
    Logs out current user
    """
    client.logout()



def attach_user_to_request(request, user):
    """
    Attach a user to a RequestFactory request
    """
    request.user = user
    return request


def create_test_image_png():
    return SimpleUploadedFile(
        "test.png",
        b"\x89PNG\r\n\x1a\nfakepngdata",
        content_type="image/png"
    )


def create_test_image_jpg():
    return SimpleUploadedFile(
        "test.jpg",
        b"\xff\xd8\xff fakejpgdata",
        content_type="image/jpeg"
    )


def create_test_pdf(name="test.pdf"):
    return SimpleUploadedFile(
        name,
        b"%PDF-1.4 fake pdf content",
        content_type="application/pdf"
    )


def create_invalid_file():
    return SimpleUploadedFile(
        "test.txt",
        b"this should fail validation",
        content_type="text/plain"
    )


def listing_payload(**overrides):
    """
    Default POST payload for creating a listing
    """
    data = {
        "title": "Test House",
        "price": "250000",
        "location": "123 Test Lane",
        "style": "Modern",
        "description": "Nice house",
        "bedrooms": 3,
        "bathrooms": 2,
        "square_footage": 1500,
    }
    data.update(overrides)
    return data


def application_payload(**overrides):
    """
    Default POST payload for buyer application
    """
    data = {
        "fname": "Test",
        "lname": "User",
        "emailID": "test@gmail.com",
        "gov_id": create_test_pdf("gov.pdf"),
        "mortgage_pre_approval": create_test_pdf("mortgage.pdf"),
        "bank_statements": [
            create_test_pdf("bank1.pdf"),
            create_test_pdf("bank2.pdf"),
        ],
    }
    data.update(overrides)
    return data


def payment_payload(**overrides):
    """
    Default POST payload for payment
    """
    data = {
        "card_name": "Test User",
        "card_number": "4111111111111111",
        "expiry": "12/30",
        "cvv": "123",
    }
    data.update(overrides)
    return data