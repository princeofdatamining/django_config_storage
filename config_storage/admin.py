from django.contrib import admin, messages
from django import forms
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect

from . import models, constant

@admin.register(models.Storage)
class StorageAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return False

    def get_form(self, request, obj=None, **kwargs):
        model_class = models.configurations[obj.key]
        class DummyForm(forms.ModelForm):

            class Meta:
                model = model_class
                exclude = []

            def __init__(self, *args, **kwargs):
                # instance 替换为 Configuration
                self.instance = kwargs['instance'] = model_class()
                super(DummyForm, self).__init__(*args, **kwargs)

            def _save_m2m_dummy(self):
                pass

            def save(self, *args, **kwargs):
                # form.save_m2m()
                self.save_m2m = self._save_m2m_dummy
                # save configuration to storage
                for k, v in self.cleaned_data.items():
                    hasattr(self.instance, k) and setattr(self.instance, k, v)
                self.instance.save()
                # 把 instance 替换回 Storage
                return self.instance.storage

        return DummyForm
