export function start_choice(id) {
    const modal = document.getElementById("choice_modal");
    const actions_div = document.getElementById("actions");
    modal.style.display = "unset";
    fetch(`/get_aviable?id=${id}`)
    .then(res=>res.json())
    .then(data=>{
        while (actions_div.childElementCount>0) {
            actions_div.removeChild(actions_div.lastChild);
        }
        let i=0;
        for (let action of data.actions) {
            actions_div.appendChild(action_element(action, id, i));
            i++;
        }
    });
}

function action_element(action, id, i) {
    const container = document.createElement("div");

    const title = document.createElement("h3");
    title.innerText = `${action.name}(${action.args.join(' ')})`;
    title.classList.add("pointable");
    title.classList.add("open");
    container.appendChild(title)
    
    const effects = [];
    for (let effect of action.effects) {
        const new_effect = document.createElement("div");
        new_effect.innerHTML = effect.map(f=>`<span>${f}</span>`).join("<br/>");
        if (new_effect.innerHTML.length==0) {
            new_effect.innerHTML="<span>No effect</span>"
        }
        effects.push(new_effect);
    }

    const effects_div = document.createElement("div");
    for (let effect of effects) {
        effects_div.appendChild(effect);
    }
    container.appendChild(effects_div);
    effects_div.classList.add("events_list");

    title.addEventListener("click", ()=>{
        effects_div.classList.toggle("hidden");
        title.classList.toggle("closed");
        title.classList.toggle("open");
    });

    const select_button = document.createElement("button");
    select_button.innerText = `Select Action`;
    select_button.classList.add("select_button");
    container.appendChild(select_button);
    select_button.addEventListener("click",()=>{
        fetch(`/choose?id=${id}&n=${i}`).then(()=>{
            document.getElementById("choice_modal").style.display="none";
            document.dispatchEvent(new CustomEvent('choice_made'));
        });
    });

    container.appendChild(document.createElement("hr"))

    return container;
}
