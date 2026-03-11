
new Chart(document.getElementById('dailyChart'), {

type: 'bar',

data: {

labels: ['Mon','Tue','Wed','Thu','Fri','Sat'],

datasets: [

{
label:'Enquiries',
backgroundColor:'#f6c23e',
data:[5,8,6,10,7,4]
},

{
label:'Admissions',
backgroundColor:'#e74a3b',
data:[2,4,3,5,4,2]
}

]

}

});
