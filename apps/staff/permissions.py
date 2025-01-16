from rest_framework.permissions import BasePermission

class IsRetail(BasePermission):
    """
    Employee can make transactions.
    """
    def has_permission(self, request, view):
        user = request.user
        if hasattr(user, "staff"):
            return not(user.staff.is_management or user.staff.is_warehouse) and user.is_authenticated
        return False


class IsAdmin(BasePermission):
    """
    Employee has administrative oversight of a specific facility
    """
    def has_permission(self, request, view):
        user = request.user
        if hasattr(user, "staff"):
            return user.staff.is_admin and user.is_authenticated
        return False
        

class IsWarehouse(BasePermission):
    """
    Employee has access to the Warehouse
    """
    def has_permission(self, request, view):
        user=request.user
        if hasattr(user, "staff"):
            return user.staff.is_warehouse and user.is_authenticated
        return False
    

class IsManagement(BasePermission):
    """
    Employee has oversight of all facilities
    """
    def has_permission(self, request, view):
        user=request.user
        if hasattr(user, "staff"):
            return user.staff.is_management and user.is_authenticated
        return False
    