window.addEventListener("DOMContentLoaded", ()=>{
    let fluents_list = document.getElementById("fluents_list");
    fetch("./get_fluents")
    .then(res=>res.json())
    .then(data=>{
        for (let fluent of data.fluents) {
            let nuovo = document.createElement("p");
            nuovo.innerText = fluent.str;
            fluents_list.appendChild(nuovo);
        }
    })
    .catch(err=>{
        console.log(err)
    })

    let objects_list = document.getElementById("objects_list")
    fetch("./get_objects")
    .then(res=>res.json())
    .then(data=>{
        for (let tipo in data.objects) {
            let nuovo_nome = document.createElement("h3");
            nuovo_nome.innerText = tipo;
            objects_list.appendChild(nuovo_nome);
            let nuovo_ul = document.createElement("ul");
            objects_list.appendChild(nuovo_ul);
            for (let oggetto of data.objects[tipo]) {
                let nuovo_li = document.createElement("li");
                nuovo_li.innerText = oggetto;
                nuovo_ul.appendChild(nuovo_li)
            }
        }
    })
    .catch(err=>{
        console.log(err)
    })
});
