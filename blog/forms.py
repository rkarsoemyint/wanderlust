from django import forms
from .models import TravelPost
from .models import TravelPost, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = TravelPost
        fields = ['title', 'location', 'content', 'image']
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ခရီးစဉ်ခေါင်းစဉ်'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'သွားခဲ့တဲ့နေရာ'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'အသေးစိတ်ရေးရန်...'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write a comment...'}),
        }