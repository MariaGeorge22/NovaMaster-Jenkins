from django import forms
from post.models import Post


class newPostForm(forms.ModelForm):
    picture = forms.ImageField(
        required=True,
        widget=forms.ClearableFileInput(
            attrs={
                "class": "input-group",
            }
        ),
    )
    caption = forms.CharField(
        widget=forms.TextInput(attrs={"class": "input-group"}),
        required=True,
    )
    tags = forms.CharField(
        widget=forms.TextInput(attrs={"class": "input-group"}),
        required=True,
    )

    class Meta:
        model = Post
        fields = ["picture", "caption", "tags"]
