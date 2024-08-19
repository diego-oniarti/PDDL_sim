import { build_tree, get_nodes } from "./classi.js"

let graph, nodes=[];
const sketch = p => {
    const view_box = document.getElementById("graph_view");
    new ResizeObserver(()=>{
        p.resizeCanvas(view_box.clientWidth, view_box.clientHeight-10);
    }).observe(view_box);

    let posX=0;
    let posY=0;

    p.setup = async function() {
        let canvas = p.createCanvas(view_box.offsetWidth, view_box.offsetHeight);
        canvas.parent(view_box)

        await update_graph();
    }

    const center_button = document.getElementById("center_button");
    p.draw = function() {
        const view = document.getElementById("graph_view").getBoundingClientRect();
        p.background(250,250,220);
        if (graph===undefined) return;
        graph.moveto(posX,posY);
        for (let node of nodes) {
            node.elem.style.top = node.rect.y;
            node.elem.style.left = node.rect.x;
            if (node.legend) {
                node.legend.style.top = node.rect.y+node.rect.h;
                node.legend.style.left = node.rect.x+node.rect.w/2+5;
            }

            // Disegna la linea
            const line_bb = node.linea.bounding_box;
            const hovering = p.mouseX>line_bb.x && p.mouseX<line_bb.x+line_bb.w && p.mouseY>line_bb.y && p.mouseY<line_bb.y+line_bb.h;
            if (hovering) {
                p.stroke(255,0,0)
                p.strokeWeight(3)
                node.legend?.classList.add('hovering')
            }else{
                p.stroke(0);
                p.strokeWeight(2)
                node.legend?.classList.remove('hovering')
            }
            for (let seg of node.linea.segments) {
                p.line(seg.a,seg.b, seg.x,seg.y);
            }
        }

        const head = nodes[0];
        const hbox = head.bounding_box;
        if (hbox.x>view.x+view.width || hbox.x+hbox.w<view.x || hbox.y>view.y+view.height || hbox.y+hbox.h<view.x) {
            center_button.style.display = "unset";
            let button_box = center_button.getBoundingClientRect();
            center_button.style.bottom = 20;
            center_button.style.left = view.x+view.width/2 - button_box.width/2;
        }else{
            center_button.style.display = "none";
        }
    }

    let oldX, oldY;
    let prevent_drag = false;
    p.mousePressed = function() {
        const mouse_out_of_canvas = (p.mouseX<0 || p.mouseX>p.width || p.mouseY<0 || p.mouseY>p.height);
        const modal_open = document.getElementById("choice_modal").style.display == "unset";
        if (mouse_out_of_canvas || modal_open) {
            prevent_drag=true;
            return;
        }
        oldX = p.mouseX;
        oldY = p.mouseY;
        document.body.style.userSelect = 'none'; // Prevent text selection
        for (let nodo of nodes) {
            if (nodo.rect.contains(p.mouseX, p.mouseY) || nodo.linea?.bounding_box.contains(p.mouseX, p.mouseY)) {
                prevent_drag=true;
                document.body.style.userSelect = 'unset'; // Prevent text selection
            }
        }
    }
    p.mouseDragged = function() {
        if (prevent_drag) return;
        if (p.mouseX<0 || p.mouseX>p.width || p.mouseY<0 || p.mouseY>p.height) return;
        posX += p.mouseX-oldX;
        posY += p.mouseY-oldY;
        oldX = p.mouseX;
        oldY = p.mouseY;
    }
    p.mouseReleased = function() {
        prevent_drag=false;
        document.body.style.userSelect = 'unset'; // Prevent text selection
    }
    p.mouseWheel = function(e) {
        if (p.mouseX<0 || p.mouseX>p.width || p.mouseY<0 || p.mouseY>p.height) return;
        if (document.getElementById("choice_modal").style.display == "unset") return;
        if (e.delta>0) {
            posY -= 50;
        }else{
            posY += 50;
        }
    }

    p.mouseClicked = function() {
        if (p.mouseX<0 || p.mouseX>p.width || p.mouseY<0 || p.mouseY>p.height) return;
        if (document.getElementById("choice_modal").style.display == "unset") return;
        for (let nodo of nodes) {
            if (nodo.linea?.bounding_box.contains(p.mouseX, p.mouseY)) {
                undo_choice(nodo.id);
                return;
            }
        }
    }

    function undo_choice(id) {
        if (!confirm("Do you wish to undo this choice and all the subsequent ones?")) return;
        fetch(`undo_choice?id=${id}`, {
            method: "POST"
        })
            .then(async ()=>{
                await update_graph();
                // const old_center_x = posX + graph.bounding_box.w/2;
                // posX = old_center_x - graph.bounding_box.w/2;
            });
    }

    center_button.addEventListener("click",()=>{
        posX = 0;
        posY = 0;
    });
    document.addEventListener("choice_made",()=>{
        update_graph();
        // const old_center_x = posX + graph.bounding_box.w/2;
        // posX = old_center_x - graph.bounding_box.w/2;
    });
}

async function update_graph() {
    for (let node of nodes) {
        node.elem.remove();
        node.legend?.remove();
    }
    graph = await build_graph();
    nodes = get_nodes(graph);
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


window.addEventListener("load",()=>{
    new p5(sketch);
});
document.getElementById("choice_modal").addEventListener("click",e=>{
    e.target.style.display="none";
});
document.getElementById("choice_modal_content").addEventListener("click",e=>{
    e.stopPropagation();
});
