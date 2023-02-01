/* Add styling to Django form elements */
let formGroup = document.querySelector("#id_form_group");
let selectbox = formGroup.querySelector("select");
let fileinput = formGroup.querySelector("input[type='file']");
selectbox.classList.add("input-reset", "ba", "b--black-20", "pa2", "mb2", "db", "w-20");
fileinput.classList.add("input-reset", "ba", "b--black-20", "pa2", "mb2", "db", "w-20");

let labels = formGroup.querySelectorAll("label");
labels.forEach(label => {
    label.classList.add("db", "fw6", "lh-copy", "f6");
});
        