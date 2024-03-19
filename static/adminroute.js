// district select dropdown
function getStringDropdown(elementName, selectedDistrict){
    districts = [
        "Staré Mesto",
        "Ružinov",
        "Nové Mesto",
        "Karlova Ves",
        "Petržalka",
        "Vrakuňa",
        "Podunajské Biskupice",
        "Rača",
        "Vajnory",
        "Dúbravka",
        "Lamač",
        "Devín",
        "Devínska Nová Ves",
        "Záhorská Bystrica",
        "Jarovce",
        "Rusovce",
        "Čunovo"
    ]
    strdropdown = `
        <select class="form-select" aria-label="${elementName}" id=${elementName}>
    `
    for (var i=0; i<districts.length; i++){
        if (selectedDistrict == districts[i]){
            strdropdown += `
                <option selected value="${districts[i]}">${districts[i]}</option>
            `
        }
        else{
            strdropdown += `
                <option value="${districts[i]}">${districts[i]}</option>
            `
        }
        
    }
    strdropdown += "</select>";
    return strdropdown;
}

// spaghetti code lmao
document.getElementById("thingamabob").innerHTML = `<label for="form_district" class="form-label">District</label>${getStringDropdown("form_district", "Staré Mesto")}`;


// lines fctns

function loadLines(){
    document.getElementById("linecontainer").innerHTML = "";
    for (const [key, value] of Object.entries(lines)){ // loop thru lines
        document.getElementById("linecontainer").innerHTML += `
            <button id='linebtn_${key}' class='linebtn' type='button' data-bs-toggle='collapse' data-bs-target='#line_editbox_${key}' onclick=updateServiceTable("${key}")>
                <img src="/../static/line_icons/line${key}.png" alt='Line ${key}' width='40'>
            </button>
            <span id='line_editbox_${key}' class='collapse'>
                This is where the contents of the collapse will go.
            </span>
        `
    }
}

