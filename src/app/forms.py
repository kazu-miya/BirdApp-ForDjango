from django import forms


class PostForm(forms.Form):
    title = forms.CharField(max_length=30, label='タイトル')
    content = forms.CharField(label='内容', widget=forms.Textarea())
    #required=Trueで画像入力を必須条件とする
    image = forms.ImageField(label='野鳥画像', required=False)