function expand(element){
    element.parentElement.classList.toggle("expanded");
    
    //if element is expanded, show return arrow
    // otherwise, show expand arrow
    if(element.parentElement.classList.contains("expanded")){
        element.innerHTML = "↩";
    }else{
        element.innerHTML = "⤢";
    }
}