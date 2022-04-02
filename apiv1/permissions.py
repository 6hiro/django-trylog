from rest_framework import permissions


class InOwnOrReadOnly(permissions.BasePermission):
    """Allow user to edit their own usermodel"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user


class IsOwnProfileOrReadOnly(permissions.BasePermission):
    """Allow user to edit their own profile"""

    def has_object_permission(self, request, view, obj):
        """Check user is trying to edit their own profile"""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsOwnPostOrReadOnly(permissions.BasePermission):
    """Allow user to edit their own post"""

    def has_object_permission(self, request, view, obj):
        """Check user is trying to edit their own post"""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.posted_by == request.user


class IsOwnRoadmapOrReadOnly(permissions.BasePermission):
    """Allow user to edit their own roadmap"""

    def has_object_permission(self, request, view, obj):
        """Check user is trying to edit their own roadmap"""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.challenger == request.user


class IsOwnStepOrReadOnly(permissions.BasePermission):
    """Allow user to edit their own step"""

    def has_object_permission(self, request, view, obj):
        """Check user is trying to edit their own step"""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.roadmap.challenger == request.user


class IsOwnLookBackOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        """Allow user to edit their own lookback"""
        if request.method in permissions.SAFE_METHODS:
            return True
        """Check user is trying to edit their own lookback"""
        return obj.step.roadmap.challenger.id == request.user.id
