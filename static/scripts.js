function register_validation() {
    const password = document.getElementById('password-input').value.split(' ').join('')
    const phone = document.getElementById('phone-input').value
    const button = document.getElementById('submit-button')

    const preparedPhone = phone.substr(1, phone.length - 1)
    
    if(password.length >= 6 && preparedPhone.length + 1 == phone.length && preparedPhone.match(/^\d+$/)) {
        button.disabled = false
    } else {
        button.disabled = true
    }
}

function code_validation() {
    const code = document.getElementById('code-input').value
    const button = document.getElementById('submit-button')
    
    if(code.match(/^\d+$/) && code.length == 4) {
        button.disabled = false
    } else {
        button.disabled = true
    }
}