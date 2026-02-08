from django import forms

from teams.models import Team
from .models import Project,AttachMentFile


class ProjectFormCreation(forms.ModelForm):
    team = forms.ModelChoiceField(
        queryset=Team.objects.only("name"),
        empty_label="Choose Team To Work With",
        widget=forms.Select(attrs={"class": "form-control mb-3"}),
        required=True,
    )
    status = forms.ChoiceField(
        choices=[("", "-------------")] + list(Project.STATUS_CHOICE),
        widget=forms.Select(attrs={"class": "form-select mb-3"}),
        label="Choose Status",
        required=True,
    )
    priority = forms.ChoiceField(
        choices=[("", "-------------")] + list(Project.PRIORITY_CHOICE),
        widget=forms.Select(attrs={"class": "form-select mb-3"}),
        label="Choose Priority",
        required=True,
    )
    name = forms.CharField(
        label="Project Name",
        widget=forms.TextInput(
            attrs={"class": "form-control mb-3", "placeholder": "project name"}
        ),
        required=True,
    )
    client_company = forms.CharField(
        label="Client Company",
        widget=forms.TextInput(
            attrs={
                "class": "form-control mb-3",
                "placeholder": "client company  / site",
            }
        ),
        required=True,
    )
    description = forms.CharField(
        label="Project description",
        widget=forms.Textarea(
            attrs={
                "class": "form-control mb-3",
                "placeholder": "project description",
                "rows": 4,
            }
        ),
        required=True,
    )
    active = forms.CharField(
        label=" Active To Work ",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input p-2 mb-3 me-1"}),
    )
    start_date = forms.DateTimeField(
        label="Start Date",
        widget=forms.DateTimeInput(
            attrs={"type": "date", "class": "form-control mb-3"}
        ),
        required=True,
    )
    due_date = forms.DateField(
        label="Due Date",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control mb-3"}),
        required=True,
    )

    class Meta:
        model = Project
        fields = (
            "team",
            "name",
            "client_company",
            "description",
            "status",
            "priority",
            "active",
            "start_date",
            "due_date",
            "total_amount",
            "amount_spent",
            "estimated_duration",
        )

    def clean_total_amount(self):
        if self.cleaned_data.get("total_amount") < 0:
            raise forms.ValidationError("it should greater then zero")
        return self.cleaned_data["total_amount"]

    def clean_amount_spent(self):
        if self.cleaned_data.get("amount_spent") < 0:
            raise forms.ValidationError("it should greater then zero")
        return self.cleaned_data["amount_spent"]

    def clean_estimated_duration(self):
        if self.cleaned_data.get("estimated_duration") < 0:
            raise forms.ValidationError("it should greater then zero")
        return self.cleaned_data["estimated_duration"]


class AttachForm(forms.ModelForm):
    name = forms.CharField(label='Prefix Name ',required=True)
    class Meta:
        model = AttachMentFile
        fields = ['name','file_upload']