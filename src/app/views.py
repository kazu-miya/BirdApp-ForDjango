import io
import sys
import os
import gc
import math
import tempfile
from django.shortcuts import render, redirect

from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post
from .forms import PostForm
from PIL import Image
from django.conf import settings

from memory_profiler import profile
from django.core.files.uploadedfile import InMemoryUploadedFile
from .darknet.python.darknet import detect, data_load
from .main import CatchData, ImgCrop, Square_main

net, meta = data_load()

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
            if request.FILES:
                a = image_resize(request.FILES['image'])
                post_data.image = image_resize2(a)
                del a
                gc.collect()
                
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
                'image': post_data.image,
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
            if request.FILES:
                post_data.image = request.FILES.get('image') # 追加
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

##画像変換
def image_resize(field):

    if field:
        im = Image.open(field)
        img = Square_main(im)
        #mediaの中で最後のファイルが自分のであるはず
        #変換処理ここまで
        #野鳥が複数羽いる場合、大きい方を出力
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85)
        output.seek(0)
        return InMemoryUploadedFile(output, 'ImageField',
                                    field.name,
                                    'image/jpeg',
                                    sys.getsizeof(output), None)
    else:
        return None
#aa
def image_resize2(field):

    if field:
        b = detect(net, meta, field)
        c=CatchData(b)
        img = Image.open(field)
        new_img=ImgCrop(c,img)
        #mediaの中で最後のファイルが自分のであるはず
        #変換処理ここまで
        #野鳥が複数羽いる場合、大きい方を出力
        output = io.BytesIO()
        new_img.save(output, format='JPEG', quality=85)
        output.seek(0)
        return InMemoryUploadedFile(output, 'ImageField',
                                    field.name,
                                    'image/jpeg',
                                    sys.getsizeof(output), None)
        
    else:
        return None