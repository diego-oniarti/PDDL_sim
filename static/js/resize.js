window.addEventListener("load", ()=>{
    const horizontal_drag = document.getElementById("horizontal_drag");
    const vertical_drag = document.getElementById("vertical_drag");
    const main_container = document.getElementById("main_container");

    const state_description = document.getElementById("state_description");
    const details = document.getElementById("details")

    let dragging_hor = false;
    let dragging_ver = false;

    horizontal_drag.addEventListener("mousedown", ()=>{dragging_hor = true;});
    vertical_drag.addEventListener("mousedown", ()=>{dragging_ver = true;});
    window.addEventListener("mouseup", ()=>{
        dragging_hor = false;
        dragging_ver = false;
    });

    document.addEventListener("mousemove", e=>{
        if (dragging_hor) {
            const new_w = window.innerWidth - e.x;
            state_description.style.width = `${new_w}px`
        }
        if (dragging_ver) {
            const new_h = window.innerHeight - e.y;
            details.style.height = `${new_h}px`;
        }
    });
});
