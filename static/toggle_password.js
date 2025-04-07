
// Toggle password box style between hidden (password) and displayed (text)
function toggleShowPwd() {
    console.log("Toggling password visibility");
    var prev = document.getElementById("password").type;
    if (prev == "password") {
        document.getElementById("password").type = "text";
    } else {
        document.getElementById("password").type = "password";
    }
}