function updateServiceTable(linelabel){
    var islooping_checkbox_value = "";
    if (lines[linelabel].looping_status == 1){
        islooping_checkbox_value = "checked"
    }
    document.getElementById(`line_editbox_${linelabel}`).innerHTML = `
        <div class="dropdown">
            <button id="admin_editline_${linelabel}" type="button" class="btn btn-primary dropdown-toggle" style="margin-right: 20px" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
                Edit Line ${linelabel}
            </button>
            <div class="dropdown-menu p-4">
                <div class="mb-3">
                    <label for="form_editlinelabel_${linelabel}" class="form-label">Label</label>
                    <input type="text" class="form-control" id="form_editlinelabel_${linelabel}" placeholder="Line Label" value="${linelabel}">
                </div>
                <div class="mb-3">
                    <label for="form_editcolor_${linelabel}" class="form-label">Color (Hexadecimal, No Alpha)</label>
                    <input type="text" class="form-control" id="form_editcolor_${linelabel}" placeholder="#abcdef" value="${lines[linelabel].color}">
                </div>
                <div class="mb-3">
                    <div class="form-check">
                        <input type="checkbox" class="form-check-input" id="dropdownCheck2_edit_${linelabel}" ${islooping_checkbox_value}>
                        <label class="form-check-label" for="dropdownCheck2_edit_${linelabel}">
                            Is Looping
                        </label>
                    </div>
                </div>
                <button type="submit" class="btn btn-success" onclick="updateLine('${linelabel}', document.getElementById('form_editlinelabel_${linelabel}').value, document.getElementById('form_editcolor_${linelabel}').value, document.getElementById('dropdownCheck2_edit_${linelabel}').checked)">Edit</button>
            </div>
        </div>
    `;
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
                            <th scope="col">Add/Reorder/Remove Stop</th>
                        </tr>
                    </thead>
                    <tbody id="line_editbox_${linelabel}_subservice_${key}_tablebody">
                        <tr>
                            <td colspan="5">Empty subservice. Add some stops!.</td>
                        </tr>
                    </tbody>
                </table>
                <div class="dropdown">
                    <input id="admin_insertstop_line_${linelabel}_subservice_${key}_position_-1" type="radio" class="btn-check" name="radiothingy" autocomplete="off">
                    <label class="btn btn-outline-success" for="admin_insertstop_line_${linelabel}_subservice_${key}_position_-1" onclick="select('${linelabel}', ${key}, -1)">
                        Append Stops To Subservice ${key}
                    </label>
                </div>
                <div class="dropdown">
                    <button id="admin_deletesubservice_line_${linelabel}_subservice_${key}" type="button" class="btn btn-danger dropdown-toggle mu-2 mb-4" style="margin-right: 20px" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
                        Delete Subservice ${key}
                    </button>
                    <div class="dropdown-menu p-4">
                        <h6>Are you sure?</h6>
                        <button type="submit" class="btn btn-danger" onclick="deleteSubservice('${linelabel}', ${key})">Delete subservice ${key} of line ${linelabel}</button>
                    </div>
                </div>
            </div>
        ` 
        updateSubserviceTable(linelabel, key);
    }
    document.getElementById(`line_editbox_${linelabel}`).innerHTML += `
        <div class="row">
            <button id="admin_addsubservice_${linelabel}" type="button" class="btn btn-primary mu-4" onclick="addSubservice('${linelabel}')">Add Subservice to Line ${linelabel}</button>
        </div>
        <div class="dropdown">
            <button id="admin_deleteline_${linelabel}" type="button" class="btn btn-danger dropdown-toggle mu-2 mb-4" style="margin-right: 20px" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
                DELETE LINE ${linelabel}
            </button>
            <div class="dropdown-menu p-4">
                <h6>Are you sure?</h6>
                <button type="submit" class="btn btn-danger" onclick="deleteLine('${linelabel}')">DELETE LINE ${linelabel}</button>
            </div>
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
                    <span class="btn-group">
                        <input id="admin_insertstop_line_${linelabel}_subservice_${subservice}_position_${key}" type="radio" class="btn-check" name="radiothingy">
                        <label class="btn btn-outline-success" for="admin_insertstop_line_${linelabel}_subservice_${subservice}_position_${key}"  onclick="select('${linelabel}', ${subservice}, ${key})">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="12" fill="currentColor" class="bi bi-plus" viewBox="0 0 16 16">
                                <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4"/>
                            </svg>
                        </label>
                        <button type="button" class="btn btn-outline-secondary" onclick="swapUp('${linelabel}', ${subservice}, ${key})">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="12" fill="currentColor" class="bi bi-caret-up" viewBox="0 0 16 16">
                                <path d="M3.204 11h9.592L8 5.519zm-.753-.659 4.796-5.48a1 1 0 0 1 1.506 0l4.796 5.48c.566.647.106 1.659-.753 1.659H3.204a1 1 0 0 1-.753-1.659"/>
                            </svg>
                        </button>
                        <button type="button" class="btn btn-outline-secondary" onclick="swapDown('${linelabel}', ${subservice}, ${key})">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="12" fill="currentColor" class="bi bi-caret-down" viewBox="0 0 16 16">
                                <path d="M3.204 5h9.592L8 10.481zm-.753.659 4.796 5.48a1 1 0 0 0 1.506 0l4.796-5.48c.566-.647.106-1.659-.753-1.659H3.204a1 1 0 0 0-.753 1.659"/>
                            </svg>
                        </button>
                        <div class="dropdown">
                            <button id="admin_deletestop_line_${linelabel}_subservice_${subservice}_position_${key}" type="button" class="btn btn-danger dropdown-toggle ml-0 mr-1" style="margin-right: 20px" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="12" fill="currentColor" class="bi bi-x" viewBox="0 0 16 16">
                                    <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708"/>
                                </svg>
                            </button>
                            <div class="dropdown-menu p-4">
                                <h6>Are you sure?</h6>
                                <button type="submit" class="btn btn-danger" onclick="deleteStopFromSubservice('${linelabel}', ${subservice}, ${key})">Delete Stop</button>
                            </div>
                        </div>
                    </span>
                </td>
            </tr>
            `
    }
    if (selectedIndexes.label == linelabel && selectedIndexes.subservice == subservice){
        document.getElementById(`admin_insertstop_line_${linelabel}_subservice_${subservice}_position_${selectedIndexes.order}`).checked = true;
    }
}

// stops fctns

function loadStops(){
    document.getElementById("stopcontainer").innerHTML = `
        <div class="row">
            <table class="table table-striped table-bordered" id="stoptable">
                <thead>
                    <tr>
                        <!-- <th scope="col">-</th> Why??? -->
                        <th scope="col">Stop ID</th>
                        <th scope="col">Stop Name</th>
                        <th scope="col">District</th>
                        <th scope="col"></th>
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
                <span class="btn-group">
                    <button type="button" class="btn btn-success" onclick="addStopToSubservice(${key})">Add</button>
                    <div class="btn-group">
                        <button id="admin_editstop_${key}" type="button" class="btn btn-primary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
                            Edit
                        </button>
                        <div class="dropdown-menu p-4">
                            <div class="mb-3">
                                <label for="form_editstopname_${key}" class="form-label">Stop Name</label>
                                <input type="text" class="form-control" id="form_editstopname_${key}" placeholder="" value="${value.truename}" minlength="2">
                            </div>
                            <div class="mb-3">
                                <label for="form_editdistrict_${key}" class="form-label">District</label>
                                `+getStringDropdown(`form_editdistrict_${key}`, value.district)+`
                            </div>
                            <button type="submit" class="btn btn-primary" onclick="editStop(${key}, document.getElementById('form_editstopname_${key}').value, document.getElementById('form_editdistrict_${key}').value)">Edit</button>
                        </div>
                    </div>
                    <div class="btn-group">
                        <button id="admin_deletestop_${key}" type="button" class="btn btn-danger dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
                            Delete
                        </button>
                        <div class="dropdown-menu p-4">
                            <h6>Are you sure?</h6>
                            <button type="submit" class="btn btn-danger" onclick="deleteStop(${key})">Delete Stop</button>
                        </div>
                    </div>
                </span>
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
                    <th scope="col">Walktime</th>
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
                    <div class="mb-3">
                        <label for="form_walktime" class="form-label">Walktime (minutes, integer)</label>
                        <input type="number" class="form-control" id="form_walktime" placeholder="3">
                    </div>
                    <button type="submit" class="btn btn-primary" onclick="addNearstops(document.getElementById('form_stoponeid').value, document.getElementById('form_stoptwoid').value, document.getElementById('form_walktime').value)">Add Relation</button>
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
                <td scope="col">${value.walktime}</td>
                <td scope="col">
                    <button type="button" class="btn btn-outline-secondary" onclick="removeNearstops(${key})">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x" viewBox="0 0 16 16">
                            <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708"/>
                        </svg>
                    </button>
                </td>
            </tr>
        `;
    }

}