function set(input){
  if(window.localStorage == null){
    alert('Local storage is required to set options');
    return;
  }
  window.localStorage.setItem(input.id, input.value);
}

function options(){
  if(window.localStorage == null){
    alert("LocalStorage must be enabled to change options.");
    document.getElementById('name').disabled = true;
    document.getElementById('username').disabled = true;
    document.getElementById('password').disabled = true;
    return;
  }
  else {
    inputs = document.getElementsByTagName('input');
    for(var i=0; i < inputs.length; i++){
      inputs[i].value = window.localStorage.getItem(inputs[i].id);
    }
  }
}

function auth_token(){
  // Create SWORD authentication token in agreed format
  var password = window.localStorage.getItem('password');
  var username = window.localStorage.getItem('username');
  password = MD5(password);
  token = 'username=' + username + ':password=' + password + ':nso';
  return MD5(token);
}