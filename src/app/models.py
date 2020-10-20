from django.conf import settings
from django.db import models
from django.utils import timezone




class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField("タイトル", max_length=200)
    #upload_toでmedia/imagesに格納される
    image = models.ImageField(upload_to='images', verbose_name='野鳥画像', null=True, blank=True) # 追加
    content = models.TextField("本文")
    created = models.DateTimeField("作成日", default=timezone.now)

    def __str__(self):
        return self.title

