from .imp_libs import *
from django.utils import timezone
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from formtools.wizard.views import SessionWizardView
from chq_pay.forms import BankForm, CurrencyForm, PayeeForm
from chq_pay.models import Banks, Currencies, Payee
from datetime import datetime

class AppSetupWizard(SessionWizardView):
    template_name = "wizard/wizard.html"

    def get_form_list(self):
        """
        Dynamically adjust the form list based on model counts.
        """
        form_list = {}
        if not Banks.objects.exists():
            form_list["bank"] = BankForm
        if not Currencies.objects.exists():
            form_list["currency"] = CurrencyForm
        if not Payee.objects.exists():
            form_list["payee"] = PayeeForm

        if not form_list:  # If all models have data
            self.no_steps_required = True
        else:
            self.no_steps_required = False

        return form_list

    def dispatch(self, request, *args, **kwargs):
        """
        Check if there are any steps to process.
        """
        self.get_form_list()  # Populate `no_steps_required`
        if getattr(self, "no_steps_required", False):
            # messages.info(request, "All setup steps are already completed.")
            return HttpResponseRedirect(reverse("index"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, form, **kwargs):
        """
        Add step information to context.
        """
        context = super().get_context_data(form=form, **kwargs)
        context["step"] = self.steps.current
        return context

    def done(self, form_list, **kwargs):
        """
        Save the models when the wizard is completed.
        """
        for form in form_list:
            instance = form.save(commit=False)
            instance.created_by = self.request.user.id  # Use authenticated user ID
            instance.created_date = datetime.now()
            instance.modified_by = self.request.user.id
            instance.modified_date = datetime.now()
            instance.save()

        messages.success(self.request, "Wizard Complete, Enjoy the App Now!!")
        return HttpResponseRedirect(reverse("index"))


