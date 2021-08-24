from django.test import TestCase, Client, tag
from django.urls import reverse


@tag("swaggerview")
class TestSwaggerUi(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("pages_api:swagger")

    def test_swagger_uses_desired_template(self):
        resp = self.client.get(self.url)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "pages/swagger_ui.html")
