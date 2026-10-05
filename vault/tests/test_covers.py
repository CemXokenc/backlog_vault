import shutil
import tempfile
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from vault.models import Game
from vault.tests.helpers import create_catalog, create_gamer
from vault.validators import validate_image_size

MEDIA_ROOT = tempfile.mkdtemp()


def make_image(name="cover.png", size=(8, 8), color="purple"):
    buffer = BytesIO()
    Image.new("RGB", size, color).save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), "image/png")


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class CoverUploadTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Path(MEDIA_ROOT).mkdir(parents=True, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    @classmethod
    def setUpTestData(cls):
        cls.gamer = create_gamer()
        cls.catalog = create_catalog()

    def setUp(self):
        self.client.force_login(self.gamer)

    def form_data(self, **extra):
        data = {
            "title": "New Game",
            "release_year": 2021,
            "genres": [self.catalog.genre.pk],
            "platforms": [self.catalog.platform.pk],
        }
        data.update(extra)
        return data

    def test_form_is_multipart(self):
        response = self.client.get(reverse("vault:game-create"))
        self.assertContains(response, 'enctype="multipart/form-data"')

    def test_upload_cover_when_creating_a_game(self):
        response = self.client.post(
            reverse("vault:game-create"),
            self.form_data(cover=make_image()),
        )
        game = Game.objects.get(title="New Game")
        self.assertRedirects(response, game.get_absolute_url())
        self.assertTrue(game.cover.name.startswith("covers/"))
        self.assertTrue(Path(game.cover.path).exists())

    def test_non_image_file_is_rejected(self):
        fake = SimpleUploadedFile("cover.png", b"not an image", "image/png")
        response = self.client.post(
            reverse("vault:game-create"),
            self.form_data(cover=fake),
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Game.objects.filter(title="New Game").exists())

    def test_validator_rejects_files_over_the_limit(self):
        too_big = SimpleNamespace(size=3 * 1024 * 1024)
        with self.assertRaises(ValidationError):
            validate_image_size(too_big)
        validate_image_size(SimpleNamespace(size=1024))

    def test_cover_source_prefers_upload_over_url(self):
        game = Game.objects.create(
            title="Both",
            release_year=2020,
            cover_url="https://example.com/c.jpg",
        )
        self.assertEqual(game.cover_source, "https://example.com/c.jpg")
        game.cover = make_image()
        game.save()
        self.assertIn("covers/", game.cover_source)

    def test_cover_source_is_empty_without_any_cover(self):
        self.assertEqual(self.catalog.game.cover_source, "")


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class CoverDisplayTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Path(MEDIA_ROOT).mkdir(parents=True, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    @classmethod
    def setUpTestData(cls):
        cls.gamer = create_gamer()
        cls.catalog = create_catalog()
        cls.game = cls.catalog.game

    def setUp(self):
        self.client.force_login(self.gamer)

    def test_placeholder_without_any_cover(self):
        for url in (
            reverse("vault:game-list"),
            reverse("vault:game-detail", args=[self.game.pk]),
        ):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, "bi-image")
                self.assertNotContains(response, "<img src=")

    def test_cover_url_is_shown_in_card_and_detail(self):
        self.game.cover_url = "https://example.com/hades.jpg"
        self.game.save()
        for url in (
            reverse("vault:game-list"),
            reverse("vault:game-detail", args=[self.game.pk]),
        ):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, "https://example.com/hades.jpg")

    def test_uploaded_cover_is_shown_in_card_and_detail(self):
        self.game.cover = make_image()
        self.game.save()
        for url in (
            reverse("vault:game-list"),
            reverse("vault:game-detail", args=[self.game.pk]),
        ):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, self.game.cover.url)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class CoverCleanupTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Path(MEDIA_ROOT).mkdir(parents=True, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def create_game(self, **extra):
        game = Game.objects.create(title="Temp", release_year=2020, **extra)
        game.cover = make_image("first.png")
        game.save()
        return game

    def test_old_file_is_removed_when_cover_is_replaced(self):
        game = self.create_game()
        old_path = Path(game.cover.path)
        self.assertTrue(old_path.exists())
        game.cover = make_image("second.png", color="green")
        game.save()
        self.assertFalse(old_path.exists())
        self.assertTrue(Path(game.cover.path).exists())

    def test_file_is_removed_when_cover_is_cleared(self):
        game = self.create_game()
        old_path = Path(game.cover.path)
        game.cover = ""
        game.save()
        self.assertFalse(old_path.exists())

    def test_file_is_removed_when_game_is_deleted(self):
        game = self.create_game()
        path = Path(game.cover.path)
        game.delete()
        self.assertFalse(path.exists())

    def test_saving_without_changes_keeps_the_file(self):
        game = self.create_game()
        path = Path(game.cover.path)
        game.title = "Renamed"
        game.save()
        self.assertTrue(path.exists())
