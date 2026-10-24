function expand(element){
    element.parentElement.classList.toggle("expanded");
    
    //if element is expanded, show return arrow
    // otherwise, show expand arrow
    if(element.parentElement.classList.contains("expanded")){
        element.innerHTML = '<i data-lucide="minimize"></i>';
    }else{
        element.innerHTML = '<i data-lucide="expand"></i>';
    }

    lucide.createIcons();
}