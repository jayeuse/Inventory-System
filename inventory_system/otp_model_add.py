

class OTP(models.Model):
    """
    Model to store OTP codes for user authentication.
    OTPs expire after 10 minutes.
    """
    otp_code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='otp_code')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='otp_codes',
        db_column='user_id'
    )
    otp = models.CharField(max_length=6, db_column='otp')
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    expires_at = models.DateTimeField(db_column='expires_at')
    is_used = models.BooleanField(default=False, db_column='is_used')
    is_verified = models.BooleanField(default=False, db_column='is_verified')
    
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
