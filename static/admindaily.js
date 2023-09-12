console.log(data);
if (data == 0){
    console.log("There is no data")
}
var generated_route;

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
        response.json().then(function(arg){
            displayGeneratedRoute(arg);
        })
    })
}

function displayGeneratedRoute(arg){
    generated_route = arg
    console.log(generated_route)
    document.getElementById("routedisplay").innerHTML = "";
    document.getElementById("admin_generateroute").innerHTML = "Regenerate Route";
    for (var i=0; i<generated_route.linelist.length; i++){
        var htmldump = ``
        if (i<generated_route.linelist.length-1){
            if (generated_route.walkingtransferlist[i+1] === null){
                htmldump += `
                    <img src="/../static/line_icons/line${generated_route.linelist[i]}.png" alt='Line ${generated_route.linelist[i]}' width='40'> - 
                    from <strong>${generated_route.stoplist[i]}</strong> to <strong>${generated_route.stoplist[i+1]}</strong>
                `;
            }
            else {
                htmldump += `
                    <img src="/../static/line_icons/line${generated_route.linelist[i]}.png" alt='Line ${generated_route.linelist[i]}' width='40'> - 
                    from <strong>${generated_route.stoplist[i]}</strong> to <strong>${generated_route.walkingtransferlist[i+1][0]}</strong>
                    <br>
                `;
                htmldump += `
                    Walk from <strong>${generated_route.walkingtransferlist[i+1][0]}</strong> to <strong>${generated_route.stoplist[i+1]}</strong>.
                    This transfer should take about ${generated_route.walkingtransferlist[i+1][1]} minutes.
                `;
            }
        }
        else {
            htmldump += `
                <img src="/../static/line_icons/line${generated_route.linelist[i]}.png" alt='Line ${generated_route.linelist[i]}' width='40'> - 
                from <strong>${generated_route.stoplist[i]}</strong> to <strong>${generated_route.stoplist[i+1]}</strong>
            `;
        }
        document.getElementById("routedisplay").innerHTML += `
            <p>
                ${htmldump}
            </p>
            <br>
        `;
    }
}

function addRoute(){
    console.log("generated_route:")
    console.log(generated_route)
    fetch(`${window.origin}/admin-daily`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(generated_route),
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
            alert("HEre!");
        })
    })
}
