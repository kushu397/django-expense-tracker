from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Expense, Category, ExpenseItem


# ==========================================
# USER REGISTRATION FORM
# ==========================================

class UserRegisterForm(UserCreationForm):

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email',
        })
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username',
            'autocomplete': 'username',
        })

        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a password',
            'autocomplete': 'new-password',
        })

        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password',
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user


# ==========================================
# EXPENSE FORM
# ==========================================

class ExpenseForm(forms.ModelForm):

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Save the current user for form validation
        self.user = user

        # Show only categories belonging to this user
        if user:
            self.fields['category'].queryset = (
                Category.objects.filter(user=user)
            )

            # Show items belonging to this user's categories
            self.fields['item'].queryset = (
                ExpenseItem.objects.filter(category__user=user)
            )

        else:
            self.fields['category'].queryset = (
                Category.objects.none()
            )

            self.fields['item'].queryset = (
                ExpenseItem.objects.none()
            )

        # Add CSS classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
            })

        self.fields['title'].widget.attrs.update({
            'placeholder': 'Enter expense title',
        })

        self.fields['amount'].widget.attrs.update({
            'placeholder': 'Enter amount',
            'min': '0',
            'step': '0.01',
        })

        self.fields['item'].widget.attrs.update({
            'id': 'id_item',
        })

        self.fields['category'].widget.attrs.update({
            'id': 'id_category',
        })

        self.fields['date'].widget.attrs.update({
            'type': 'date',
        })

        self.fields['notes'].widget.attrs.update({
            'placeholder': 'Add notes (optional)',
            'rows': 3,
        })

    class Meta:
        model = Expense

        fields = [
            'title',
            'amount',
            'category',
            'item',
            'date',
            'notes',
        ]

        widgets = {
            'title': forms.TextInput(),

            'amount': forms.NumberInput(attrs={
                'min': '0',
                'step': '0.01',
            }),

            'category': forms.Select(),

            'date': forms.DateInput(attrs={
                'type': 'date',
            }),

            'notes': forms.Textarea(attrs={
                'rows': 3,
            }),
        }

    # ======================================
    # VALIDATE EXPENSE AMOUNT
    # ======================================

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')

        if amount is not None and amount < 0:
            raise forms.ValidationError(
                'Expense amount cannot be negative.'
            )

        return amount

    # ======================================
    # VALIDATE CATEGORY AND ITEM
    # ======================================

    def clean(self):
        cleaned_data = super().clean()

        category = cleaned_data.get('category')
        item = cleaned_data.get('item')

        if category and item:
            if item.category_id != category.id:
                raise forms.ValidationError(
                    'Selected item does not belong '
                    'to the selected category.'
                )

        return cleaned_data