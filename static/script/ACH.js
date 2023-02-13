let button = document.querySelector('#claim');
let checkboxes = document.querySelectorAll('input');
let form = document.querySelector('form')
let claimed = [];

for (let checkbox of checkboxes){
    console.log(checkbox)
    checkbox.addEventListener('click', function(e) {

        if (e.target.checked) {
            claimed.push(parseInt(e.target.value));
        } 
        else {
            index = claimed.indexOf(parseInt(e.target.value));
            if (index > -1) {
                claimed.splice(index, 1);
            }
        }
    
        if (claimed.length > 0){
            button.disabled = false;
        }
        else {
            button.disabled = true;
        }
    });
}

// form.addEventListener('submit', async function(e) {
//     e.preventDefault()
//     let res = await axios.post('/fiscal/ACH/claim', data={
//                                                         'ach_credits': claimed
//                                                     });                                                       
// })