from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from vault.forms import CommentForm
from vault.mixins import get_safe_next_url
from vault.models import Collection, Comment, Game


def add_comment(request, **target):
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        for field, obj in target.items():
            setattr(comment, field, obj)
        comment.save()
        messages.success(request, "Your comment was added.")
    else:
        messages.error(request, "A comment can't be empty or too long.")
    return redirect(next(iter(target.values())))


@login_required
@require_POST
def game_comment_add(request, pk):
    game = get_object_or_404(Game, pk=pk)
    return add_comment(request, game=game)


@login_required
@require_POST
def collection_comment_add(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    return add_comment(request, collection=collection)


@login_required
@require_POST
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    is_author = comment.author_id == request.user.pk
    if not (is_author or request.user.has_perm("vault.delete_comment")):
        raise PermissionDenied
    comment.delete()
    messages.success(request, "Comment was deleted.")
    return redirect(get_safe_next_url(request) or comment.target)
