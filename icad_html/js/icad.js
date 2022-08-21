
//Function To Display Popup
function div_show_trans(transcription) {
    let fbv = document.getElementById('transcription');
    fbv.value = transcription;
    fbv.ariaPlaceholder = transcription;
    document.getElementById('TransWindow').style.display = "block";
}
//Function to Hide Popup
function div_hide_trans(){
    document.getElementById('TransWindow').style.display = "none";
}
