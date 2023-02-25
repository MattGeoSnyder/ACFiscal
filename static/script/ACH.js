let button = document.querySelector('#claim');
let search_form = document.querySelector('#search-form');
let tableBody = document.querySelector('#credit-content')
let selected = [];

async function queryCredits() {
    let unchecked = document.querySelectorAll('.credit:not(.credit:checked)');
    for (let box of unchecked){
        let row = box.parentElement.parentElement;
        tableBody.removeChild(row);
    }

    let params = {};
    let search_terms = document.querySelectorAll('.search-value');
    for (let input of search_terms){
        params[input.name] = input.value;
    }
    params['selected'] = JSON.stringify(selected)

    let res = await axios.get('/api/search', { params });
    for (let credit of res.data['credits']){
        let tr = document.createElement('tr');
        let td = document.createElement('td');
        let claim = document.createElement('input');
        let date = document.createElement('td');
        let department = document.createElement('td');
        let bank = document.createElement('td');
        let amount = document.createElement('td');
        let description = document.createElement('td');

        claim.type = 'checkbox';
        claim.value = credit.id;
        claim.name = 'credit-id';
        claim.classList.add('credit')
        td.appendChild(claim)
        
        date.innerText = credit.received;
        department.innerText = credit.department;
        bank.innerText = credit.bank;
        amount.innerText = credit.amount;
        description.innerText = credit.description;

        let cols = [td, date, department, bank, amount, description];
        for (let col of cols){
            tr.append(col);
        }
        
        tableBody.append(tr);
    }

}

function addEventToCheckboxes() {
    let checkboxes = document.querySelectorAll('.credit');

    for (let checkbox of checkboxes){
        checkbox.addEventListener('click', function(e) {
    
            if (e.target.checked) {
                selected.push(parseInt(e.target.value));
            } 
            else {
                index = selected.indexOf(parseInt(e.target.value));
                if (index > -1) {
                    selected.splice(index, 1);
                }
            }
        
            if (selected.length > 0){
                button.disabled = false;
            }
            else {
                button.disabled = true;
            }
        });
    }    
}

window.addEventListener('load', async function(e){
    await queryCredits();

    let checkboxes = Array.from(document.querySelectorAll('.credit'));
    
    if (checkboxes.some((checkbox) => checkbox.checked)){
        button.disabled = false;
    }

    addEventToCheckboxes();
});


search_form.addEventListener('submit', async (e) => {

    e.preventDefault();

    await queryCredits();

    addEventToCheckboxes();
});


