from django.shortcuts import render, redirect

from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post
from .forms import PostForm


class IndexView(TemplateView):
    login_url = '/accounts/login/'
    def get(self, request, *args, **kwargs):
        #Postクラスのインスタンスをpost_dataに代入
        #クエリ発行を防ぐためselect_relatedでauthorクエリのみ発行させる
        post_data = Post.objects.order_by("-id").select_related('author')
        #render関数を使用して、テンプレートにデータを渡す
        return render(request, 'app/index.html', {
            'post_data': post_data,
        })

#アカウント主又はスーパーユーザーのみ処理可能
#accountの方にユーザーデータベースがあるので通常のままでは使えない
#post_dataでPostクラスのインスタンスを作成する必要がある
class OnlyYouMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        post_data = Post.objects.get(id=self.kwargs['pk'])
        user = self.request.user
        return user.id == post_data.author.id or user.is_superuser

#aa
class PostDetailView(View):
    def get(self, request, *args, **kwargs):
        post_data = Post.objects.get(id=self.kwargs['pk'])
        return render(request, 'app/post_detail.html', {
            'post_data': post_data
        })
#aa
class CreatePostView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = PostForm(request.POST or None)

        return render(request, 'app/post_form.html', {
            'form': form
        })

    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST or None)

        if form.is_valid():
            post_data = Post()
            post_data.author = request.user
            post_data.title = form.cleaned_data['title']
            post_data.content = form.cleaned_data['content']
            post_data.save()
            return redirect('post_detail', post_data.id)

        return render(request, 'app/post_form.html', {
            'form': form
        })

#aa
class PostEditView(OnlyYouMixin, View):
    def get(self, request, *args, **kwargs):
        post_data = Post.objects.get(id=self.kwargs['pk'])
        form = PostForm(
            request.POST or None,
            initial={
                'title': post_data.title,
                'content': post_data.content,
            }
        )

        return render(request, 'app/post_form.html', {
            'form': form
        })

    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST or None)

        if form.is_valid():
            post_data = Post.objects.get(id=self.kwargs['pk'])
            post_data.title = form.cleaned_data['title']
            post_data.content = form.cleaned_data['content']
            post_data.save()
            return redirect('post_detail', self.kwargs['pk'])

        return render(request, 'app/post_form.html', {
            'form': form
        })
#aa
class PostDeleteView(OnlyYouMixin, View):
    def get(self, request, *args, **kwargs):
        post_data = Post.objects.get(id=self.kwargs['pk'])
        return render(request, 'app/post_delete.html', {
            'post_data': post_data
        })

    def post(self, request, *args, **kwargs):
        post_data = Post.objects.get(id=self.kwargs['pk'])
        post_data.delete()
        return redirect('index')