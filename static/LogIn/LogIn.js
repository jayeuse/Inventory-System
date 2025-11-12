   <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>

      const loginCard = document.getElementById("login-card");
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

      function showCard(cardToShow) {
        [
          loginCard,
          forgotUsernameCard,
          verificationCard,
          forgotPasswordCard,
          successCard,
        ].forEach((card) => {
          card.classList.add("hidden");
          card.classList.remove("active");
        });
        cardToShow.classList.remove("hidden");
        cardToShow.classList.add("active");

        if (cardToShow === verificationCard) {
          setTimeout(() => {
            document
              .querySelector('.verification-code[data-index="0"]')
              .focus();
          }, 300);
        }
      }

      forgotPasswordLink.addEventListener("click", () =>
        showCard(forgotUsernameCard)
      );
      backToLoginFromUsername.addEventListener("click", () =>
        showCard(loginCard)
      );
      backToLoginFromPassword.addEventListener("click", () =>
        showCard(loginCard)
      );
      backToUsername.addEventListener("click", () =>
        showCard(forgotUsernameCard)
      );
      backToLoginSuccess.addEventListener("click", () => showCard(loginCard));

      findAccountBtn.addEventListener("click", () =>
        showCard(verificationCard)
      );
      verifyBtn.addEventListener("click", () => showCard(forgotPasswordCard));
      resetPasswordBtn.addEventListener("click", () => showCard(successCard));

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

      document.addEventListener("DOMContentLoaded", function () {
        const verificationInputs =
          document.querySelectorAll(".verification-code");

        verificationInputs.forEach((input) => {
          input.addEventListener("input", function (e) {
            const value = e.target.value;
            const index = parseInt(e.target.getAttribute("data-index"));
            if (value && value.length === 1) {
              if (index < verificationInputs.length - 1) {
                verificationInputs[index + 1].focus();
              }
            }
          });

          input.addEventListener("keydown", function (e) {
            const index = parseInt(e.target.getAttribute("data-index"));

            if (e.key === "Backspace") {
              if (e.target.value === "" && index > 0) {
                verificationInputs[index - 1].focus();
              }
            }

            if (e.key === "ArrowLeft" && index > 0) {
              verificationInputs[index - 1].focus();
            }

            if (
              e.key === "ArrowRight" &&
              index < verificationInputs.length - 1
            ) {
              verificationInputs[index + 1].focus();
            }
          });

          input.addEventListener("paste", function (e) {
            e.preventDefault();
            const pastedData = e.clipboardData.getData("text").trim();

            if (pastedData.length === 6) {
              for (let i = 0; i < 6; i++) {
                if (i < verificationInputs.length) {
                  verificationInputs[i].value = pastedData[i];
                }
              }
              verificationInputs[5].focus();
            }
          });
        });
      });