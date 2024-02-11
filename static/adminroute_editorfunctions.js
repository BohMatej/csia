function select(line, subservice, order_in_subservice){
    selectedIndexes.label = line;
    selectedIndexes.subservice = subservice;
    selectedIndexes.order = order_in_subservice;
}

// editor functions

function addLine(label, color, looping_status){
    // check if label does not exist
    if (Object.keys(lines).includes(label)){
        alert(`Line label ${label} already exists`)
        return;
    }
    var ls;
    if (looping_status == true){
        ls = 1;
    }
    else {
        ls = 0;
    }
    lines[label] = {"color": color, "label": label, "looping_status": looping_status, "service": {}}
    console.log(`addLine: ${label} = {color: ${color}, label: ${label}, looping_status: ${looping_status}, service: {}`);
    console.log(lines);
    loadLines();
    alert("Line Added!")
}

function updateLine(oldlabel, newlabel, color, looping_status){
    var ls;
    if (looping_status == true){
        ls = 1;
    }
    else {
        ls = 0;
    }
    lines[newlabel] = {"label": newlabel, "looping_status": looping_status, "color": color, "service": lines[oldlabel].service}
    if (newlabel != oldlabel){
        delete lines[oldlabel]
    }
    console.log(`updateLine: ${oldlabel} -> ${newlabel} {color: ${color}, label: ${newlabel}, looping_status: ${looping_status}, service: {...}`);
    console.log(lines);
    loadLines();
    alert(`Line ${oldlabel} Updated!`)
}

function deleteLine(label){
    delete lines[label];
    console.log(`deleteLine: ${label}`)
    console.log(lines);
    loadLines();
    alert(`Line ${label} Deleted!`)
}

function addSubservice(label){
    if (Object.keys(lines[label].service).length == 0){
        var maxID = 0;
    }
    else{
        var maxID = Math.max(...Object.keys(lines[label].service).map(x => parseInt(x, 10)));
    }
    lines[label].service[maxID+1] = [];
    console.log(`addSubservice: Line ${label} - added empty subservice (index ${maxID+1})`);
    console.log(lines);
    updateServiceTable(label);
    alert(`Subservice added to Line ${label}!`)
}

function deleteSubservice(label, subservice_id){
    subservice_id = parseInt(subservice_id, 10);
  
    // Delete the entry with the given key
    delete lines[label].service[subservice_id];

    // Shift keys of subsequent entries
    for (let key in lines[label].service) {
        let currentKey = parseInt(key, 10);
        if (currentKey > subservice_id) {
            // Decrement the key by 1
            lines[label].service[currentKey - 1] = lines[label].service[key];
            delete lines[label].service[key];
        }
    }
    console.log(`deleteSubservice: Line ${label} - deleted empty subservice (index ${subservice_id})`);
    console.log(lines);
    updateServiceTable(label);
    alert(`Subservice ${subservice_id} Removed from Line ${label}!`)
}

function addStopToSubservice(stop_id){
    //alert(lines[selectedIndexes.label])
    if (selectedIndexes.subservice == -1){
        alert("First select the location where to insert the stop. Choose a line subservice, and click any of the '+' button or the 'Append Stops to Subservice' button.")
    }
    if (selectedIndexes.order == -1){
        lines[selectedIndexes.label].service[selectedIndexes.subservice].push(stop_id);
    }
    else{
        lines[selectedIndexes.label].service[selectedIndexes.subservice].splice(selectedIndexes.order, 0, stop_id);
        selectedIndexes.order += 1;
    }
    console.log(`addStopToSubservice: Line ${selectedIndexes.label} Subservice ${selectedIndexes.subservice} Order ${selectedIndexes.order}: stop with ID ${stop_id}`);
    console.log(lines);
    updateSubserviceTable(selectedIndexes.label, selectedIndexes.subservice)
}

function swapUp(label, subservice_id, order_in_subservice){
    if (order_in_subservice == 0){
        alert("Can't swap up a stop that's already first.");
        return;
    }
    var a = lines[label].service[subservice_id][order_in_subservice];
    var b = lines[label].service[subservice_id][order_in_subservice-1];
    lines[label].service[subservice_id][order_in_subservice] = b;
    lines[label].service[subservice_id][order_in_subservice-1] = a;
    console.log(`swapUp: Line ${label} Subservice ${subservice_id}: Swiched stops at positions ${order_in_subservice} and ${order_in_subservice-1}`);
    console.log(lines);
    updateSubserviceTable(label, subservice_id);
}

