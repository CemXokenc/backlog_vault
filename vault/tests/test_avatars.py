import shutil
import tempfile
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from vault.models import Gamer
from vault.tests.helpers import create_gamer
from vault.tests.test_covers import make_image

MEDIA_ROOT = tempfile.mkdtemp()
URL = "https://example.com/avatar.png"


class AvatarSourceTests(TestCase):
    def test_initial_uses_nickname_then_username(self):
        self.assertEqual(Gamer(username="alex").avatar_initial, "A")
        self.assertEqual(
            Gamer(username="alex", nickname="zed").avatar_initial,
            "Z",
        )

    def test_url_is_used_when_nothing_is_uploaded(self):
        gamer = Gamer(username="alex", avatar_url=URL)
        self.assertEqual(gamer.avatar_source, URL)

    def test_uploaded_file_wins_over_the_url(self):
        gamer = Gamer(username="alex", avatar_url=URL)
        gamer.avatar.name = "avatars/me.png"
        self.assertTrue(gamer.avatar_source.endswith("avatars/me.png"))

    def test_no_avatar_gives_an_empty_source(self):
        self.assertEqual(Gamer(username="alex").avatar_source, "")


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class AvatarUploadTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Path(MEDIA_ROOT).mkdir(parents=True, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.gamer = create_gamer("alex")
        self.client.force_login(self.gamer)
        self.url = reverse("vault:gamer-update", args=[self.gamer.pk])

    def post(self, **extra):
        data = {"nickname": "Alex", "bio": "", "avatar_url": ""}
        data.update(extra)
        return self.client.post(self.url, data)

    def test_profile_form_accepts_an_upload(self):
        response = self.post(avatar=make_image("me.png"))
        self.assertRedirects(response, self.gamer.get_absolute_url())
        self.gamer.refresh_from_db()
        self.assertTrue(self.gamer.avatar.name.startswith("avatars/"))

    def test_profile_form_is_multipart(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'enctype="multipart/form-data"')

    def test_avatar_url_can_be_set(self):
        self.post(avatar_url=URL)
        self.gamer.refresh_from_db()
        self.assertEqual(self.gamer.avatar_source, URL)

    def test_too_large_image_is_rejected(self):
        big = SimpleUploadedFile(
            "big.png",
            make_image("x.png").read() + b"0" * (2 * 1024 * 1024 + 1),
            "image/png",
        )
        response = self.post(avatar=big)
        self.assertEqual(response.status_code, 200)
        self.gamer.refresh_from_db()
        self.assertFalse(self.gamer.avatar)

    def test_old_file_is_removed_when_replaced(self):
        self.post(avatar=make_image("one.png"))
        self.gamer.refresh_from_db()
        old_path = Path(self.gamer.avatar.path)
        self.assertTrue(old_path.exists())
        self.post(avatar=make_image("two.png"))
        self.assertFalse(old_path.exists())

    def test_file_is_removed_with_the_gamer(self):
        self.post(avatar=make_image("one.png"))
        self.gamer.refresh_from_db()
        path = Path(self.gamer.avatar.path)
        self.gamer.delete()
        self.assertFalse(path.exists())


class AvatarDisplayTests(TestCase):
    def setUp(self):
        self.gamer = create_gamer("alex", avatar_url=URL)
        self.client.force_login(self.gamer)

    def test_gamer_list_and_profile_show_the_image(self):
        for url in (
            reverse("vault:gamer-list"),
            self.gamer.get_absolute_url(),
        ):
            with self.subTest(url=url):
                self.assertContains(self.client.get(url), URL)

    def test_navbar_shows_the_avatar(self):
        response = self.client.get(reverse("vault:index"))
        self.assertContains(response, 'class="avatar avatar-sm"')

    def test_broken_image_falls_back_to_the_letter(self):
        response = self.client.get(reverse("vault:gamer-list"))
        self.assertContains(response, 'onerror="this.remove()"')
        self.assertContains(response, ">A<img")

    def test_gamer_without_avatar_shows_only_the_letter(self):
        other = create_gamer("zed")
        response = self.client.get(other.get_absolute_url())
        self.assertContains(
            response,
            '<span class="avatar avatar-lg">Z</span>',
        )
