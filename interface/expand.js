function expand(element){
    element.parentElement.classList.toggle("expanded");
    
    //if element is expanded, show return arrow
    // otherwise, show expand arrow
    if(element.parentElement.classList.contains("expanded")){
        element.innerHTML = '<i data-lucide="minimize"></i>';
        scaleFactor = (0.2/250)*0.75;
    }else{
        element.innerHTML = '<i data-lucide="expand"></i>';
        scaleFactor = (0.2/250);
    }

    lucide.createIcons();
}