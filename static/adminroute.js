// lines fctns

function loadLines(){
    for (const [key, value] of Object.entries(lines)){ // loop thru lines
        document.getElementById("linecontainer").innerHTML += `
            <button id='linebtn_${key}' class='linebtn' type='button' data-bs-toggle='collapse' data-bs-target='#line_editbox_${key}' onclick=updateServiceTable(${key})>
                <img src="/../static/line_icons/line${key}.png" alt='Line ${key}' width='40'>
            </button>
            <span id='line_editbox_${key}' class='collapse'>
                <p>
                    You're probably not supposed to see this
                </p>
                <p>
                ${JSON.stringify(value)}
                </p>
            </span>
        `
    }
}

function updateServiceTable(linelabel){
    document.getElementById(`line_editbox_${linelabel}`).innerHTML = "";
    for (const [key, value] of Object.entries(lines[linelabel].service)){ // loop thru the subservices of a line
        document.getElementById(`line_editbox_${linelabel}`).innerHTML += `
            <h5 style="text-align: center">Subservice ${key}</h5>
            <div class="row">
                <table class="table table-striped table-bordered" id="line_editbox_${linelabel}_subservice_${key}">
                    <thead>
                        <tr>
                            
                            <th scope="col">Order</th>
                            <th scope="col">Stop ID</th>
                            <th scope="col">Stop Name</th>
                            <th scope="col">District</th>
                            <th scope="col">Add/Edit/Remove</th>
                        </tr>
                    </thead>
                    <tbody id="line_editbox_${linelabel}_subservice_${key}_tablebody">
                        <tr>
                            <td colspan="5">Empty subservice. Add some stops!.</td>
                        </tr>
                    </tbody>
                </table>
                <button id="admin_appendstop_line_${linelabel}_subservice_${key}" type="button" class="btn btn-primary" onclick="TODO">Append Stop To Subservice ${key}</button>
                <button id="admin_deletesubservice_line_${linelabel}_subservice_${key}" type="button" class="btn btn-danger mb-2" onclick="TODO">Delete Subservice ${key}</button>
            </div>
        ` 
        updateSubserviceTable(linelabel, key);
    }
    document.getElementById(`line_editbox_${linelabel}`).innerHTML += `
        <div class="row">
            <button id="admin_addsubservice_${linelabel}" type="button" class="btn btn-primary mu-2 mb-4" onclick="addSubservice(${linelabel})">Add Subservice to ${linelabel}</button>
        </div>
        <div class="row">
            <button id="admin_deleteline_${linelabel}" type="button" class="btn btn-danger mu-2 mb-4" onclick="deleteLine(${linelabel})">DELETE LINE ${linelabel}</button>
        </div>
    `;
}

function updateSubserviceTable(linelabel, subservice){
    document.getElementById(`line_editbox_${linelabel}_subservice_${subservice}_tablebody`).innerHTML = "";
    for (const [key, value] of Object.entries(lines[linelabel].service[subservice])){ // loop thru stops in a subservice
        document.getElementById(`line_editbox_${linelabel}_subservice_${subservice}_tablebody`).innerHTML += `
            <tr id="line_editbox_${linelabel}_subservice_${subservice}_order_${key}_tablerow">
                <td>${key}</td>
                <td>${value}</td>
                <td>${stops[value].truename}</td>
                <td>${stops[value].district}</td>
                <td>
                    <div class="btn-group">
                        <button type="button" class="btn btn-outline-secondary">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="12" fill="currentColor" class="bi bi-plus" viewBox="0 0 16 16">
                                <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4"/>
                            </svg>
                        </button>
                        <button type="button" class="btn btn-outline-secondary">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="12" fill="currentColor" class="bi bi-caret-up" viewBox="0 0 16 16">
                                <path d="M3.204 11h9.592L8 5.519zm-.753-.659 4.796-5.48a1 1 0 0 1 1.506 0l4.796 5.48c.566.647.106 1.659-.753 1.659H3.204a1 1 0 0 1-.753-1.659"/>
                            </svg>
                        </button>
                        <button type="button" class="btn btn-outline-secondary">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="12" fill="currentColor" class="bi bi-caret-down" viewBox="0 0 16 16">
                                <path d="M3.204 5h9.592L8 10.481zm-.753.659 4.796 5.48a1 1 0 0 0 1.506 0l4.796-5.48c.566-.647.106-1.659-.753-1.659H3.204a1 1 0 0 0-.753 1.659"/>
                            </svg>
                        </button>
                        <button type="button" class="btn btn-outline-secondary">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="12" fill="currentColor" class="bi bi-x" viewBox="0 0 16 16">
                                <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708"/>
                            </svg>
                        </button>
                    </div>
                </td>
            </tr>
            `
    }
}

function addLine(label, color, looping_status){
    alert("TODO")
}

