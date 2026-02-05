from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    comment_body = forms.CharField(
        widget=forms.Textarea(
            attrs={"placeholder": "Write Comment with Description Word ", "rows": 4}
        ),
        label=False,
        required=True,
    )

    class Meta:
        model = Comment
        fields = ("comment_body",)

    def clean_comment_body(self):
        if len(self.cleaned_data["comment_body"]) < 10:
            raise forms.ValidationError(
                "Comment should be at least more then 10 length"
            )
        return self.cleaned_data["comment_body"]
