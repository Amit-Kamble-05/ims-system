new Chart(document.getElementById('revenueChart'), {

type: 'line',

data: {

labels: ['Jan','Feb','Mar','Apr','May','Jun'],

datasets: [{
    label: 'Revenue',
    borderColor: '#36b9cc',
    data: [12000,18000,15000,22000,20000,26000],
    fill:false
}]

}

});