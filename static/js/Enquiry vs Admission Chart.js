const enquiryChart = new Chart(
document.getElementById('enquiryChart'),

{
    type: 'bar',

    data: {

        labels: ['Jan','Feb','Mar','Apr','May','Jun'],

        datasets: [

        {
            label: 'Enquiries',
            backgroundColor: '#4e73df',
            data: [12,19,8,15,10,20]
        },

        {
            label: 'Admissions',
            backgroundColor: '#1cc88a',
            data: [5,9,6,10,7,12]
        }

        ]
    },

});
