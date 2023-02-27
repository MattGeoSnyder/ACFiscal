let tableBody = document.querySelector('tbody')
let searchForm = document.querySelector('#search-form')

async function queryCredits() {
    let rows = document.querySelectorAll('.credit')
    for (let row of rows){
        tableBody.removeChild(row);
    }

    let params = {};
    let search_terms = document.querySelectorAll('.search-value');
    for (let input of search_terms){
        params[input.name] = input.value;
    }

    let res = await axios.get('/api/search', { params });
    for (let credit of res.data['credits']){
        let tr = document.createElement('tr');
        let received = document.createElement('td');
        let claimed = document.createElement('td');
        let booked = document.createElement('td');
        let bank = document.createElement('td');
        let department = document.createElement('td');
        let amount = document.createElement('td');
        let roc = document.createElement('td');
        let description = document.createElement('td');

        if (credit.roc.id){
            let a = document.createElement('a');
            a.href = `http://localhost:5000/fiscal/book/${roc.id}`;
            a.innerText = credit.roc.filename;
            roc.appendChild(a);
        }
        
        received.innerText = credit.received;
        claimed.innerText = credit.claimed;
        booked.innerText = credit.booked
        bank.innerText = credit.bank;
        department.innerText = credit.department;
        amount.innerText = credit.amount;
        description.innerText = credit.description;

        let cols = [received, claimed, booked, bank, department, amount, roc, description];
        for (let col of cols){
            tr.append(col);
        }
        
        tr.classList.add('credit')

        tableBody.append(tr);
    }

}

window.addEventListener('load', async (e) => {
    await queryCredits();
})

searchForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    await queryCredits();
})
