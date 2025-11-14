import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
import string


class OTP(models.Model):
    """
    Model to store OTP codes for user authentication.
    OTPs expire after 10 minutes.
    """
    otp_code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_codes')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'otp'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # OTP expires in 10 minutes
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        """Check if OTP is still valid (not expired and not used)"""
        return (
            not self.is_used and
            not self.is_verified and
            timezone.now() < self.expires_at
        )
    
    @staticmethod
    def generate_otp():
        """Generate a random 6-digit OTP"""
        return ''.join(random.choices(string.digits, k=6))
    
    def __str__(self):
        return f"OTP for {self.user.username} - {'Valid' if self.is_valid() else 'Invalid'}"
