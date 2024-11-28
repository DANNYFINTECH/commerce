from django import forms
from .models import Listing, Category

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_bid', 'image_url', 'category']

    # Adding the Category dropdown manually (ModelChoiceField automatically handles this)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label="Choose a Category", required=True)

    # Custom validation to ensure starting_bid is positive
    def clean_starting_bid(self):
        starting_bid = self.cleaned_data.get('starting_bid')
        if starting_bid <= 0:
            raise forms.ValidationError("Starting bid must be greater than zero.")
        return starting_bid

class BidForm(forms.Form):
    bid_amount = forms.DecimalField(max_digits=10, decimal_places=2, label="Bid Amount")

    # Custom validation for bid amount (ensure it's greater than the current price)
    def clean_bid_amount(self):
        bid_amount = self.cleaned_data.get('bid_amount')
        if bid_amount <= 0:
            raise forms.ValidationError("Bid amount must be greater than zero.")
        return bid_amount
