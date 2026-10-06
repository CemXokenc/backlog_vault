from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from vault.models import Comment
from vault.tests.helpers import (
    create_catalog,
    create_collection,
    create_gamer,
    create_moderator,
)


class CommentTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.game = create_catalog().game
        cls.author = create_gamer("author")
        cls.other = create_gamer("other")
        cls.moderator = create_moderator()
        cls.collection = create_collection(cls.author, games=[cls.game])
        cls.game_url = reverse("vault:game-comment-add", args=[cls.game.pk])
        cls.collection_url = reverse(
            "vault:collection-comment-add",
            args=[cls.collection.pk],
        )


class CommentModelTests(CommentTestCase):
    def test_comment_needs_exactly_one_target(self):
        for target in ({}, {"game": self.game, "collection": self.collection}):
            with self.subTest(target=target):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    Comment.objects.create(
                        author=self.author,
                        text="Hi",
                        **target,
                    )

    def test_target_and_url(self):
        on_game = Comment.objects.create(
            author=self.author,
            game=self.game,
            text="Nice",
        )
        on_collection = Comment.objects.create(
            author=self.author,
            collection=self.collection,
            text="Nice",
        )
        self.assertEqual(on_game.target, self.game)
        self.assertEqual(on_collection.target, self.collection)
        self.assertEqual(
            on_game.get_absolute_url(),
            self.game.get_absolute_url(),
        )


class CommentCreateTests(CommentTestCase):
    def test_gamer_can_comment_on_game_and_collection(self):
        self.client.force_login(self.other)
        response = self.client.post(self.game_url, {"text": "Great game"})
        self.assertRedirects(response, self.game.get_absolute_url())
        self.client.post(self.collection_url, {"text": "Nice list"})
        self.assertTrue(
            Comment.objects.filter(
                author=self.other,
                game=self.game,
                text="Great game",
            ).exists(),
        )
        self.assertTrue(
            Comment.objects.filter(
                author=self.other,
                collection=self.collection,
                text="Nice list",
            ).exists(),
        )

    def test_guest_cannot_comment(self):
        for url in (self.game_url, self.collection_url):
            with self.subTest(url=url):
                response = self.client.post(url, {"text": "Spam"})
                self.assertEqual(response.status_code, 302)
                self.assertIn("/accounts/login/", response["Location"])
        self.assertEqual(Comment.objects.count(), 0)

    def test_empty_and_too_long_comments_are_rejected(self):
        self.client.force_login(self.other)
        for text in ("", "   ", "x" * 1001):
            with self.subTest(length=len(text)):
                self.client.post(self.game_url, {"text": text})
        self.assertEqual(Comment.objects.count(), 0)

    def test_comment_endpoint_requires_post(self):
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(self.game_url).status_code, 405)


class CommentDisplayTests(CommentTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        Comment.objects.create(
            author=cls.author,
            game=cls.game,
            text="Visible to everyone",
        )

    def test_guest_sees_comments_but_no_form(self):
        response = self.client.get(self.game.get_absolute_url())
        self.assertContains(response, "Visible to everyone")
        self.assertContains(response, "to leave a comment")
        self.assertNotContains(response, self.game_url)

    def test_gamer_sees_comment_form_on_game_and_collection(self):
        self.client.force_login(self.other)
        response = self.client.get(self.game.get_absolute_url())
        self.assertContains(response, self.game_url)
        response = self.client.get(self.collection.get_absolute_url())
        self.assertContains(response, self.collection_url)

    def test_comments_are_not_mixed_between_objects(self):
        self.client.force_login(self.other)
        response = self.client.get(self.collection.get_absolute_url())
        self.assertNotContains(response, "Visible to everyone")

    def test_comment_text_is_escaped(self):
        Comment.objects.create(
            author=self.author,
            game=self.game,
            text="<script>alert(1)</script>",
        )
        response = self.client.get(self.game.get_absolute_url())
        self.assertNotContains(response, "<script>alert(1)</script>")


class CommentDeleteTests(CommentTestCase):
    def setUp(self):
        self.comment = Comment.objects.create(
            author=self.author,
            game=self.game,
            text="Delete me",
        )
        self.url = reverse("vault:comment-delete", args=[self.comment.pk])

    def test_author_can_delete_own_comment(self):
        self.client.force_login(self.author)
        response = self.client.post(self.url)
        self.assertRedirects(response, self.game.get_absolute_url())
        self.assertFalse(Comment.objects.exists())

    def test_moderator_can_delete_any_comment(self):
        self.client.force_login(self.moderator)
        self.client.post(self.url)
        self.assertFalse(Comment.objects.exists())

    def test_other_gamer_gets_403(self):
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(self.url).status_code, 403)
        self.assertTrue(Comment.objects.exists())

    def test_guest_cannot_delete(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.exists())

    def test_delete_button_follows_permissions(self):
        page = self.game.get_absolute_url()
        for gamer, visible in (
            (self.author, True),
            (self.moderator, True),
            (self.other, False),
        ):
            self.client.force_login(gamer)
            response = self.client.get(page)
            with self.subTest(gamer=gamer.username):
                if visible:
                    self.assertContains(response, self.url)
                else:
                    self.assertNotContains(response, self.url)

    def test_deleting_game_removes_its_comments(self):
        self.game.delete()
        self.assertFalse(Comment.objects.exists())
