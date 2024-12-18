from django.contrib import admin
from .models import Vendor

# Register your models here.
class VendorAdmin(admin.ModelAdmin):
  prepopulated_fields = {'vendor_slug': ('vendor_name',)}
  list_display = ['user','vendor_name','is_approved','created_at']
  list_filter = ['is_approved','created_at','modified_at']
  list_display_links = ['user','vendor_name']
  list_editable = ['is_approved']
  


admin.site.register(Vendor,VendorAdmin)