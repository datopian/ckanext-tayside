(function() {
  // This utility function hides the Allowed users field if the visibility field
  // is set to Public.

  var visibilitySelect = document.querySelector('select[name="private"]')
  var allowedUsersField = document.querySelector('label[for="allowed_users"]')
  var allowedUsersInfoBlock = document.querySelector('.allowed-users-info-block')

  if (visibilitySelect.value === 'False') {
    allowedUsersField.parentElement.style.display = 'none';
    allowedUsersInfoBlock.style.display = 'none';
  }

  visibilitySelect.addEventListener('change', function() {
    if (visibilitySelect.value === 'False') {
      allowedUsersField.parentElement.style.display = 'none';
      allowedUsersInfoBlock.style.display = 'none';
    } else if (visibilitySelect.value === 'True') {
      allowedUsersField.parentElement.style.display = 'block';
      allowedUsersInfoBlock.style.display = 'block';
    }
  })

})()