function deleteLine(label){
    alert("TODO")
}

function addSubservice(label){
    alert("TODO")
}

function deleteSubservice(label, subservice_id){
    alert("TODO")
}

function appendStopToSubservice(label, subservice_id){
    alert("TODO")
}

function insertStopToSubservice(label, subservice_id, order_in_subservice){
    alert("TODO")
}

function swapUp(label, subservice_id, order_in_subservice){
    alert("TODO")
}

function swapDown(label, subservice_id, order_in_subservice){
    alert("TODO")
}

function deleteStopFromSubservice(label, subservice_id, order_in_subservice){
    alert("TODO")
}

// stops fctns

function loadStops() {

    document.getElementById("stopcontainer").innerHTML = `
        <div class="row">
            <table class="table table-striped table-bordered" id="stoptable">
                <thead>
                    <tr>
                        <!-- <th scope="col">-</th> Why??? -->
                        <th scope="col">Stop ID</th>
                        <th scope="col">Stop Name</th>
                        <th scope="col">District</th>
                        <th scope="col">Edit/Remove</th>
                    </tr>
                </thead>
                <tbody id="stoptablebody">
                </tbody>
            </table>
        </div>
    `;

    const fragment = document.createDocumentFragment(); // Create a document fragment

    for (const [key, value] of Object.entries(stops)) { // loop through stops
        const row = document.createElement('tr'); // Create a table row
        row.innerHTML = `
            <td>${key}</td>
            <td>${value.truename}</td>
            <td>${value.district}</td>
            <td>
                <div class="dropdown">
                    <button id="admin_editstop_${key}" type="button" class="btn btn-primary dropdown-toggle" style="margin-right: 20px" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
                        Edit Stop
                    </button>
                    <div class="dropdown-menu p-4">
                        <div class="mb-3">
                            <label for="form_editstopname" class="form-label">Stop Name</label>
                            <input type="text" class="form-control" id="form_editstopname" placeholder="Pod Stanicou, Zochova, ...">
                        </div>
                        <div class="mb-3">
                            <label for="form_editdistrict" class="form-label">District (exact name!)</label>
                            <input type="text" class="form-control" id="form_editdistrict" placeholder="Staré Mesto, Ružinov, ...">
                        </div>
                        <button type="submit" class="btn btn-primary" onclick="TODO">Edit</button>
                    </div>
                </div>
            </td>
        `;

        fragment.appendChild(row); // Append the row to the fragment
    }

    const tableBody = document.getElementById("stoptablebody");
    tableBody.innerHTML = ''; // Clear the existing content
    tableBody.appendChild(fragment); // Append the fragment to the table body

    new DataTable('#stoptable', {
        pageLength: 5,
        bLengthChange: false,
        deferRender: true
    });
}


// nearstops fctns

function loadNearstops(){
    document.getElementById("nearstopstablecontainer").innerHTML = `
        <table class="table table-striped table-bordered" id="nearstopstable">
            <thead>
                <tr>
                    <th scope="col">NearstopsID</th>
                    <th scope="col">S1 ID</th>
                    <th scope="col">S1 Name</th>
                    <th scope="col">S2 ID</th>
                    <th scope="col">S2 Name</th>
                    <th scope="col">Delete</th>
                </tr>
            </thead>
            <tbody id="nearstopstablebody">
            </tbody>
        </table>
        <div class="row">
            <div class="dropdown">
                <button id="admin_addnearstops" type="button" class="btn btn-primary dropdown-toggle" style="margin-right: 20px" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
                    Add Nearstops
                </button>
                <div class="dropdown-menu p-4">
                    <div class="mb-3">
                        <label for="form_stoponeid" class="form-label">Stop 1 ID</label>
                        <input type="number" class="form-control" id="form_stoponeid" placeholder="123">
                    </div>
                    <div class="mb-3">
                        <label for="form_stoptwoid" class="form-label">Stop 2 ID</label>
                        <input type="number" class="form-control" id="form_stoptwoid" placeholder="456">
                    </div>
                    <button type="submit" class="btn btn-primary" onclick="TODO">Add Relation</button>
                </div>
            </div>
        </div>
    `;
    for (const [key, value] of Object.entries(nearstops)){ // loop thru nearstops
        document.getElementById("nearstopstablebody").innerHTML += `
            <tr>
                <td scope="col">${value.nearstops_id}</td>
                <td scope="col">${value.stopone_id}</td>
                <td scope="col">${stops[value.stopone_id].truename}</td>
                <td scope="col">${value.stoptwo_id}</td>
                <td scope="col">${stops[value.stoptwo_id].truename}</td>
                <td scope="col">
                    <button type="button" class="btn btn-outline-secondary">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x" viewBox="0 0 16 16">
                            <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708"/>
                        </svg>
                    </button>
                </td>
            </tr>
        `;
    }

}