//data = JSON.parse(data)
console.log("Initial Data:")
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
    fetch(`${window.origin}/admin-writedailyroute`, {
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
        response.json().then(function(datastring){
            data = datastring
            console.log("Data:");
            console.log(data);
            displayAllDailyRoutes();
        })
    })
}

function removeRoute(){
    console.log("removing route")
    fetch(`${window.origin}/admin-deletedailyroute`, {
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
        response.json().then(function(datastring){
            data = datastring
            console.log("Data:");
            console.log(data);
            displayAllDailyRoutes();
        })
    })
}

function displayAllDailyRoutes(){
    if (data == 0){
        document.getElementById("dailyroute_tablebody").innerHTML = `
        <tr><td colspan="4">
        No daily routes exist. Generate some routes using the "Generate Route" button, 
        and once you like a route, add it using the "add" button.
        </td></tr>
        `
        return;
    }
    document.getElementById("dailyroute_tablebody").innerHTML = ""
    for (var i=0; i<data.length; i++){
        let htmldump = ``;
        htmldump += `
            <tr>
                <th scope="row">${data[i].routedate}</th>
                <td>
        `
        for (var j=0; j<data[i].routejson.linelist.length; j++){
            htmldump += `
                <img src="/../static/line_icons/line${data[i].routejson.linelist[j]}.png" alt='Line ${data[i].routejson.linelist[j]}' width='40'>
            `
        }
        htmldump += `
            </td>
            <td>
        `
        for (var j=0; j<data[i].routejson.stoplist.length; j++){
            htmldump += `
                ${data[i].routejson.stoplist[j]}
            `
            if (j != data[i].routejson.stoplist.length - 1){
                htmldump += `
                    ->
                `
            }
        }
        
        htmldump += `
                </td>
                <td>${data[i].route_id}</td>
            </tr>
        `
        document.getElementById("dailyroute_tablebody").innerHTML += htmldump
    }
}