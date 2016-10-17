from django.contrib import admin
from django import forms

from config_storage import models

# Creaet your ModelAdmin


@admin.register(models.Storage)
class StorageAdmin(admin.ModelAdmin):

    def get_queryset(self, *args, **kwargs):
        models.confs.load()
        return super(StorageAdmin, self).get_queryset(*args, **kwargs).filter(is_active=True)

    def get_form(self, request, obj=None, **kwargs):
        # 此 Admin 关联的是 Storage ，但我们编辑的时候是按 Configuration 显示，保存的时候的切换回 Storage
        model_class = models.confs[obj.key]
        class DummyForm(forms.ModelForm):

            class Meta:
                #  实际对应的 Configuration
                model = model_class
                exclude = []

            # instance 替换为 Configuration，因为需要跟 Form.Meta.moel 对应
            def __init__(self, *args, **kwargs):
                self.instance = kwargs['instance'] = model_class()
                super(DummyForm, self).__init__(*args, **kwargs)

            # Fix: 'DummyForm' object has no attribute 'save_m2m'
            def save_m2m(self, *args, **kwargs):
                pass

            # 返回 Storage，因为 ModelAdmin 后续处理需要 Storage 类型的对象
            def save(self, *args, **kwargs):
                # 更新修改值到 Storage
                for k, v in self.cleaned_data.items():
                    if hasattr(self.instance, k):
                        obj.value[k] = v
                # 返回 Storage
                return obj

        return DummyForm
