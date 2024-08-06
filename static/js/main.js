const sketch = async p => {
    const view_box = document.getElementById("graph_view");
    new ResizeObserver(()=>{
        p.resizeCanvas(view_box.clientWidth, view_box.clientHeight);
    }).observe(view_box);

    let grafo = await get_graph();
    console.log(grafo)

    p.setup = function() {
        let canvas = p.createCanvas(view_box.offsetWidth, view_box.offsetHeight);
        canvas.parent(view_box)
        canvas.id("canvas")
    }

    p.draw = function() {
        p.background(50);
    }
}

function get_graph() {
    return fetch("get_graph")
    .then(res=>res.json())
    .then(data=>{
        return data.nodes;
    });
}


window.addEventListener("load",()=>{
    new p5(sketch);
})
