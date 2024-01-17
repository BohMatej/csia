console.log(data);
const ROUTE = data.linelist
const ROUTELENGTH = ROUTE.length;
var currentrow = 0
var currentcolumn = 0
var guess = []
const STARTING_NUMBER_OF_GUESSES = 3 + parseInt(data.numberOfGuessesRaw) + parseInt(ROUTELENGTH);

// define task
document.getElementById("task").innerHTML = `Travel from ${data.stoplist[0]} to ${data.stoplist[data.stoplist.length - 1]} using ${data.linelist.length - 1} transfers.`;

// create cells for guessing
for (var i=0; i<STARTING_NUMBER_OF_GUESSES; i++){
    document.getElementById("guessspace").innerHTML += `
        <div id='guessrow_${i}' class='row guessrow mb-3'>
        </div>
    `;
    for (var j=0; j<ROUTELENGTH; j++){
        document.getElementById(`guessrow_${i}`).innerHTML += `
            <div id='guesscell_${i}_${j}' class='col guesscol'>
                <div id='guesscellcontainer_${i}_${j}' class='guesscellcontainer'>
                    <img src="/../static/other_icons/blankicon.png" alt='placeholder' width='48'>
                </div>
            </div>
        `;
    }
}

// create line buttons
for (var i=0; i<data.availablelines.length; i++){
    document.getElementById("buttonspace").innerHTML += `
        <span id='linespan_${data.availablelines[i]}' class='linespan'>
            <button id='linebtn_${data.availablelines[i]}' class='linebtn' onclick="clickLine(${data.availablelines[i]})">
                <img src="/../static/line_icons/line${data.availablelines[i]}.png" alt='Line ${data.availablelines[i]}' width='40'>
            </button>
        </span>
    `;
}

// create winner/loser popups
document.getElementById("winnerModalLabel").innerHTML = `
    Congratulations, you are correct!
`;

document.getElementById("loserModalLabel").innerHTML = `
    Looks like you got lost. Here's the route you were trying to guess.
`;

document.getElementById("winnerModalBody").innerHTML = "";
document.getElementById("loserModalBody").innerHTML = "";


for (var i=0; i<ROUTELENGTH; i++){
    var htmldump = ``
    // if (i == 0){
    //     htmldump += `Start by taking `;
    // }
    // else if (i<ROUTELENGTH-1){
    //     htmldump += `Transfer to `;
    // }
    if (i<ROUTELENGTH-1){
        if (data.walkingtransferlist[i+1] === null){
            htmldump += `
                <img src="/../static/line_icons/line${data.linelist[i]}.png" alt='Line ${data.linelist[i]}' width='40'> - 
                from <strong>${data.stoplist[i]}</strong> to <strong>${data.stoplist[i+1]}</strong>
            `;
        }
        else {
            htmldump += `
                <img src="/../static/line_icons/line${data.linelist[i]}.png" alt='Line ${data.linelist[i]}' width='40'> - 
                from <strong>${data.stoplist[i]}</strong> to <strong>${data.walkingtransferlist[i+1][0]}</strong>
                <br>
            `;
            htmldump += `
                Walk from <strong>${data.walkingtransferlist[i+1][0]}</strong> to <strong>${data.stoplist[i+1]}</strong>.
                This transfer should take about ${data.walkingtransferlist[i+1][1]} minutes.
            `;
        }
    }
    else {
        htmldump += `
            <img src="/../static/line_icons/line${data.linelist[i]}.png" alt='Line ${data.linelist[i]}' width='40'> - 
            from <strong>${data.stoplist[i]}</strong> to <strong>${data.stoplist[i+1]}</strong>
        `;
    }
    document.getElementById("winnerModalBody").innerHTML += `
        <p>
            ${htmldump}
        </p>
        <br>
    `;
    document.getElementById("loserModalBody").innerHTML += `
        <p>
            ${htmldump}
        </p>
        <br>
    `;
}

if (data.gamemode == "daily"){
    console.log(progress);
    for (var i=0; i<progress.length; i++){
        clickLine(progress[i][1]);
        clickLine(progress[i][2]);
        clickLine(progress[i][3]);
        commitEntry();
    }
    document.getElementById("winnerModalFooter").innerHTML = `
    <form action="/viewDailyData" method="post">
    <button class="btn btn-secondary" type="submit">View Stats</button>
    </form>
    `
    document.getElementById("loserModalFooter").innerHTML = `
    <form action="/viewDailyData" method="post">
    <button class="btn btn-secondary" type="submit">View Stats</button>
    </form>
    `
}

// set route length and number of guesses for help box
document.getElementById("modalbody-guesses").innerHTML = `${STARTING_NUMBER_OF_GUESSES}`;
document.getElementById("modalbody-length").innerHTML = `${ROUTELENGTH}`;



function clickLine(line){
    if (guess.length < ROUTELENGTH){
        document.getElementById(`guesscellcontainer_${currentrow}_${currentcolumn}`).innerHTML = `
            <img src="/../static/line_icons/line${line}.png" alt='Line ${line}' width='48'>
        `;
        guess.push(line);
        currentcolumn += 1;
    }
}

