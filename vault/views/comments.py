from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.views import generic

from vault.forms import CommentForm
from vault.mixins import NextUrlMixin
from vault.models import Collection, Comment, Game


class CommentAddView(LoginRequiredMixin, generic.View):
    """Base of the POST-only views that comment on a game or a collection."""

    target_model = None
    target_field = ""

    def post(self, request, pk):
        target = get_object_or_404(self.target_model, pk=pk)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            setattr(comment, self.target_field, target)
            comment.save()
            messages.success(request, "Your comment was added.")
        else:
            messages.error(request, "A comment can't be empty or too long.")

        return redirect(target)


class GameCommentAddView(CommentAddView):
    target_model = Game
    target_field = "game"


class CollectionCommentAddView(CommentAddView):
    target_model = Collection
    target_field = "collection"


class CommentDeleteView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    NextUrlMixin,
    generic.DeleteView,
):
    model = Comment
    http_method_names = ["post"]
    success_message = "Comment was deleted."

    def get_object(self, queryset=None):
        comment = super().get_object(queryset)
        user = self.request.user
        is_author = comment.author_id == user.pk
        if not (is_author or user.has_perm("vault.delete_comment")):
            raise PermissionDenied

        return comment

    def get_success_url(self):
        return self.get_next_url() or self.object.get_absolute_url()
