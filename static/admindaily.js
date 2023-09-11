console.log(data);
if (data == 0){
    console.log("Null")
}

function generateRoute(){
    fetch(`${window.origin}/generateDailyRoute`, {
        method: "POST",
        credentials: "include",
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
            displayGeneratedRoute(data);
        })
    })
}

function displayGeneratedRoute(data){
    console.log(data)
}