import { build_tree, get_nodes } from "./classi.js"

const sketch = p => {
    const view_box = document.getElementById("graph_view");
    new ResizeObserver(()=>{
        p.resizeCanvas(view_box.clientWidth, view_box.clientHeight-10);
    }).observe(view_box);

    let graph, nodes;
    let posX=0;
    let posY=0;

    p.setup = async function() {
        let canvas = p.createCanvas(view_box.offsetWidth, view_box.offsetHeight);
        canvas.parent(view_box)

        graph = await build_graph();
        nodes = get_nodes(graph);
    }

    p.draw = function() {
        p.background(250,250,220);
        if (nodes===undefined) return;
        graph.moveto(posX,posY);
        for (let node of nodes) {
            node.elem.style.top = node.rect.y;
            node.elem.style.left = node.rect.x;

            // Disegna la linea
            p.stroke(0);
            for (let seg of node.linea.segments) {
                p.line(seg.a,seg.b, seg.x,seg.y);
            }
        }
    }

    let opened = -1;
    let oldX, oldY;
    let pressed = -1;
    let dragging = false;
    p.mousePressed = function() {
        if (p.mouseX<0 || p.mouseX>p.width || p.mouseY<0 || p.mouseY>p.height) return;

        let on_card = false;
        for (let node of nodes) {
            if (node.rect.contains(p.mouseX, p.mouseY)) {
                pressed = node.id;
                on_card=true;
                break;
            }
        }
        if (!on_card) {
            dragging = true;
            document.body.style.userSelect = 'none'; // Prevent text selection
            oldX = p.mouseX;
            oldY = p.mouseY;
        }
    }

    p.mouseReleased = function() {
        const state_description = document.getElementById("state_description");
        const horizontal_drag = document.getElementById("horizontal_drag");
        if (!(dragging || (p.mouseX<0 || p.mouseX>p.width || p.mouseY<0 || p.mouseY>p.height))) {
            if (opened == pressed) {
                state_description.style.display = "none";
                horizontal_drag.style.display = "none";
                opened = -1;
            }else{
                state_description.style.display = "unset";
                horizontal_drag.style.display = "unset";
                load_description(pressed);
                opened = pressed;
            }
        }
        if (dragging) {
            document.body.style.userSelect = 'unset'; // Prevent text selection
        }
        pressed=false;
        dragging = false;
    }
    p.mouseDragged = function() {
        if (!dragging) return;
        if (p.mouseX<0 || p.mouseX>p.width || p.mouseY<0 || p.mouseY>p.height) return;
        posX += p.mouseX-oldX;
        posY += p.mouseY-oldY;
        oldX = p.mouseX;
        oldY = p.mouseY;
    }

    function load_description(id) {
        fetch(`state_description?id=${id}`)
        .then(res=>res.json())
        .then(data=>{
            let fluents = data.fluents;
            const state_name = document.getElementById("state_name");
            state_name.innerText = `State ${id}`;
            const state_params = document.getElementById("state_params");
            let lines = [];
            for (let name in fluents) {
                for (let a of fluents[name]) {
                    lines.push(`${name}[${a.parameters}] := ${a.value}`);
                }
            }
            state_params.innerHTML = lines.join("<br/>")
        });
    }

    async function get_graph() {
        return await fetch("get_graph")
            .then(res=>res.json())
            .then(data=>{
                return data.nodes;
            });
    }

    async function build_graph() {
        let nodes = await get_graph();
        return build_tree(nodes);
    }
}



window.addEventListener("load",()=>{
    new p5(sketch);
})
