const startButton = document.getElementById('start');
const stopButton = document.getElementById('stop');

startButton.addEventListener('click', function () {
    fetch('/data', {
        headers: {
            'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify({
            'cmd': 'Start',
            'sts': 'Start Req.'
        })
    })
        .then(function (response) {
            if (response.ok) {
                response.json()
                    .then(function (response) {
                        console.log(response)
                        document.getElementById("reqStatus").innerHTML = response["sts"];
                    });
            }
            else {
                throw Error('Something went wrong');
            }
        })
        .catch(function (error) {
            console.log(error);
        });
});

stopButton.addEventListener('click', function () {
    fetch('/data', {
        headers: {
            'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify({
            'cmd': 'Stop',
            'sts': 'Stop Req.'
        })
    })
        .then(function (response) {

            if (response.ok) {
                response.json()
                    .then(function (response) {
                        console.log(response)
                        document.getElementById("reqStatus").innerHTML = response["sts"];
                    });
            }
            else {
                throw Error('Something went wrong');
            }
        })
        .catch(function (error) {
            console.log(error);
        });
});

var myVar = setInterval(function () { displayRunT() }, 500);
function displayRunT() {
    fetch('/data')
        .then(function (response) {
            if (response.ok) {
                response.json()
                    .then(function (response) {
                        console.log(response)
                        document.getElementById("runTime").innerHTML = "Run Time: " + response["sts"];
                    });
            }
            else {
                throw Error('Something went wrong');
            }
        })
        .catch(function (error) {
            console.log(error);
        });
}