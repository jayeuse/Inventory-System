
      const loginCard = document.getElementById("login-card");
      const otpVerificationCard = document.getElementById("otp-verification-card");
      const forgotUsernameCard = document.getElementById(
        "forgot-username-card"
      );
      const verificationCard = document.getElementById("verification-card");
      const forgotPasswordCard = document.getElementById(
        "forgot-password-card"
      );
      const successCard = document.getElementById("success-card");

      const forgotPasswordLink = document.getElementById(
        "forgot-password-link"
      );
      const backToLoginFromOtp = document.getElementById(
        "back-to-login-from-otp"
      );
      const backToLoginFromUsername = document.getElementById(
        "back-to-login-from-username"
      );
      const backToLoginFromPassword = document.getElementById(
        "back-to-login-from-password"
      );
      const backToUsername = document.getElementById("back-to-username");
      const backToLoginSuccess = document.getElementById(
        "back-to-login-success"
      );
      const findAccountBtn = document.getElementById("find-account-btn");
      const verifyBtn = document.getElementById("verify-btn");
      const resetPasswordBtn = document.getElementById("reset-password-btn");

      // OTP-related variables
      let otpSession = null;
      let userEmail = null;
      
      // Password reset variables
      let resetSession = null;
      let resetUsername = null;

      function showCard(cardToShow) {
        [
          loginCard,
          otpVerificationCard,
          forgotUsernameCard,
          verificationCard,
          forgotPasswordCard,
          successCard,
        ].forEach((card) => {
          if (card) {
            card.classList.add("hidden");
            card.classList.remove("active");
          }
        });
        if (cardToShow) {
          cardToShow.classList.remove("hidden");
          cardToShow.classList.add("active");
        }

        if (cardToShow === verificationCard || cardToShow === otpVerificationCard) {
          setTimeout(() => {
            const firstInput = document.querySelector('.verification-code[data-index="0"]');
            if (firstInput) firstInput.focus();
          }, 300);
        }
      }

      if (forgotPasswordLink) {
        forgotPasswordLink.addEventListener("click", (e) => {
          e.preventDefault();
          showCard(forgotUsernameCard);
        });
      }
      
      if (backToLoginFromOtp) {
        backToLoginFromOtp.addEventListener("click", (e) => {
          e.preventDefault();
          showCard(loginCard);
        });
      }
      
      if (backToLoginFromUsername) {
        backToLoginFromUsername.addEventListener("click", (e) => {
          e.preventDefault();
          showCard(loginCard);
        });
      }
      
      if (backToLoginFromPassword) {
        backToLoginFromPassword.addEventListener("click", (e) => {
          e.preventDefault();
          showCard(loginCard);
        });
      }
      
      if (backToUsername) {
        backToUsername.addEventListener("click", (e) => {
          e.preventDefault();
          resetSession = null;
          resetUsername = null;
          showCard(loginCard);
        });
      }
      
      if (backToLoginSuccess) {
        backToLoginSuccess.addEventListener("click", () => showCard(loginCard));
      }

      if (findAccountBtn) {
        findAccountBtn.addEventListener("click", () => showCard(verificationCard));
      }
      
      if (verifyBtn) {
        verifyBtn.addEventListener("click", () => showCard(forgotPasswordCard));
      }
      
      if (resetPasswordBtn) {
        resetPasswordBtn.addEventListener("click", () => showCard(successCard));
      }

      document.querySelectorAll(".password-toggle").forEach((toggle) => {
        toggle.addEventListener("click", (e) => {
          const input = e.target.previousElementSibling;
          if (input.type === "password") {
            input.type = "text";
            e.target.textContent = "Hide";
          } else {
            input.type = "password";
            e.target.textContent = "Show";
          }
        });
      });

      // Setup verification code inputs using event delegation
      document.addEventListener("input", function (e) {
        if (e.target.classList.contains("verification-code")) {
          const value = e.target.value;
          const index = parseInt(e.target.getAttribute("data-index"));
          const container = e.target.closest(".verification-inputs");
          const allInputs = container.querySelectorAll(".verification-code");
          
          if (value && value.length === 1) {
            if (index < allInputs.length - 1) {
              allInputs[index + 1].focus();
            }
          }
        }
      });

      document.addEventListener("keydown", function (e) {
        if (e.target.classList.contains("verification-code")) {
          const index = parseInt(e.target.getAttribute("data-index"));
          const container = e.target.closest(".verification-inputs");
          const allInputs = container.querySelectorAll(".verification-code");

          if (e.key === "Backspace") {
            if (e.target.value === "" && index > 0) {
              allInputs[index - 1].focus();
            }
          }

          if (e.key === "ArrowLeft" && index > 0) {
            allInputs[index - 1].focus();
          }

          if (e.key === "ArrowRight" && index < allInputs.length - 1) {
            allInputs[index + 1].focus();
          }
        }
      });

      document.addEventListener("paste", function (e) {
        if (e.target.classList.contains("verification-code")) {
          e.preventDefault();
          const pastedData = e.clipboardData.getData("text").trim();
          const container = e.target.closest(".verification-inputs");
          const allInputs = container.querySelectorAll(".verification-code");

          if (pastedData.length === 6) {
            for (let i = 0; i < 6; i++) {
              if (i < allInputs.length) {
                allInputs[i].value = pastedData[i];
              }
            }
            allInputs[5].focus();
          }
        }
      });

      // Login button handler with OTP
      const loginBtn = document.getElementById("login-btn");
      if (loginBtn) {
        loginBtn.addEventListener("click", async function (e) {
          e.preventDefault();
          
          const username = document.getElementById("login-username").value;
          const password = document.getElementById("login-password").value;
          const errorDiv = document.getElementById("login-error");
          
          // Hide forgot password link initially
          if (forgotPasswordLink) {
            forgotPasswordLink.style.display = "none";
          }
          
          // Clear previous errors
          if (errorDiv) errorDiv.style.display = "none";
          
          if (!username || !password) {
            if (errorDiv) {
              errorDiv.textContent = "Please enter both username and password";
              errorDiv.style.display = "block";
            }
            return;
          }
          
          // Disable button and show loading
          loginBtn.disabled = true;
          loginBtn.textContent = "Logging in...";
          
          try {
            const response = await fetch('/api/auth/login/', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
              },
              body: JSON.stringify({ username, password })
            });
            
            const data = await response.json();
            
            if (response.ok) {
              // Store OTP session
              otpSession = data.otp_session;
              userEmail = data.email;
              
              // Display masked email
              const emailDisplay = document.getElementById("user-email-display");
              if (emailDisplay) emailDisplay.textContent = userEmail;
              
              // Clear OTP inputs
              document.querySelectorAll('.verification-code').forEach(input => {
                input.value = '';
              });
              
              // Show OTP verification card
              showCard(otpVerificationCard);
            } else {
              // Show error message
              if (errorDiv) {
                errorDiv.textContent = data.error || "Login failed";
                errorDiv.style.display = "block";
              }
              
              // If error is "Invalid username or password", check if username exists
              if (data.error === "Invalid username or password" && username) {
                // Check if username exists
                try {
                  const checkResponse = await fetch('/api/auth/check-username/', {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json',
                      'X-CSRFToken': getCSRFToken()
                    },
                    body: JSON.stringify({ username })
                  });
                  
                  if (checkResponse.ok) {
                    // Username exists, so wrong password - show forgot password link
                    if (forgotPasswordLink) {
                      forgotPasswordLink.style.display = "block";
                      resetUsername = username; // Store for later use
                    }
                  }
                } catch (error) {
                  // If check fails, don't show forgot password link
                  console.error("Failed to check username:", error);
                }
              }
            }
          } catch (error) {
            if (errorDiv) {
              errorDiv.textContent = "Network error. Please try again.";
              errorDiv.style.display = "block";
            }
          } finally {
            loginBtn.disabled = false;
            loginBtn.textContent = "Log In";
          }
        });
      }
      
      // Handle OTP verification
      const verifyOtpBtn = document.getElementById("verify-otp-btn");
      if (verifyOtpBtn) {
        verifyOtpBtn.addEventListener("click", async function (e) {
          e.preventDefault();
          
          // Collect OTP code
          const otpInputs = document.querySelectorAll('.verification-code');
          const otpCode = Array.from(otpInputs).map(input => input.value).join('');
          const errorDiv = document.getElementById("otp-error");
          
          if (errorDiv) errorDiv.style.display = "none";
          
          if (otpCode.length !== 6) {
            if (errorDiv) {
              errorDiv.textContent = "Please enter the complete 6-digit code";
              errorDiv.style.display = "block";
            }
            return;
          }
          
          verifyOtpBtn.disabled = true;
          verifyOtpBtn.textContent = "Verifying...";
          
          try {
            const response = await fetch('/api/auth/verify-otp/', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
              },
              body: JSON.stringify({
                otp_session: otpSession,
                otp_code: otpCode
              })
            });
            
            const data = await response.json();
            
            if (response.ok) {
              // OTP verified successfully, redirect to dashboard
              window.location.href = '/dashboard/';
            } else {
              if (errorDiv) {
                errorDiv.textContent = data.error || "Verification failed";
                errorDiv.style.display = "block";
              }
            }
          } catch (error) {
            if (errorDiv) {
              errorDiv.textContent = "Network error. Please try again.";
              errorDiv.style.display = "block";
            }
          } finally {
            verifyOtpBtn.disabled = false;
            verifyOtpBtn.textContent = "Verify Code";
          }
        });
      }
      
      // Handle Resend OTP
      const resendOtpLink = document.getElementById("resend-otp-link");
      if (resendOtpLink) {
        resendOtpLink.addEventListener("click", async function (e) {
          e.preventDefault();
          
          const errorDiv = document.getElementById("otp-error");
          if (errorDiv) errorDiv.style.display = "none";
          
          const originalText = resendOtpLink.textContent;
          resendOtpLink.textContent = "Sending...";
          
          try {
            const response = await fetch('/api/auth/resend-otp/', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
              },
              body: JSON.stringify({
                otp_session: otpSession
              })
            });
            
            const data = await response.json();
            
            if (response.ok) {
              // Update OTP session
              otpSession = data.otp_session;
              
              // Clear OTP inputs
              document.querySelectorAll('.verification-code').forEach(input => {
                input.value = '';
              });
              
              // Show success message
              alert("A new verification code has been sent to your email!");
            } else {
              if (errorDiv) {
                errorDiv.textContent = data.error || "Failed to resend code";
                errorDiv.style.display = "block";
              }
            }
          } catch (error) {
            if (errorDiv) {
              errorDiv.textContent = "Network error. Please try again.";
              errorDiv.style.display = "block";
            }
          } finally {
            resendOtpLink.textContent = originalText;
          }
        });
      }

      // Forgot Password Link - Start password reset flow
      if (forgotPasswordLink) {
        forgotPasswordLink.addEventListener("click", async function (e) {
          e.preventDefault();
          
          if (!resetUsername) {
            resetUsername = document.getElementById("login-username").value;
          }
          
          if (!resetUsername) {
            alert("Please enter your username first.");
            return;
          }
          
          // Request password reset OTP
          const errorDiv = document.getElementById("login-error");
          if (errorDiv) errorDiv.style.display = "none";
          
          try {
            const response = await fetch('/api/auth/request-password-reset/', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
              },
              body: JSON.stringify({ username: resetUsername })
            });
            
            const data = await response.json();
            
            if (response.ok) {
              // Store reset session
              resetSession = data.reset_session;
              userEmail = data.email;
              
              // Display masked email in verification card
              const resetEmailDisplay = document.getElementById("reset-email-display");
              if (resetEmailDisplay) resetEmailDisplay.textContent = userEmail;
              
              // Clear verification inputs
              document.querySelectorAll('.reset-verification-code').forEach(input => {
                input.value = '';
              });
              
              // Show verification card
              showCard(verificationCard);
            } else {
              alert(data.error || "Failed to send password reset code");
            }
          } catch (error) {
            alert("Network error. Please try again.");
          }
        });
      }
      
      // Verify Reset OTP Button
      if (verifyBtn) {
        verifyBtn.addEventListener("click", async function (e) {
          e.preventDefault();
          
          // Collect OTP code from reset verification inputs
          const otpInputs = document.querySelectorAll('.reset-verification-code');
          const otpCode = Array.from(otpInputs).map(input => input.value).join('');
          const errorDiv = document.getElementById("reset-otp-error");
          
          if (errorDiv) errorDiv.style.display = "none";
          
          if (otpCode.length !== 6) {
            if (errorDiv) {
              errorDiv.textContent = "Please enter the complete 6-digit code";
              errorDiv.style.display = "block";
            }
            return;
          }
          
          verifyBtn.disabled = true;
          verifyBtn.textContent = "Verifying...";
          
          try {
            const response = await fetch('/api/auth/verify-reset-otp/', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
              },
              body: JSON.stringify({
                reset_session: resetSession,
                otp_code: otpCode
              })
            });
            
            const data = await response.json();
            
            if (response.ok) {
              // OTP verified, show password reset form
              showCard(forgotPasswordCard);
            } else {
              if (errorDiv) {
                errorDiv.textContent = data.error || "Verification failed";
                errorDiv.style.display = "block";
              }
            }
          } catch (error) {
            if (errorDiv) {
              errorDiv.textContent = "Network error. Please try again.";
              errorDiv.style.display = "block";
            }
          } finally {
            verifyBtn.disabled = false;
            verifyBtn.textContent = "Verify Code";
          }
        });
      }
      
      // Reset Password Button
      if (resetPasswordBtn) {
        resetPasswordBtn.addEventListener("click", async function (e) {
          e.preventDefault();
          
          const newPassword = document.getElementById("new-password").value;
          const confirmPassword = document.getElementById("confirm-password").value;
          const errorDiv = document.getElementById("reset-password-error");
          
          if (errorDiv) errorDiv.style.display = "none";
          
          if (!newPassword || !confirmPassword) {
            if (errorDiv) {
              errorDiv.textContent = "Please fill in both password fields";
              errorDiv.style.display = "block";
            }
            return;
          }
          
          if (newPassword !== confirmPassword) {
            if (errorDiv) {
              errorDiv.textContent = "Passwords do not match";
              errorDiv.style.display = "block";
            }
            return;
          }
          
          if (newPassword.length < 8) {
            if (errorDiv) {
              errorDiv.textContent = "Password must be at least 8 characters long";
              errorDiv.style.display = "block";
            }
            return;
          }
          
          resetPasswordBtn.disabled = true;
          resetPasswordBtn.textContent = "Resetting...";
          
          try {
            const response = await fetch('/api/auth/reset-password/', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
              },
              body: JSON.stringify({
                reset_session: resetSession,
                new_password: newPassword,
                confirm_password: confirmPassword
              })
            });
            
            const data = await response.json();
            
            if (response.ok) {
              // Password reset successful
              showCard(successCard);
              
              // Clear all fields
              document.getElementById("new-password").value = "";
              document.getElementById("confirm-password").value = "";
              document.getElementById("login-username").value = "";
              document.getElementById("login-password").value = "";
              resetSession = null;
              resetUsername = null;
            } else {
              if (errorDiv) {
                errorDiv.textContent = data.error || "Password reset failed";
                errorDiv.style.display = "block";
              }
            }
          } catch (error) {
            if (errorDiv) {
              errorDiv.textContent = "Network error. Please try again.";
              errorDiv.style.display = "block";
            }
          } finally {
            resetPasswordBtn.disabled = false;
            resetPasswordBtn.textContent = "Reset Password";
          }
        });
      }
      
      // Resend Reset OTP
      const resendResetLink = document.getElementById("resend-reset-link");
      if (resendResetLink) {
        resendResetLink.addEventListener("click", async function (e) {
          e.preventDefault();
          
          const errorDiv = document.getElementById("reset-otp-error");
          if (errorDiv) errorDiv.style.display = "none";
          
          const originalText = resendResetLink.textContent;
          resendResetLink.textContent = "Sending...";
          
          try {
            const response = await fetch('/api/auth/resend-reset-otp/', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
              },
              body: JSON.stringify({
                reset_session: resetSession
              })
            });
            
            const data = await response.json();
            
            if (response.ok) {
              // Update reset session
              resetSession = data.reset_session;
              
              // Clear OTP inputs
              document.querySelectorAll('.reset-verification-code').forEach(input => {
                input.value = '';
              });
              
              // Show success message
              alert("A new verification code has been sent to your email!");
            } else {
              if (errorDiv) {
                errorDiv.textContent = data.error || "Failed to resend code";
                errorDiv.style.display = "block";
              }
            }
          } catch (error) {
            if (errorDiv) {
              errorDiv.textContent = "Network error. Please try again.";
              errorDiv.style.display = "block";
            }
          } finally {
            resendResetLink.textContent = originalText;
          }
        });
      }