function deleteLine(){
    if (guess.length > 0){
        currentcolumn -= 1;
        document.getElementById(`guesscellcontainer_${currentrow}_${currentcolumn}`).innerHTML = `
            <img src="/../static/other_icons/blankicon.png" alt='placeholder' width='48'>
        `;
        guess.pop();
        
    }
}

function verifyEntry(){
    if (guess.length != ROUTELENGTH){
        alert("Incomplete route!")
        return
    }
    var entry = {
        lines: guess
    }
    fetch(`${window.origin}/verifyroute`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(entry),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
    .then(function(response){
        if (response.status !== 200) {
            console.log(`Response was not 200: ${response.status}`);
            return;
        }
        response.json().then(function(data){
            if (data.message === "Invalid") {
                alert("Invalid route");
                return;
            }
            commitEntry();
        })
    })
}

function commitEntry(){
    wincon = 0
    for (var i=0; i<ROUTELENGTH; i++){
        if (guess[i] == ROUTE[i]){
            document.getElementById(`guesscellcontainer_${currentrow}_${i}`).style.backgroundColor = "#40bd40";
            document.getElementById(`linebtn_${guess[i]}`).style.backgroundColor = "#40bd40";
            wincon += 1
            continue;
        }
        isPresent = false;
        isInterlined = false;
        if (ROUTE.includes(guess[i].toString()) == true){
            isPresent = true;
        }
        if (data.interlinedlist[i].includes(guess[i].toString()) == true){
            isInterlined = true;
        }

        console.log(isPresent)
        console.log(isInterlined)

        if (isPresent && isInterlined){
            document.getElementById(`guesscellcontainer_${currentrow}_${i}`).style.backgroundColor = "#f283f7";
            document.getElementById(`guesscellcontainer_${currentrow}_${i}`).style.backgroundImage = "linear-gradient(45deg, #34b4eb 0%, #34b4eb 50%, #f28f37 50%, #f28f37 100%)";
            document.getElementById(`linebtn_${guess[i]}`).style.backgroundColor = "#f28f37";
            continue;
        }
        if (isPresent){
            document.getElementById(`guesscellcontainer_${currentrow}_${i}`).style.backgroundColor = "#f28f37";
            document.getElementById(`linebtn_${guess[i]}`).style.backgroundColor = "#f28f37";
            continue;
        }
        if (isInterlined){
            document.getElementById(`guesscellcontainer_${currentrow}_${i}`).style.backgroundColor = "#34b4eb";
            document.getElementById(`linebtn_${guess[i]}`).style.backgroundColor = "#696969";
            continue;
        }
        document.getElementById(`guesscellcontainer_${currentrow}_${i}`).style.backgroundColor = "#696969";
        document.getElementById(`linebtn_${guess[i]}`).style.backgroundColor = "#696969";
    }

    if (data.gamemode == "daily"){
        writeProgress(guess, currentrow);
    }

    if (wincon == ROUTELENGTH){
        $(document).ready(function(){
            $("#winnerModal").modal('show');
        });
        if (data.gamemode == "daily"){
            writeDatabaseWinOrLoss(1)
        }
        return;
    }

    currentrow += 1;
    currentcolumn = 0;
    guess = []
    if (currentrow === STARTING_NUMBER_OF_GUESSES){
        $(document).ready(function(){
            $("#loserModal").modal('show');
        });
        if (data.gamemode == "daily"){
            writeDatabaseWinOrLoss(0)
        }
    }
}

function writeProgress(guess, currentrow){
    var entry = {
        guess0: guess[0],
        guess1: guess[1],
        guess2: guess[2],
        currentrow: currentrow
    }
    fetch(`${window.origin}/logDailyProgress`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(entry),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
    .then(function(response){
        if (response.status !== 200){
            console.log(`Response was not 200: $(response.status)`);
            return;
        }
        response.json().then(function(data){
            alert("Progress logged to database.")
        })
    })
}

function writeDatabaseWinOrLoss(status){
    var entry = {
        status: status,
        numberOfGuesses: currentrow+1
    }
    fetch(`${window.origin}/logDailyRoute`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(entry),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
    .then(function(response){
        if (response.status !== 200) {
            console.log(`Response was not 200: ${response.status}`);
            return;
        }
        response.json().then(function(data){ // useless code left over from copypaste
            // if (data.message === "Invalid") {
            //     alert("Invalid route");
            //     return;
            // }
            // commitEntry();
            alert("Daily entry logged to database!")
        })
    })
}

function logEverything(){
    console.log(currentrow)
    console.log(currentcolumn)
    console.log(guess)
}

window.addEventListener("keydown", function(event){
    if (event.key === "Backspace"){
        deleteLine();
    }
    if (event.key === "Enter"){
        verifyEntry();
    }
    if (event.key === " "){
        logEverything();
    }
})
