/**
 * Fitness Master - Main Interactive Script
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Password Visibility Toggle
  const toggleButtons = document.querySelectorAll('.toggle-password-btn');
  toggleButtons.forEach(button => {
    button.addEventListener('click', function () {
      const targetId = this.getAttribute('data-target');
      const input = document.getElementById(targetId);
      const icon = this.querySelector('i');

      if (input) {
        if (input.type === 'password') {
          input.type = 'text';
          if (icon) {
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
          }
        } else {
          input.type = 'password';
          if (icon) {
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
          }
        }
      }
    });
  });

  // 2. Real-time Live BMI Calculator in Registration / Edit forms
  const heightInput = document.getElementById('id_height');
  const weightInput = document.getElementById('id_weight');
  const liveBmiDisplay = document.getElementById('live-bmi-val');
  const liveBmiBadge = document.getElementById('live-bmi-badge');

  function updateLiveBmi() {
    if (!heightInput || !weightInput || !liveBmiDisplay) return;

    const h = parseFloat(heightInput.value);
    const w = parseFloat(weightInput.value);

    if (h > 50 && w > 20) {
      const heightInMeters = h / 100.0;
      const bmi = (w / (heightInMeters * heightInMeters)).toFixed(1);
      liveBmiDisplay.textContent = bmi;

      if (liveBmiBadge) {
        liveBmiBadge.style.display = 'inline-block';
        if (bmi < 18.5) {
          liveBmiBadge.className = 'badge bg-info text-dark';
          liveBmiBadge.textContent = 'Underweight';
        } else if (bmi < 25) {
          liveBmiBadge.className = 'badge bg-success';
          liveBmiBadge.textContent = 'Healthy';
        } else if (bmi < 30) {
          liveBmiBadge.className = 'badge bg-warning text-dark';
          liveBmiBadge.textContent = 'Overweight';
        } else {
          liveBmiBadge.className = 'badge bg-danger';
          liveBmiBadge.textContent = 'Obese';
        }
      }
    } else {
      liveBmiDisplay.textContent = '--';
      if (liveBmiBadge) liveBmiBadge.style.display = 'none';
    }
  }

  if (heightInput && weightInput) {
    heightInput.addEventListener('input', updateLiveBmi);
    weightInput.addEventListener('input', updateLiveBmi);
    updateLiveBmi();
  }

  // 3. Auto dismiss bootstrap alerts after 6 seconds
  const autoAlerts = document.querySelectorAll('.alert-dismissible');
  autoAlerts.forEach(alert => {
    setTimeout(() => {
      try {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        bsAlert.close();
      } catch (e) {
        // Fallback
        alert.remove();
      }
    }, 6000);
  });

  // 4. Image preview for file input
  const avatarInput = document.getElementById('id_profile_picture');
  const avatarPreview = document.getElementById('avatar-preview-img');
  if (avatarInput && avatarPreview) {
    avatarInput.addEventListener('change', function () {
      const file = this.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
          avatarPreview.src = e.target.result;
          avatarPreview.style.display = 'block';
          const placeholder = document.getElementById('avatar-preview-placeholder');
          if (placeholder) placeholder.style.display = 'none';
        };
        reader.readAsDataURL(file);
      }
    });
  }
});
