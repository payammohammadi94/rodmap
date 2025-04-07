from rest_framework import permissions

class ReadOnlyOrAdmin(permissions.BasePermission):
    """
    دسترسی خواندن برای همه کاربران، اما فقط سوپر یوزرها می‌توانند تغییرات ایجاد کنند.
    """

    def has_permission(self, request, view):
        # همه کاربران می‌توانند درخواست‌های GET, HEAD, OPTIONS را ارسال کنند
        if request.method in permissions.SAFE_METHODS:
            return True
        # فقط سوپر یوزرها می‌توانند درخواست‌های POST, PUT, DELETE را ارسال کنند
        return request.user.is_superuser