function swapDown(label, subservice_id, order_in_subservice){
    if (order_in_subservice == lines[label].service[subservice_id].length-1){
        alert("Can't swap down a stop that's already last.");
        return;
    }
    var a = lines[label].service[subservice_id][order_in_subservice];
    var b = lines[label].service[subservice_id][order_in_subservice+1];
    lines[label].service[subservice_id][order_in_subservice] = b;
    lines[label].service[subservice_id][order_in_subservice+1] = a;
    console.log(`swapUp: Line ${label} Subservice ${subservice_id}: Swiched stops at positions ${order_in_subservice} and ${order_in_subservice-1}`);
    console.log(lines);
    updateSubserviceTable(label, subservice_id);}

function deleteStopFromSubservice(label, subservice_id, order_in_subservice){
    lines[label].service[subservice_id].splice(order_in_subservice, 1);
    console.log(`deleteStopFromSubservice: Line ${label} Subservice ${subservice_id} Order ${order_in_subservice}`);
    console.log(lines);
    updateSubserviceTable(label, subservice_id);
}

function addStop(truename, district){
    var maxID = Math.max(...Object.keys(stops).map(x => parseInt(x, 10)));
    stops[maxID+1] = {"district": district, "truename": truename};
    console.log(`addStop: ${maxID+1} = {district: ${district}, truename: ${truename}}}`);
    console.log(stops);
    loadStops();
    alert(`Stop with ID ${maxID+1} Added!`)
}

function editStop(stop_id, truename, district){
    stops[stop_id] = {"district": district, "truename": truename};
    console.log(`editStop: ${stop_id} = {district: ${district}, truename: ${truename}}}`);
    console.log(stops);
    loadLines()
    loadStops();
    alert(`Stop with ID ${stop_id} Has Been Edited!`)
}

function deleteStop(stop_id){
    var isUsed = false;
    var lineswhereitisused = new Set()
    for (const [linelabel, linedata] of Object.entries(lines)){ // loop thru lines
        for (const [subservice, subservicedata] of Object.entries(lines[linelabel].service)){ // loop thru subservices
            for (const [order_in_subservice, id] of Object.entries(lines[linelabel].service[subservice])){ // loop thru stops
                if (stop_id == id){
                    isUsed = true;
                    lineswhereitisused.add(`Line${linelabel}`)
                }
            }
        }
    }
    for (const [key, value] of Object.entries(nearstops)){ // loop thru nearstops
        if (value.stopone_id == stop_id || value.stoptwo_id == stop_id){
            isUsed = true;
            lineswhereitisused.add(`NearstopsID${value["nearstops_id"]}`)
        }
    }
    if (isUsed == false){
        delete stops[stop_id]
        console.log(`deleteStop: ${stop_id} successful`);
        console.log(stops);
        loadStops();
        alert(`Stop with ID ${stop_id} Has Been Deleted!`)
    }
    else{
        var tmp=""
        for (const value of lineswhereitisused) {
            tmp += `${value} `;
        }
        console.log(`deleteStop: ${stop_id} unsuccessful`);
        alert(`Cannot delete. Stop is still used: ${tmp}`)
    }
}

function addNearstops(stopone_id, stoptwo_id, walktime){

    const s1 = parseInt(stopone_id, 10);
    const s2 = parseInt(stoptwo_id, 10);
    const wt = parseInt(walktime, 10);
    // make sure stopone and stoptwo exist
    console.log(Object.keys(stops))
    if (Object.keys(stops).includes(stopone_id) && Object.keys(stops).includes(stoptwo_id)){
        var maxID = Math.max(...Object.values(nearstops).map(x => parseInt(x.nearstops_id, 10)));
        nearstops.push({"nearstops_id": maxID+1, "stopone_id": s1, "stoptwo_id": s2, "walktime": wt})
        console.log(`addNearstops: ${nearstops.length - 1} = {nearstops_id: ${maxID+1}, stopone_id: ${stopone_id}, stoptwo_id: ${stoptwo_id}, walktime: ${walktime}}`);
        console.log(nearstops);
        loadNearstops();
        alert("Nearstops Added!")
    }
    else{
        alert("Either stopone_id or stoptwo_id don't exist.")
    }
}

function removeNearstops(nearstops_id){
    alert(nearstops_id)
    nearstops.splice(nearstops_id,1)
    console.log(`removeNearstops: ${nearstops[nearstops_id]["nearstops_id"]} successful`);
    console.log(nearstops[nearstops_id]);
    loadNearstops();
    alert(`Nearstops with ID ${nearstops_id} Has Been Deleted!`)
}

// save changes

function saveChanges(){
    alert("DANGER TODO")
}