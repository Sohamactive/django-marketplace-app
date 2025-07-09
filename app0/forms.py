from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'id': 'name',
            'placeholder': 'enter your name'
        }),
        label='Enter your name',
        required=True
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'id': 'email',  #  changed from 'id': 'id'
            'placeholder': 'enter your email'
        }),
        label="Enter your email",
        required=True
    )

    message = forms.CharField(
        widget=forms.Textarea(attrs={  #  FIXED: 'Testarea' → 'Textarea', 'attris' → 'attrs'
            'id': 'message',
            'placeholder': 'enter your message'
        }),
        label="Enter your message",
        required=True
    )
