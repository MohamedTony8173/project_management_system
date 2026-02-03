from django import forms

from teams.models import Team
from .models import Project, Task


class TaskFormCreation(forms.ModelForm):
    team = forms.ModelChoiceField(
        queryset=Team.objects.only("name"),
        empty_label="Choose Team To Work With",
        widget=forms.Select(attrs={"class": "form-control mb-3"}),
        required=True,
    )
    project = forms.ModelChoiceField(
        queryset=Project.objects.only("name"),
        empty_label="Choose Project To Work With",
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
        label="Task Name",
        widget=forms.TextInput(
            attrs={"class": "form-control mb-3", "placeholder": "Task name"}
        ),
        required=True,
    )

    description = forms.CharField(
        label="Task description",
        widget=forms.Textarea(
            attrs={
                "class": "form-control mb-3",
                "placeholder": "Task description",
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
        model = Task
        fields = (
            "project",
            "team",
            "name",
            "description",
            "status",
            "priority",
            "active",
            "start_date",
            "due_date",
        )


